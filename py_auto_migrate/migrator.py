from pymongo import MongoClient
from mysqlSaver import Saver, CheckerAndReceiver, Connection, Creator
import pandas as pd


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

        # اتصال اولیه بدون دیتابیس برای ساخت دیتابیس
        temp_conn = Connection.connect(host, port, user, password, None)
        creator = Creator(temp_conn)
        creator.database_creator(db_name)
        temp_conn.close()

        # اتصال به دیتابیس ساخته شده
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
        source_db = self._get_mongo_db(self.source_uri)
        target_db = self._get_mongo_db(self.target_uri)

        data = list(source_db[collection_name].find())
        if not data:
            print(f"❌ Collection '{collection_name}' in source MongoDB is empty.")
            return

        if collection_name in target_db.list_collection_names():
            print(f"⚠ Collection '{collection_name}' already exists in target MongoDB. Skipping.")
            return

        target_db[collection_name].insert_many(data)
        print(f"✅ Migrated {len(data)} documents from '{collection_name}' to target MongoDB.")

    def migrate_all(self):
        source_db = self._get_mongo_db(self.source_uri)
        collections = source_db.list_collection_names()
        print(f"📦 Found {len(collections)} collections in source MongoDB")
        for col in collections:
            print(f"➡ Migrating collection: {col}")
            self.migrate_one(col)

    def _get_mongo_db(self, mongo_uri):
        client = MongoClient(mongo_uri)
        db_name = mongo_uri.split("/")[-1]
        return client[db_name]




# ========== MySQL → MySQL ==========
class MySQLToMySQL:
    def __init__(self, source_uri, target_uri):
        self.source_uri = source_uri
        self.target_uri = target_uri

    def migrate_one(self, table_name):
        # اتصال به دیتابیس مبدأ
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

        # اتصال به دیتابیس مقصد (قبل از ساخت دیتابیس)
        tgt_host, tgt_port, tgt_user, tgt_pass, tgt_db = self._parse_mysql_uri(self.target_uri)
        temp_conn = Connection.connect(tgt_host, tgt_port, tgt_user, tgt_pass, None)
        creator = Creator(temp_conn)
        creator.database_creator(tgt_db)
        temp_conn.close()

        # اتصال به دیتابیس مقصد
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

# ========== MySQL → Mongo ==========
class MySQLToMongo:
    def __init__(self, mysql_uri, mongo_uri):
        self.mysql_uri = mysql_uri
        self.mongo_uri = mongo_uri

    def migrate_one(self, table_name):
        # اتصال به MySQL
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

        # اتصال به Mongo
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