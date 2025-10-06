import pandas as pd
import sqlite3
import os
from pymongo import MongoClient
from mysqlSaver import Connection, Saver, CheckerAndReceiver, Creator
import psycopg2
from .tools import map_dtype_to_postgres

# ========= Base MySQL =========
class BaseMySQL:
    def __init__(self, mysql_uri):
        self.mysql_uri = mysql_uri

    def _parse_mysql_uri(self, mysql_uri=None):
        if mysql_uri is None:
            mysql_uri = self.mysql_uri
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

    def _connect(self, db_name=None):
        host, port, user, password, uri_db_name = self._parse_mysql_uri()
        if db_name is None:
            db_name = uri_db_name
        return Connection.connect(host, port, user, password, db_name)

    def get_tables(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables

    def read_table(self, table_name):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM `{table_name}`")
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        df = pd.DataFrame(data, columns=columns)
        if df.empty:
            print(f"❌ Table '{table_name}' is empty.")

        df = df.fillna(0)
        return df


# ========= MySQL → PostgreSQL =========
class MySQLToPostgres(BaseMySQL):
    def __init__(self, mysql_uri, pg_uri):
        super().__init__(mysql_uri)
        self.pg_uri = pg_uri

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if df.empty:
            return

        conn = self._connect_postgres()
        cursor = conn.cursor()

        cursor.execute("SELECT to_regclass(%s)", (table_name,))
        if cursor.fetchone()[0]:
            print(f"⚠ Table '{table_name}' already exists in PostgreSQL. Skipping.")
            conn.close()
            return

        columns = ', '.join([f'"{col}" {map_dtype_to_postgres(df[col].dtype)}' for col in df.columns])
        cursor.execute(f'CREATE TABLE "{table_name}" ({columns})')

        for _, row in df.iterrows():
            values = tuple(row.astype(str))
            placeholders = ', '.join(['%s'] * len(values))
            cursor.execute(f'INSERT INTO "{table_name}" VALUES ({placeholders})', values)

        conn.commit()
        conn.close()
        print(f"✅ Migrated {len(df)} rows from MySQL table '{table_name}' to PostgreSQL table '{table_name}'")

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)

    def _connect_postgres(self):
        uri = self.pg_uri.replace("postgresql://", "")
        user_pass, host_db = uri.split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 5432
        return psycopg2.connect(dbname=db_name, user=user, password=password, host=host, port=port)


# ========= MySQL → MongoDB =========
class MySQLToMongo(BaseMySQL):
    def __init__(self, mysql_uri, mongo_uri):
        super().__init__(mysql_uri)
        self.mongo_uri = mongo_uri

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if df.empty:
            return

        client = MongoClient(self.mongo_uri)
        mongo_db_name = self.mongo_uri.split("/")[-1]
        db = client[mongo_db_name]

        if table_name in db.list_collection_names():
            print(f"⚠ Collection '{table_name}' already exists in MongoDB. Skipping.")
            return

        db[table_name].insert_many(df.to_dict("records"))
        print(f"✅ Migrated {len(df)} rows from MySQL table '{table_name}' to MongoDB collection '{table_name}'")

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)


# ========= MySQL → SQLite =========
class MySQLToSQLite(BaseMySQL):
    def __init__(self, mysql_uri, sqlite_file):
        super().__init__(mysql_uri)
        self.sqlite_file = self._prepare_sqlite_file(sqlite_file)

    def _prepare_sqlite_file(self, file_path):
        if file_path.startswith("sqlite:///"):
            file_path = file_path.replace("sqlite:///", "", 1)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        return file_path

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if df.empty:
            return

        conn_sqlite = sqlite3.connect(self.sqlite_file)
        cursor = conn_sqlite.cursor()

        columns = []
        dtype_map = {
            'int32': 'INTEGER',
            'int64': 'INTEGER',
            'float64': 'REAL',
            'object': 'TEXT',
            'bool': 'BOOLEAN',
            'datetime64[ns]': 'TEXT'
        }
        for col, dtype in df.dtypes.items():
            col_type = dtype_map.get(str(dtype), 'TEXT')
            columns.append(f'"{col}" {col_type}')
        columns_str = ", ".join(columns)
        cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_str})')
        conn_sqlite.commit()

        placeholders = ", ".join(["?"] * len(df.columns))
        cursor.executemany(f'INSERT INTO "{table_name}" VALUES ({placeholders})', df.values.tolist())
        conn_sqlite.commit()
        conn_sqlite.close()
        print(f"✅ Migrated {len(df)} rows from MySQL table '{table_name}' to SQLite table '{table_name}'")

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)


# ========= MySQL → MySQL =========
class MySQLToMySQL(BaseMySQL):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri)
        self.target_uri = target_uri

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if df.empty:
            return

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
        print(f"✅ Migrated {len(df)} rows from source MySQL table '{table_name}' to target MySQL")

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)




# ========= MySQL → MariaDB =========
class MySQLToMaria(BaseMySQL):
    def __init__(self, mysql_uri, maria_uri, mongo_target_uri=None):
        super().__init__(mysql_uri)
        self.maria_uri = maria_uri
        self.mongo_target_uri = mongo_target_uri

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if df.empty:
            return

        host, port, user, password, db_name = self._parse_maria_uri(self.maria_uri)
        temp_conn = Connection.connect(host, port, user, password, None)
        creator = Creator(temp_conn)
        creator.database_creator(db_name)
        temp_conn.close()

        conn = Connection.connect(host, port, user, password, db_name)
        checker = CheckerAndReceiver(conn)
        if checker.table_exist(table_name):
            print(f"⚠ Table '{table_name}' already exists in MariaDB. Skipping Maria save.")
        else:
            saver = Saver(conn)
            saver.sql_saver(df, table_name)
            print(f"✅ Saved {len(df)} rows to MariaDB table '{table_name}'")
        conn.close()

        if self.mongo_target_uri:
            target_client = MongoClient(self.mongo_target_uri)
            target_db_name = self.mongo_target_uri.split("/")[-1]
            target_db = target_client[target_db_name]

            if table_name in target_db.list_collection_names():
                print(f"⚠ Collection '{table_name}' already exists in target MongoDB. Skipping Mongo save.")
            else:
                target_db[table_name].insert_many(df.to_dict("records"))
                print(f"✅ Also saved {len(df)} rows to target MongoDB collection '{table_name}'")

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)

    def _parse_maria_uri(self, maria_uri):
        maria_uri = maria_uri.replace("mariadb://", "").replace("mysql://", "")
        user_pass, host_db = maria_uri.split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 3309
        return host, port, user, password, db_name
