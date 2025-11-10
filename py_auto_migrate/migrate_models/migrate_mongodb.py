from ..base_models.base_mongodb import BaseMongoDB
from ..insert_models.insert_mongodb import InsertMongoDB


from ..insert_models.insert_mysql import InsertMySQL
from ..insert_models.insert_sqlite import InsertSQLite
from ..insert_models.insert_mssql import InsertMSSQL
from ..insert_models.insert_postgressql import InsertPostgresSQL
from ..insert_models.insert_mariadb import InsertMariaDB
from ..insert_models.insert_oracle import InsertOracle


# ========= Mongo → MySQL =========
class MongoToMySQL(BaseMongoDB):
    def __init__(self, mongo_uri, mysql_uri):
        super().__init__(mongo_uri)
        self.inserter = InsertMySQL(mysql_uri)

    def migrate_one(self, collection_name):
        df = self.read_collection(collection_name)
        if not df.empty:
            self.inserter.insert(df, collection_name)

    def migrate_all(self):
        for col in self.get_collections():
            print(f"➡ Migrating collection: {col}")
            self.migrate_one(col)


# ========= Mongo → PostgreSQL =========
class MongoToPostgres(BaseMongoDB):
    def __init__(self, mongo_uri, pg_uri):
        super().__init__(mongo_uri)
        self.inserter = InsertPostgresSQL(pg_uri)

    def migrate_one(self, collection_name):
        df = self.read_collection(collection_name)
        if not df.empty:
            self.inserter.insert(df, collection_name)

    def migrate_all(self):
        for col in self.get_collections():
            print(f"➡ Migrating collection: {col}")
            self.migrate_one(col)


# ========= Mongo → SQLite =========
class MongoToSQLite(BaseMongoDB):
    def __init__(self, mongo_uri, sqlite_file):
        super().__init__(mongo_uri)
        self.inserter = InsertSQLite(sqlite_file)

    def migrate_one(self, collection_name):
        df = self.read_collection(collection_name)
        if not df.empty:
            self.inserter.insert(df, collection_name)

    def migrate_all(self):
        for col in self.get_collections():
            print(f"➡ Migrating collection: {col}")
            self.migrate_one(col)


# ========= Mongo → Mongo =========
class MongoToMongo(BaseMongoDB):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri)
        self.inserter = InsertMongoDB(target_uri)

    def migrate_one(self, collection_name):
        df = self.read_collection(collection_name)
        if not df.empty:
            self.inserter.insert(df, collection_name)

    def migrate_all(self):
        for col in self.get_collections():
            print(f"➡ Migrating collection: {col}")
            self.migrate_one(col)



# ========= Mongo → MariaDB =========
class MongoToMaria(BaseMongoDB):
    def __init__(self, mongo_uri, maria_uri):
        super().__init__(mongo_uri)
        self.inserter = InsertMariaDB(maria_uri)

    def migrate_one(self, collection_name):
        df = self.read_collection(collection_name)
        if not df.empty:
            self.inserter.insert(df, collection_name)

    def migrate_all(self):
        for col in self.get_collections():
            print(f"➡ Migrating collection: {col}")
            self.migrate_one(col)



# ========= Mongo → SQL Server =========
class MongoToMSSQL(BaseMongoDB):
    def __init__(self, mongo_uri, mssql_uri):
        super().__init__(mongo_uri)
        self.inserter = InsertMSSQL(mssql_uri)

    def migrate_one(self, collection_name):
        df = self.read_collection(collection_name)
        if not df.empty:
            self.inserter.insert(df, collection_name)

    def migrate_all(self):
        for col in self.get_collections():
            print(f"➡ Migrating collection: {col}")
            self.migrate_one(col)





# ========= Mongo → Oracle =========
class MongoToOracle(BaseMongoDB):
    def __init__(self, mongo_uri, oracle_uri):
        super().__init__(mongo_uri)
        self.inserter = InsertOracle(oracle_uri)

    def migrate_one(self, table_name):
        df = self.read_collection(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_collections():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)