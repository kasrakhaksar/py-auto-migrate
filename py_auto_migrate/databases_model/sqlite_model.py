import sqlite3
import pandas as pd
from pymongo import MongoClient
import pyodbc
import os
from .mysql_model import Connection, Creator, CheckerAndReceiver, Saver


# ========= Base SQLite =========
class BaseSQLite:
    def __init__(self, sqlite_path):
        self.sqlite_path = sqlite_path

    def _connect(self):
        return sqlite3.connect(self.sqlite_path)

    def get_tables(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tables

    def read_table(self, table_name):
        conn = self._connect()
        df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)
        conn.close()
        if df.empty:
            print(f"❌ Table '{table_name}' is empty.")

        df = df.fillna(0)
        return df


# ========= SQLite → MySQL =========
class SQLiteToMySQL(BaseSQLite):
    def __init__(self, sqlite_path, mysql_uri):
        super().__init__(sqlite_path)
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
            print(f"⚠ Table '{table_name}' already exists in MySQL. Skipping migration.")
            conn.close()
            return

        saver = Saver(conn)
        saver.sql_saver(df, table_name)
        conn.close()
        print(f"✅ Migrated {len(df)} rows from SQLite to MySQL table '{table_name}'")

    def migrate_all(self):
        for table in self.get_tables():
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


# ========= SQLite → Mongo =========
class SQLiteToMongo(BaseSQLite):
    def __init__(self, sqlite_path, mongo_uri):
        super().__init__(sqlite_path)
        self.mongo_uri = mongo_uri

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if df.empty:
            return

        client = MongoClient(self.mongo_uri)
        db_name = self.mongo_uri.split("/")[-1]
        db = client[db_name]

        if table_name in db.list_collection_names():
            print(f"⚠ Collection '{table_name}' already exists in MongoDB. Skipping migration.")
            return

        db[table_name].insert_many(df.to_dict("records"))
        print(f"✅ Migrated {len(df)} rows from SQLite to MongoDB collection '{table_name}'")

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)


# ========= SQLite → SQLite =========
class SQLiteToSQLite(BaseSQLite):
    def __init__(self, source_path, target_path):
        super().__init__(source_path)
        self.target_path = target_path

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if df.empty:
            return

        target_conn = sqlite3.connect(self.target_path)
        cursor = target_conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        exist = cursor.fetchone()
        if exist:
            print(f"⚠ Table '{table_name}' already exists in target SQLite. Skipping migration.")
            target_conn.close()
            return

        df.to_sql(table_name, target_conn, index=False)
        target_conn.close()
        print(f"✅ Migrated {len(df)} rows from SQLite to SQLite table '{table_name}'")

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)


# ========= SQLite → PostgreSQL =========
class SQLiteToPostgres(BaseSQLite):
    def __init__(self, sqlite_path, pg_uri):
        super().__init__(sqlite_path)
        self.pg_uri = pg_uri

    def migrate_one(self, table_name):
        import psycopg2
        df = self.read_table(table_name)
        if df.empty:
            return

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
            pg_conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db_name)
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            return

        cursor = pg_conn.cursor()
        cursor.execute(f"SELECT to_regclass('{table_name}')")
        exist = cursor.fetchone()[0]
        if exist:
            print(f"⚠ Table '{table_name}' already exists in PostgreSQL. Skipping migration.")
            pg_conn.close()
            return

        columns = ", ".join([f'"{col}" TEXT' for col in df.columns])
        cursor.execute(f'CREATE TABLE "{table_name}" ({columns})')
        pg_conn.commit()

        for _, row in df.iterrows():
            placeholders = ", ".join(["%s"] * len(row))
            cursor.execute(f'INSERT INTO "{table_name}" VALUES ({placeholders})', tuple(row))
        pg_conn.commit()
        pg_conn.close()
        print(f"✅ Migrated {len(df)} rows from SQLite to PostgreSQL table '{table_name}'")

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)



# ========= SQLite → MariaDB =========
class SQLiteToMaria(BaseSQLite):
    def __init__(self, sqlite_path, maria_uri):
        super().__init__(sqlite_path)
        self.maria_uri = maria_uri

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
            print(f"⚠ Table '{table_name}' already exists in MariaDB. Skipping migration.")
            conn.close()
            return

        saver = Saver(conn)
        saver.sql_saver(df, table_name)
        conn.close()
        print(f"✅ Migrated {len(df)} rows from SQLite to MariaDB table '{table_name}'")

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
            port = 3306
        return host, port, user, password, db_name


# ========= SQLite → SQL Server =========
class SQLiteToSQLServer:
    def __init__(self, sqlite_uri, mssql_uri):
        self.sqlite_file = sqlite_uri.replace("sqlite:///", "")
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

    def _connect_sqlite(self):
        if not os.path.exists(self.sqlite_file):
            raise FileNotFoundError(f"❌ SQLite file not found: {self.sqlite_file}")
        return sqlite3.connect(self.sqlite_file)

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

    def get_tables(self):
        conn = self._connect_sqlite()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        conn.close()
        return tables

    def migrate_one(self, table_name):
        conn_sqlite = self._connect_sqlite()
        df = pd.read_sql(f"SELECT * FROM '{table_name}'", conn_sqlite)
        conn_sqlite.close()

        if df.empty:
            print(f"⚠ Table '{table_name}' is empty.")
            return

        conn_mssql = self._connect_mssql(create_db=True)
        cur = conn_mssql.cursor()

        dtype_map = {
            "int64": "BIGINT",
            "float64": "FLOAT",
            "object": "NVARCHAR(MAX)",
            "bool": "BIT",
            "datetime64[ns]": "DATETIME"
        }

        columns = ", ".join([f"[{col}] {dtype_map.get(str(dtype), 'NVARCHAR(MAX)')}" for col, dtype in df.dtypes.items()])
        cur.execute(f"IF OBJECT_ID('{table_name}', 'U') IS NULL CREATE TABLE [{table_name}] ({columns})")
        conn_mssql.commit()

        placeholders = ", ".join(["?"] * len(df.columns))
        cur.fast_executemany = True
        cur.executemany(f"INSERT INTO [{table_name}] VALUES ({placeholders})", df.values.tolist())
        conn_mssql.commit()
        conn_mssql.close()
        print(f"✅ Migrated {len(df)} rows from SQLite '{table_name}' to SQL Server.")

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)