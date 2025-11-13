from py_auto_migrate.base_models.base_sqlite import BaseSQLite
from py_auto_migrate.insert_models.insert_sqlite import InsertSQLite


from py_auto_migrate.insert_models.insert_mssql import InsertMSSQL
from py_auto_migrate.insert_models.insert_mongodb import InsertMongoDB
from py_auto_migrate.insert_models.insert_postgressql import InsertPostgresSQL
from py_auto_migrate.insert_models.insert_mysql import InsertMySQL
from py_auto_migrate.insert_models.insert_mariadb import InsertMariaDB
from py_auto_migrate.insert_models.insert_oracle import InsertOracle
from py_auto_migrate.insert_models.insert_redis import InsertRedis
from py_auto_migrate.insert_models.insert_dynamodb import InsertDynamoDB

# ========= SQLite → MySQL =========
class SQLiteToMySQL(BaseSQLite):
    def __init__(self, sqlite_path, mysql_uri):
        super().__init__(sqlite_path)
        self.inserter = InsertMySQL(mysql_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)


# ========= SQLite → MongoDB =========
class SQLiteToMongo(BaseSQLite):
    def __init__(self, sqlite_path, mongo_uri):
        super().__init__(sqlite_path)
        self.inserter = InsertMongoDB(mongo_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)


# ========= SQLite → SQLite =========
class SQLiteToSQLite(BaseSQLite):
    def __init__(self, source_path, target_path):
        super().__init__(source_path)
        self.inserter = InsertSQLite(target_path)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)


# ========= SQLite → PostgreSQL =========
class SQLiteToPostgres(BaseSQLite):
    def __init__(self, sqlite_path, pg_uri):
        super().__init__(sqlite_path)
        self.inserter = InsertPostgresSQL(pg_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)


# ========= SQLite → MariaDB =========
class SQLiteToMaria(BaseSQLite):
    def __init__(self, sqlite_path, maria_uri, mongo_target_uri=None):
        super().__init__(sqlite_path)
        self.maria_inserter = InsertMariaDB(maria_uri)
        self.mongo_target_inserter = InsertMongoDB(
            mongo_target_uri) if mongo_target_uri else None

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if df.empty:
            return
        self.maria_inserter.insert(df, table_name)
        if self.mongo_target_inserter:
            self.mongo_target_inserter.insert(df, table_name)

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)


# ========= SQLite → SQL Server =========
class SQLiteToMSSQL(BaseSQLite):
    def __init__(self, sqlite_path, mssql_uri):
        super().__init__(sqlite_path)
        self.inserter = InsertMSSQL(mssql_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)



# ========= SQLite → Oracle =========
class SQLiteToOracle(BaseSQLite):
    def __init__(self, sqlite_path, oracle_uri):
        super().__init__(sqlite_path)
        self.inserter = InsertOracle(oracle_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)



# ========= SQLite → Redis =========
class SQLiteToRedis(BaseSQLite):
    def __init__(self, sqlite_path, redis_uri):
        super().__init__(sqlite_path)
        self.inserter = InsertRedis(redis_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)



# ========= SQLite → Dynamo =========
class SQLiteToDynamoDB(BaseSQLite):
    def __init__(self, sqlite_path, dynamo_uri):
        super().__init__(sqlite_path)
        self.inserter = InsertDynamoDB(dynamo_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)