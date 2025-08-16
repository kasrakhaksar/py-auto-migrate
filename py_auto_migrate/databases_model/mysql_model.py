from pymongo import MongoClient
from mysqlSaver import Connection, Saver, CheckerAndReceiver, Creator
import pandas as pd
from .tools import map_dtype_to_postgres
from .postgresql_model import PostgresConnection

# ========== MySQL → Mongo ==========
class MySQLToMongo:
    def __init__(self, mysql_uri, mongo_uri):
        self.mysql_uri = mysql_uri
        self.mongo_uri = mongo_uri

    def migrate_one(self, table_name):
        host, port, user, password, db_name = self._parse_mysql_uri(self.mysql_uri)
        conn = Connection.connect(host, port, user, password, db_name)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        if not data:
            print(f"❌ Table '{table_name}' in MySQL is empty.")
            return

        df = pd.DataFrame(data, columns=columns)

        client = MongoClient(self.mongo_uri)
        mongo_db_name = self.mongo_uri.split("/")[-1]
        db = client[mongo_db_name]

        if table_name in db.list_collection_names():
            print(f"⚠ Collection '{table_name}' already exists in target MongoDB. Skipping.")
            return

        db[table_name].insert_many(df.to_dict('records'))
        print(f"✅ Migrated {len(df)} rows from MySQL table '{table_name}' to MongoDB collection '{table_name}'")

    def migrate_all(self):
        host, port, user, password, db_name = self._parse_mysql_uri(self.mysql_uri)
        conn = Connection.connect(host, port, user, password, db_name)
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        print(f"📦 Found {len(tables)} tables in MySQL")
        for table in tables:
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)

    def _parse_mysql_uri(self, mysql_uri):
        mysql_uri = mysql_uri.replace("mysql://", "")
        user_pass, host_db = mysql_uri.split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 3306
        return host, port, user, password, db_name
    



# ========== MySQL → MySQL ==========
class MySQLToMySQL:
    def __init__(self, source_uri, target_uri):
        self.source_uri = source_uri
        self.target_uri = target_uri

    def migrate_one(self, table_name):
        src_host, src_port, src_user, src_pass, src_db = self._parse_mysql_uri(self.source_uri)
        src_conn = Connection.connect(src_host, src_port, src_user, src_pass, src_db)
        src_cursor = src_conn.cursor()
        src_cursor.execute(f"SELECT * FROM {table_name}")
        data = src_cursor.fetchall()
        columns = [desc[0] for desc in src_cursor.description]

        if not data:
            print(f"❌ Table '{table_name}' in source MySQL is empty.")
            src_conn.close()
            return

        df = pd.DataFrame(data, columns=columns)
        src_conn.close()

        tgt_host, tgt_port, tgt_user, tgt_pass, tgt_db = self._parse_mysql_uri(self.target_uri)
        temp_conn = Connection.connect(tgt_host, tgt_port, tgt_user, tgt_pass, None)
        creator = Creator(temp_conn)
        creator.database_creator(tgt_db)
        temp_conn.close()

        tgt_conn = Connection.connect(tgt_host, tgt_port, tgt_user, tgt_pass, tgt_db)
        checker = CheckerAndReceiver(tgt_conn)
        if checker.table_exist(table_name):
            print(f"⚠ Table '{table_name}' already exists in target MySQL. Skipping migration.")
            tgt_conn.close()
            return

        saver = Saver(tgt_conn)
        saver.sql_saver(df, table_name)
        tgt_conn.close()
        print(f"✅ Migrated {len(df)} rows from MySQL table '{table_name}' to target MySQL")

    def migrate_all(self):
        src_host, src_port, src_user, src_pass, src_db = self._parse_mysql_uri(self.source_uri)
        src_conn = Connection.connect(src_host, src_port, src_user, src_pass, src_db)
        cursor = src_conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        src_conn.close()

        print(f"📦 Found {len(tables)} tables in source MySQL")
        for table in tables:
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)

    def _parse_mysql_uri(self, mysql_uri):
        mysql_uri = mysql_uri.replace("mysql://", "")
        user_pass, host_db = mysql_uri.split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 3306
        return host, port, user, password, db_name




# ========== MySQL → PostgreSQL ==========
class MySQLToPostgres:
    def __init__(self, mysql_uri, pg_uri):
        self.mysql_uri = mysql_uri
        self.pg_uri = pg_uri

    def migrate_one(self, table_name):
        host, port, user, password, db_name = self._parse_mysql_uri(self.mysql_uri)
        mysql_conn = Connection.connect(host, port, user, password, db_name)
        df = pd.read_sql(f"SELECT * FROM {table_name}", mysql_conn)
        mysql_conn.close()

        pg_conn = self._get_postgres_conn(self.pg_uri)
        cursor = pg_conn.cursor()

        cursor.execute(f"SELECT to_regclass('{table_name}')")
        if cursor.fetchone()[0]:
            print(f"⚠ Table '{table_name}' already exists in PostgreSQL. Skipping.")
            pg_conn.close()
            return

        columns = ', '.join([f'"{col}" {map_dtype_to_postgres(df[col].dtype)}' for col in df.columns])
        cursor.execute(f'CREATE TABLE "{table_name}" ({columns})')

        for _, row in df.iterrows():
            values = tuple(row.astype(str))
            placeholders = ', '.join(['%s'] * len(values))
            cursor.execute(f'INSERT INTO "{table_name}" VALUES ({placeholders})', values)

        pg_conn.commit()
        pg_conn.close()
        print(f"✅ Migrated {len(df)} rows from MySQL to PostgreSQL table '{table_name}'")

    def migrate_all(self):
        host, port, user, password, db_name = self._parse_mysql_uri(self.mysql_uri)
        mysql_conn = Connection.connect(host, port, user, password, db_name)
        cursor = mysql_conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        mysql_conn.close()

        for table in tables:
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)

    def _parse_mysql_uri(self, mysql_uri):
        mysql_uri = mysql_uri.replace("mysql://", "")
        user_pass, host_db = mysql_uri.split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 3306
        return host, port, user, password, db_name

    def _get_postgres_conn(self, pg_uri):
        user_pass, host_db = pg_uri.replace("postgresql://", "").split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 5432
        return PostgresConnection.connect(host, port, user, password, db_name)