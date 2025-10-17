import pandas as pd
import sqlite3
import os
import pyodbc
from pymongo import MongoClient
import psycopg2
from mysqlSaver import Connection, Saver, CheckerAndReceiver, Creator
from .tools import map_dtype_to_postgres


# ========= Base Reader =========
class BasePostgres:
    def __init__(self, pg_uri):
        self.pg_uri = pg_uri

    def _connect(self):
        user_pass, host_db = self.pg_uri.replace("postgresql://", "").split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 5432
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=db_name
            )
            return conn
        except Exception as e:
            print(f"❌ PostgreSQL Connection Error: {e}")
            return None

    def get_tables(self):
        conn = self._connect()
        if conn is None:
            return []
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tables

    def read_table(self, table_name):
        conn = self._connect()
        if conn is None:
            return pd.DataFrame()
        df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)
        conn.close()
        if df.empty:
            print(f"❌ Table '{table_name}' is empty.")


        df = df.fillna(0)
        return df


# ========= Postgres → MySQL =========
class PostgresToMySQL(BasePostgres):
    def __init__(self, pg_uri, mysql_uri):
        super().__init__(pg_uri)
        self.mysql_uri = mysql_uri

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if df.empty:
            return

        host, port, user, password, db_name = self._parse_mysql_uri(self.mysql_uri)
        temp_conn = Connection.connect(host, port, user, password, None)
        creator = Creator(temp_conn)
        creator.database_creator(db_name)
        temp_conn.close()

        conn = Connection.connect(host, port, user, password, db_name)
        checker = CheckerAndReceiver(conn)
        if checker.table_exist(table_name):
            print(f"⚠ Table '{table_name}' already exists in MySQL. Skipping.")
            conn.close()
            return

        saver = Saver(conn)
        saver.sql_saver(df, table_name)
        conn.close()
        print(f"✅ Migrated {len(df)} rows from PostgreSQL to MySQL table '{table_name}'")

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating PostgreSQL table: {table}")
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


# ========= Postgres → Mongo =========
class PostgresToMongo(BasePostgres):
    def __init__(self, pg_uri, mongo_uri):
        super().__init__(pg_uri)
        self.mongo_uri = mongo_uri

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if df.empty:
            return

        client = MongoClient(self.mongo_uri)
        db_name = self.mongo_uri.split("/")[-1]
        db = client[db_name]

        if table_name in db.list_collection_names():
            print(f"⚠ Collection '{table_name}' already exists in MongoDB. Skipping.")
            return

        db[table_name].insert_many(df.to_dict("records"))
        print(f"✅ Migrated {len(df)} rows from PostgreSQL to MongoDB collection '{table_name}'")

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating PostgreSQL table: {table}")
            self.migrate_one(table)


# ========= Postgres → PostgreSQL =========
class PostgresToPostgres(BasePostgres):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri)
        self.target_uri = target_uri

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if df.empty:
            return

        target_conn = self._connect_target()
        cursor = target_conn.cursor()
        cursor.execute(f"SELECT to_regclass('{table_name}')")
        if cursor.fetchone()[0]:
            print(f"⚠ Table '{table_name}' already exists in target PostgreSQL. Skipping.")
            target_conn.close()
            return

        columns = ', '.join([f'"{col}" {map_dtype_to_postgres(df[col].dtype)}' for col in df.columns])
        cursor.execute(f'CREATE TABLE "{table_name}" ({columns})')
        for _, row in df.iterrows():
            values = tuple(row.astype(str))
            placeholders = ', '.join(['%s'] * len(values))
            cursor.execute(f'INSERT INTO "{table_name}" VALUES ({placeholders})', values)
        target_conn.commit()
        target_conn.close()
        print(f"✅ Migrated {len(df)} rows from PostgreSQL to PostgreSQL table '{table_name}'")

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating PostgreSQL table: {table}")
            self.migrate_one(table)

    def _connect_target(self):
        user_pass, host_db = self.target_uri.replace("postgresql://", "").split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 5432
        try:
            conn = psycopg2.connect(
                host=host, port=port, user=user, password=password, dbname=db_name
            )
            return conn
        except Exception as e:
            print(f"❌ Target PostgreSQL Connection Error: {e}")
            return None


# ========= Postgres → SQLite =========
class PostgresToSQLite(BasePostgres):
    def __init__(self, pg_uri, sqlite_file):
        super().__init__(pg_uri)
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
        df.to_sql(table_name, conn_sqlite, if_exists="replace", index=False)
        conn_sqlite.close()
        print(f"✅ Migrated {len(df)} rows from PostgreSQL to SQLite table '{table_name}'")

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating PostgreSQL table: {table}")
            self.migrate_one(table)





# ========= Postgres → MariaDB =========
class PostgresToMaria(BasePostgres):
    def __init__(self, pg_uri, maria_uri, mongo_target_uri=None):
        super().__init__(pg_uri)
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
            print(f"➡ Migrating PostgreSQL table: {table}")
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
            port = 3306
        return host, port, user, password, db_name




# ========= Postgres → SQL Server =========
class PostgresToSQLServer:
    def __init__(self, pg_uri, mssql_uri):
        self.pg_uri = pg_uri
        self.mssql_uri = mssql_uri

    def _parse_mssql_uri(self, uri):
        uri = uri.replace("mssql://", "")
        if uri.startswith("@") or "@" not in uri:
            if uri.startswith("@"):
                uri = uri[1:]
            host_port, db_name = uri.split("/", 1)
            if ":" in host_port:
                host, port = host_port.split(":")
            else:
                host, port = host_port, "1433"
            return {"auth": "windows", "host": host, "port": port, "database": db_name}
        else:
            user_pass, host_db = uri.split("@", 1)
            user, password = user_pass.split(":", 1)
            host_port, db_name = host_db.split("/", 1)
            if ":" in host_port:
                host, port = host_port.split(":")
            else:
                host, port = host_port, "1433"
            return {
                "auth": "sql",
                "host": host,
                "port": port,
                "database": db_name,
                "user": user,
                "password": password
            }

    def _connect_postgres(self):
        uri = self.pg_uri.replace("postgresql://", "")
        user_pass, host_db = uri.split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
        else:
            host, port = host_port, 5432
        return psycopg2.connect(dbname=db_name, user=user, password=password, host=host, port=port)

    def _connect_mssql(self, create_db=False):
        cfg = self._parse_mssql_uri(self.mssql_uri)
        if cfg["auth"] == "windows":
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={cfg['host']},{cfg['port']};Trusted_Connection=yes;"
        else:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={cfg['host']},{cfg['port']};UID={cfg['user']};PWD={cfg['password']};"

        if create_db:
            with pyodbc.connect(conn_str, autocommit=True) as tmp:
                cur = tmp.cursor()
                cur.execute(f"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name='{cfg['database']}') CREATE DATABASE [{cfg['database']}]")
                cur.close()

        conn_str += f"DATABASE={cfg['database']};"
        return pyodbc.connect(conn_str)

    def migrate_one(self, table_name):
        pg_conn = self._connect_postgres()
        df = pd.read_sql(f"SELECT * FROM {table_name}", pg_conn)
        pg_conn.close()

        if df.empty:
            print(f"⚠ Table '{table_name}' is empty.")
            return

        conn = self._connect_mssql(create_db=True)
        cur = conn.cursor()

        dtype_map = {
            "int64": "BIGINT",
            "float64": "FLOAT",
            "object": "NVARCHAR(MAX)",
            "bool": "BIT",
            "datetime64[ns]": "DATETIME"
        }

        columns = ", ".join([f"[{col}] {dtype_map.get(str(dtype), 'NVARCHAR(MAX)')}" for col, dtype in df.dtypes.items()])
        cur.execute(f"IF OBJECT_ID('{table_name}', 'U') IS NULL CREATE TABLE [{table_name}] ({columns})")
        conn.commit()

        placeholders = ", ".join(["?"] * len(df.columns))
        cur.fast_executemany = True
        cur.executemany(f"INSERT INTO [{table_name}] VALUES ({placeholders})", df.values.tolist())
        conn.commit()
        conn.close()
        print(f"✅ Migrated {len(df)} rows from PostgreSQL '{table_name}' to SQL Server.")

    def migrate_all(self):
        pg_conn = self._connect_postgres()
        cur = pg_conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = [r[0] for r in cur.fetchall()]
        pg_conn.close()

        for table in tables:
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)