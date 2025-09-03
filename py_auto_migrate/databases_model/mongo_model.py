from pymongo import MongoClient
from mysqlSaver import Connection, Saver, CheckerAndReceiver, Creator
import pandas as pd
import sqlite3
from .tools import map_dtype_to_postgres
from .postgresql_model import PostgresConnection


# ========== Mongo → MySQL ==========
class MongoToMySQL:
    def __init__(self, mongo_uri, mysql_uri):
        self.mongo_uri = mongo_uri
        self.mysql_uri = mysql_uri

    def migrate_one(self, table_name):
        db = self._get_mongo_db(self.mongo_uri)
        data = list(db[table_name].find())
        if not data:
            print(f"❌ Collection '{table_name}' in MongoDB is empty.")
            return

        df = pd.DataFrame(data)
        if "_id" in df.columns:
            df["_id"] = df["_id"].astype(str)

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
        print(f"✅ Migrated {len(df)} rows from MongoDB to MySQL table '{table_name}'")

    def migrate_all(self):
        db = self._get_mongo_db(self.mongo_uri)
        collections = db.list_collection_names()
        print(f"📦 Found {len(collections)} collections in MongoDB")
        for col in collections:
            print(f"➡ Migrating collection: {col}")
            self.migrate_one(col)

    def _get_mongo_db(self, mongo_uri):
        client = MongoClient(mongo_uri)
        db_name = mongo_uri.split("/")[-1]
        return client[db_name]

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





# ========== Mongo → Mongo ==========
class MongoToMongo:
    def __init__(self, source_uri, target_uri):
        self.source_uri = source_uri
        self.target_uri = target_uri

    def migrate_one(self, collection_name):
        src_db = self._get_mongo_db(self.source_uri)
        tgt_db = self._get_mongo_db(self.target_uri)

        data = list(src_db[collection_name].find())
        if not data:
            print(f"❌ Collection '{collection_name}' in source MongoDB is empty.")
            return

        if collection_name in tgt_db.list_collection_names():
            print(f"⚠ Collection '{collection_name}' already exists in target MongoDB. Skipping.")
            return

        tgt_db[collection_name].insert_many(data)
        print(f"✅ Migrated {len(data)} documents from '{collection_name}'")

    def migrate_all(self):
        src_db = self._get_mongo_db(self.source_uri)
        collections = src_db.list_collection_names()
        print(f"📦 Found {len(collections)} collections in source MongoDB")

        for col in collections:
            print(f"➡ Migrating collection: {col}")
            self.migrate_one(col)

    def _get_mongo_db(self, uri):
        client = MongoClient(uri)
        db_name = uri.split("/")[-1]
        return client[db_name]




# ========== Mongo → PostgreSQL ==========
class MongoToPostgres:
    def __init__(self, mongo_uri, pg_uri):
        self.mongo_uri = mongo_uri
        self.pg_uri = pg_uri

    def migrate_one(self, collection_name):
        client = MongoClient(self.mongo_uri)
        db_name = self.mongo_uri.split("/")[-1]
        db = client[db_name]
        data = list(db[collection_name].find())
        if not data:
            print(f"❌ Collection '{collection_name}' is empty.")
            return

        df = pd.DataFrame(data)
        if "_id" in df.columns:
            df["_id"] = df["_id"].astype(str)

        pg_conn = self._get_postgres_conn(self.pg_uri)
        cursor = pg_conn.cursor()

        cursor.execute(f"SELECT to_regclass('{collection_name}')")
        if cursor.fetchone()[0]:
            print(f"⚠ Table '{collection_name}' already exists in PostgreSQL. Skipping.")
            pg_conn.close()
            return

        columns = ', '.join([f'"{col}" {map_dtype_to_postgres(df[col].dtype)}' for col in df.columns])
        cursor.execute(f'CREATE TABLE "{collection_name}" ({columns})')

        for _, row in df.iterrows():
            values = tuple(row.astype(str))
            placeholders = ', '.join(['%s'] * len(values))
            cursor.execute(f'INSERT INTO "{collection_name}" VALUES ({placeholders})', values)

        pg_conn.commit()
        pg_conn.close()
        print(f"✅ Migrated {len(df)} documents from MongoDB to PostgreSQL table '{collection_name}'")

    def migrate_all(self):
        client = MongoClient(self.mongo_uri)
        db_name = self.mongo_uri.split("/")[-1]
        db = client[db_name]
        collections = db.list_collection_names()
        for col in collections:
            print(f"➡ Migrating collection: {col}")
            self.migrate_one(col)

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
    

# ========== Mongo → SQLite ==========
class MongoToSQLite:
    def __init__(self, mongo_uri, sqlite_file):
        self.mongo_uri = mongo_uri
        self.sqlite_file = sqlite_file

    def migrate_one(self, collection_name):
        db = self._get_mongo_db(self.mongo_uri)
        data = list(db[collection_name].find())
        if not data:
            print(f"❌ Collection '{collection_name}' in MongoDB is empty.")
            return

        import pandas as pd
        df = pd.DataFrame(data)
        if "_id" in df.columns:
            df["_id"] = df["_id"].astype(str)

        conn_sqlite = sqlite3.connect(self.sqlite_file)
        cursor = conn_sqlite.cursor()

        columns = []
        dtype_map = {
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
        cursor.execute(f'CREATE TABLE IF NOT EXISTS "{collection_name}" ({columns_str})')
        conn_sqlite.commit()

        placeholders = ", ".join(["?"] * len(df.columns))
        cursor.executemany(f'INSERT INTO "{collection_name}" VALUES ({placeholders})', df.values.tolist())
        conn_sqlite.commit()
        conn_sqlite.close()
        print(f"✅ Migrated {len(df)} rows from MongoDB collection '{collection_name}' to SQLite")

    def migrate_all(self):
        db = self._get_mongo_db(self.mongo_uri)
        collections = db.list_collection_names()
        print(f"📦 Found {len(collections)} collections in MongoDB")
        for col in collections:
            print(f"➡ Migrating collection: {col}")
            self.migrate_one(col)

    def _get_mongo_db(self, mongo_uri):
        client = MongoClient(mongo_uri)
        db_name = mongo_uri.split("/")[-1]
        return client[db_name]