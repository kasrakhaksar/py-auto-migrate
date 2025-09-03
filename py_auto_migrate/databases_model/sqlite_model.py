import sqlite3
import pandas as pd
from pymongo import MongoClient
from .mysql_model import Connection, Creator, CheckerAndReceiver, Saver
from .postgresql_model import PostgresConnection




# =================== SQLite → MySQL ===================
class SQLiteToMySQL:
    def __init__(self, sqlite_path, mysql_uri):
        self.sqlite_path = sqlite_path
        self.mysql_uri = mysql_uri

    def migrate_one(self, table_name):
        conn = sqlite3.connect(self.sqlite_path)
        df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)
        conn.close()

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
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

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


# =================== SQLite → PostgreSQL ===================
class SQLiteToPostgres:
    def __init__(self, sqlite_path, pg_uri):
        self.sqlite_path = sqlite_path
        self.pg_uri = pg_uri

    def migrate_one(self, table_name):
        conn = sqlite3.connect(self.sqlite_path)
        df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)
        conn.close()

        user_pass, host_db = self.pg_uri.replace("postgresql://", "").split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 5432

        pg_conn = PostgresConnection.connect(host, port, user, password, db_name)

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
            cursor.execute(
                f'INSERT INTO "{table_name}" VALUES ({placeholders})', tuple(row)
            )
        pg_conn.commit()
        pg_conn.close()
        print(f"✅ Migrated {len(df)} rows from SQLite to PostgreSQL table '{table_name}'")

    def migrate_all(self):
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        for table in tables:
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)


# =================== SQLite → Mongo ===================
class SQLiteToMongo:
    def __init__(self, sqlite_path, mongo_uri):
        self.sqlite_path = sqlite_path
        self.mongo_uri = mongo_uri

    def migrate_one(self, table_name):
        conn = sqlite3.connect(self.sqlite_path)
        df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)
        conn.close()

        client = MongoClient(self.mongo_uri)
        db_name = self.mongo_uri.split("/")[-1]
        db = client[db_name]

        if table_name in db.list_collection_names():
            print(f"⚠ Collection '{table_name}' already exists in MongoDB. Skipping migration.")
            return

        db[table_name].insert_many(df.to_dict("records"))
        print(f"✅ Migrated {len(df)} rows from SQLite to MongoDB collection '{table_name}'")

    def migrate_all(self):
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        for table in tables:
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)


# =================== SQLite → SQLite ===================
class SQLiteToSQLite:
    def __init__(self, source_path, target_path):
        self.source_path = source_path
        self.target_path = target_path

    def migrate_one(self, table_name):
        source_conn = sqlite3.connect(self.source_path)
        df = pd.read_sql(f'SELECT * FROM "{table_name}"', source_conn)
        source_conn.close()

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
        source_conn = sqlite3.connect(self.source_path)
        cursor = source_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        source_conn.close()

        for table in tables:
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)
