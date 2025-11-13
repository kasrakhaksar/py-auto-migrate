from py_auto_migrate.base_models.base_mysql import BaseMySQL
from py_auto_migrate.insert_models.insert_mysql import InsertMySQL


from py_auto_migrate.insert_models.insert_mssql import InsertMSSQL
from py_auto_migrate.insert_models.insert_mongodb import InsertMongoDB
from py_auto_migrate.insert_models.insert_sqlite import InsertSQLite
from py_auto_migrate.insert_models.insert_postgressql import InsertPostgresSQL
from py_auto_migrate.insert_models.insert_mariadb import InsertMariaDB
from py_auto_migrate.insert_models.insert_oracle import InsertOracle
from py_auto_migrate.insert_models.insert_redis import InsertRedis
from py_auto_migrate.insert_models.insert_dynamodb import InsertDynamoDB



# ========= MySQL → PostgreSQL =========
class MySQLToPostgres(BaseMySQL):
    def __init__(self, mysql_uri, pg_uri):
        super().__init__(mysql_uri)
        self.inserter = InsertPostgresSQL(pg_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)


# ========= MySQL → MongoDB =========
class MySQLToMongo(BaseMySQL):
    def __init__(self, mysql_uri, mongo_uri):
        super().__init__(mysql_uri)
        self.inserter = InsertMongoDB(mongo_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)


# ========= MySQL → SQLite =========
class MySQLToSQLite(BaseMySQL):
    def __init__(self, mysql_uri, sqlite_file):
        super().__init__(mysql_uri)
        self.inserter = InsertSQLite(sqlite_file)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)


# ========= MySQL → MySQL =========
class MySQLToMySQL(BaseMySQL):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri)
        self.inserter = InsertMySQL(target_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)


# ========= MySQL → MariaDB =========
class MySQLToMaria(BaseMySQL):
    def __init__(self, mysql_uri, maria_uri, mongo_target_uri=None):
        super().__init__(mysql_uri)
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


# ========= MySQL → SQL Server =========
class MySQLToMSSQL(BaseMySQL):
    def __init__(self, mysql_uri, mssql_uri):
        super().__init__(mysql_uri)
        self.inserter = InsertMSSQL(mssql_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)



# ========= MySQL → Oracle =========
class MySQLToOracle(BaseMySQL):
    def __init__(self, mysql_uri, oracle_uri):
        super().__init__(mysql_uri)
        self.inserter = InsertOracle(oracle_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= MySQL → Redis =========
class MySQLToRedis(BaseMySQL):
    def __init__(self, mysql_uri, redis_uri):
        super().__init__(mysql_uri)
        self.inserter = InsertRedis(redis_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)



# ========= MySQL → Dynamo =========
class MySQLToDynamoDB(BaseMySQL):
    def __init__(self, mysql_uri, dynamo_uri):
        super().__init__(mysql_uri)
        self.inserter = InsertDynamoDB(dynamo_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)