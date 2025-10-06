import pandas as pd
import sqlite3
import os
import psycopg2
from pymongo import MongoClient
from mysqlSaver import Connection, Saver, CheckerAndReceiver, Creator
from .tools import map_dtype_to_postgres


# ========= Base MariaDB =========
class BaseMaria:
    def __init__(self, maria_uri):
        self.maria_uri = maria_uri

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

    def _connect(self):
        try:
            host, port, user, password, db_name = self._parse_maria_uri(self.maria_uri)
            conn = Connection.connect(host, port, user, password, db_name)
            return conn
        except Exception as e:
            print(f"❌ MariaDB Connection Error: {e}")
            return None

    def get_tables(self):
        conn = self._connect()
        if conn is None:
            return []
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables

    def read_table(self, table_name):
        conn = self._connect()
        if conn is None:
            return pd.DataFrame()
        df = pd.read_sql(f"SELECT * FROM `{table_name}`", conn)
        conn.close()
        if df.empty:
            print(f"❌ Table '{table_name}' is empty.")
        df = df.fillna(0)
        return df


# ========= MariaDB → MySQL =========
class MariaToMySQL(BaseMaria):
    def __init__(self, maria_uri, mysql_uri):
        super().__init__(maria_uri)
        self.mysql_uri = mysql_uri

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if df.empty:
            return

        host, port, user, password, db_name = self._parse_maria_uri(self.mysql_uri)
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
        print(f"✅ Migrated {len(df)} rows from MariaDB to MySQL table '{table_name}'")

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating MariaDB table: {table}")
            self.migrate_one(table)


# ========= MariaDB → PostgreSQL =========
class MariaToPostgres(BaseMaria):
    def __init__(self, maria_uri, pg_uri):
        super().__init__(maria_uri)
        self.pg_uri = pg_uri

    def migrate_one(self, table_name):
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
        if cursor.fetchone()[0]:
            print(f"⚠ Table '{table_name}' already exists in PostgreSQL. Skipping migration.")
            pg_conn.close()
            return

        columns = ", ".join([f'"{col}" {map_dtype_to_postgres(df[col].dtype)}' for col in df.columns])
        cursor.execute(f'CREATE TABLE "{table_name}" ({columns})')
        pg_conn.commit()

        for _, row in df.iterrows():
            placeholders = ", ".join(["%s"] * len(row))
            cursor.execute(f'INSERT INTO "{table_name}" VALUES ({placeholders})', tuple(row))
        pg_conn.commit()
        pg_conn.close()
        print(f"✅ Migrated {len(df)} rows from MariaDB to PostgreSQL table '{table_name}'")

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating MariaDB table: {table}")
            self.migrate_one(table)


# ========= MariaDB → Mongo =========
class MariaToMongo(BaseMaria):
    def __init__(self, maria_uri, mongo_uri):
        super().__init__(maria_uri)
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
        print(f"✅ Migrated {len(df)} rows from MariaDB to MongoDB collection '{table_name}'")

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating MariaDB table: {table}")
            self.migrate_one(table)


# ========= MariaDB → SQLite =========
class MariaToSQLite(BaseMaria):
    def __init__(self, maria_uri, sqlite_file):
        super().__init__(maria_uri)
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

        conn = sqlite3.connect(self.sqlite_file)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()
        print(f"✅ Migrated {len(df)} rows from MariaDB to SQLite table '{table_name}'")

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating MariaDB table: {table}")
            self.migrate_one(table)


# ========= MariaDB → MariaDB =========
class MariaToMaria(BaseMaria):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri)
        self.target_uri = target_uri

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if df.empty:
            return

        host, port, user, password, db_name = self._parse_maria_uri(self.target_uri)
        temp_conn = Connection.connect(host, port, user, password, None)
        creator = Creator(temp_conn)
        creator.database_creator(db_name)
        temp_conn.close()

        conn = Connection.connect(host, port, user, password, db_name)
        checker = CheckerAndReceiver(conn)
        if checker.table_exist(table_name):
            print(f"⚠ Table '{table_name}' already exists in target MariaDB. Skipping migration.")
            conn.close()
            return

        saver = Saver(conn)
        saver.sql_saver(df, table_name)
        conn.close()
        print(f"✅ Migrated {len(df)} rows from MariaDB to MariaDB table '{table_name}'")

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating MariaDB table: {table}")
            self.migrate_one(table)
