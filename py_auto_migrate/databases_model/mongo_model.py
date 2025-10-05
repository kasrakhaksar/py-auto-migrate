import os
import pandas as pd
import sqlite3
from pymongo import MongoClient
import psycopg2
from mysqlSaver import Connection, Saver, CheckerAndReceiver, Creator
from .tools import map_dtype_to_postgres


# ========= Base Reader =========
class BaseMongo:
    def __init__(self, mongo_uri):
        self.mongo_uri = mongo_uri

    def _connect(self):
        try:
            client = MongoClient(self.mongo_uri)
            db_name = self.mongo_uri.split("/")[-1]
            db = client[db_name]
            return db
        except Exception as e:
            print(f"❌ MongoDB Connection Error: {e}")
            return None

    def get_collections(self):
        db = self._connect()
        if db is None:
            return []
        return db.list_collection_names()

    def read_collection(self, collection_name):
        db = self._connect()
        if db is None:
            return pd.DataFrame()
        data = list(db[collection_name].find())
        if not data:
            print(f"❌ Collection '{collection_name}' is empty.")
            return pd.DataFrame()
        df = pd.DataFrame(data)
        if "_id" in df.columns:
            df["_id"] = df["_id"].astype(str)
        return df


# ========= Mongo → MySQL =========
class MongoToMySQL(BaseMongo):
    def __init__(self, mongo_uri, mysql_uri):
        super().__init__(mongo_uri)
        self.mysql_uri = mysql_uri

    def migrate_one(self, collection_name):
        df = self.read_collection(collection_name)
        if df.empty:
            return

        host, port, user, password, db_name = self._parse_mysql_uri(self.mysql_uri)
        temp_conn = Connection.connect(host, port, user, password, None)
        creator = Creator(temp_conn)
        creator.database_creator(db_name)
        temp_conn.close()

        conn = Connection.connect(host, port, user, password, db_name)
        checker = CheckerAndReceiver(conn)
        if checker.table_exist(collection_name):
            print(f"⚠ Table '{collection_name}' already exists in MySQL. Skipping.")
            conn.close()
            return

        saver = Saver(conn)
        saver.sql_saver(df, collection_name)
        conn.close()
        print(f"✅ Migrated {len(df)} rows from MongoDB to MySQL table '{collection_name}'")

    def migrate_all(self):
        for col in self.get_collections():
            print(f"➡ Migrating collection: {col}")
            self.migrate_one(col)

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


# ========= Mongo → PostgreSQL =========
class MongoToPostgres(BaseMongo):
    def __init__(self, mongo_uri, pg_uri):
        super().__init__(mongo_uri)
        self.pg_uri = pg_uri

    def migrate_one(self, collection_name):
        df = self.read_collection(collection_name)
        if df.empty:
            return

        conn = self._connect_postgres()
        cursor = conn.cursor()
        cursor.execute(f"SELECT to_regclass(%s)", (collection_name,))
        if cursor.fetchone()[0]:
            print(f"⚠ Table '{collection_name}' already exists in PostgreSQL. Skipping.")
            conn.close()
            return

        columns = ', '.join([f'"{col}" {map_dtype_to_postgres(df[col].dtype)}' for col in df.columns])
        cursor.execute(f'CREATE TABLE "{collection_name}" ({columns})')

        for _, row in df.iterrows():
            values = tuple(row.astype(str))
            placeholders = ', '.join(['%s'] * len(values))
            cursor.execute(f'INSERT INTO "{collection_name}" VALUES ({placeholders})', values)

        conn.commit()
        conn.close()
        print(f"✅ Migrated {len(df)} rows from MongoDB to PostgreSQL table '{collection_name}'")

    def migrate_all(self):
        for col in self.get_collections():
            print(f"➡ Migrating collection: {col}")
            self.migrate_one(col)

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


# ========= Mongo → SQLite =========
class MongoToSQLite(BaseMongo):
    def __init__(self, mongo_uri, sqlite_file):
        super().__init__(mongo_uri)
        self.sqlite_file = self._prepare_sqlite_file(sqlite_file)

    def _prepare_sqlite_file(self, file_path):
        if file_path.startswith("sqlite:///"):
            file_path = file_path.replace("sqlite:///", "", 1)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        return file_path

    def migrate_one(self, collection_name):
        df = self.read_collection(collection_name)
        if df.empty:
            return

        conn = sqlite3.connect(self.sqlite_file)
        df.to_sql(collection_name, conn, if_exists="replace", index=False)
        conn.close()
        print(f"✅ Migrated {len(df)} rows from MongoDB to SQLite table '{collection_name}'")

    def migrate_all(self):
        for col in self.get_collections():
            print(f"➡ Migrating collection: {col}")
            self.migrate_one(col)


# ========= Mongo → Mongo =========
class MongoToMongo(BaseMongo):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri)
        self.target_uri = target_uri

    def migrate_one(self, collection_name):
        df = self.read_collection(collection_name)
        if df.empty:
            return

        target_db = MongoClient(self.target_uri)[self.target_uri.split("/")[-1]]
        if collection_name in target_db.list_collection_names():
            print(f"⚠ Collection '{collection_name}' already exists in target MongoDB. Skipping.")
            return

        target_db[collection_name].insert_many(df.to_dict("records"))
        print(f"✅ Migrated {len(df)} rows from MongoDB to MongoDB collection '{collection_name}'")

    def migrate_all(self):
        for col in self.get_collections():
            print(f"➡ Migrating collection: {col}")
            self.migrate_one(col)
