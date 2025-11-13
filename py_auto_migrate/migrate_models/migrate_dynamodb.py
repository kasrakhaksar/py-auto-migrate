from py_auto_migrate.base_models.base_dynamodb import BaseDynamoDB
from py_auto_migrate.insert_models.insert_dynamodb import InsertDynamoDB

from py_auto_migrate.insert_models.insert_mysql import InsertMySQL
from py_auto_migrate.insert_models.insert_mongodb import InsertMongoDB
from py_auto_migrate.insert_models.insert_sqlite import InsertSQLite
from py_auto_migrate.insert_models.insert_mssql import InsertMSSQL
from py_auto_migrate.insert_models.insert_postgressql import InsertPostgresSQL
from py_auto_migrate.insert_models.insert_oracle import InsertOracle
from py_auto_migrate.insert_models.insert_redis import InsertRedis
from py_auto_migrate.insert_models.insert_mariadb import InsertMariaDB


# ========= Dynamo → MongoDB =========
class DynamoToMongo(BaseDynamoDB):
    def __init__(self, dynamo_uri, mongo_uri):
        super().__init__(dynamo_uri)
        self.inserter = InsertMongoDB(mongo_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= Dynamo → MySQL =========
class DynamoToMySQL(BaseDynamoDB):
    def __init__(self, dynamo_uri, mysql_uri):
        super().__init__(dynamo_uri)
        self.inserter = InsertMySQL(mysql_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= Dynamo → PostgreSQL =========
class DynamoToPostgres(BaseDynamoDB):
    def __init__(self, dynamo_uri, pg_uri):
        super().__init__(dynamo_uri)
        self.inserter = InsertPostgresSQL(pg_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= Dynamo → SQLite =========
class DynamoToSQLite(BaseDynamoDB):
    def __init__(self, dynamo_uri, sqlite_path):
        super().__init__(dynamo_uri)
        self.inserter = InsertSQLite(sqlite_path)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= Dynamo → MSSQL =========
class DynamoToMSSQL(BaseDynamoDB):
    def __init__(self, dynamo_uri, mssql_uri):
        super().__init__(dynamo_uri)
        self.inserter = InsertMSSQL(mssql_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= Dynamo → Oracle =========
class DynamoToOracle(BaseDynamoDB):
    def __init__(self, dynamo_uri, oracle_uri):
        super().__init__(dynamo_uri)
        self.inserter = InsertOracle(oracle_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= Dynamo → Redis =========
class DynamoToRedis(BaseDynamoDB):
    def __init__(self, dynamo_uri, redis_uri):
        super().__init__(dynamo_uri)
        self.inserter = InsertRedis(redis_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= Dynamo → MariaDB =========
class DynamoToMaria(BaseDynamoDB):
    def __init__(self, dynamo_uri, maria_uri):
        super().__init__(dynamo_uri)
        self.inserter = InsertMariaDB(maria_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= Dynamo → Dynamo =========
class DynamoToDynamo(BaseDynamoDB):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri)
        self.inserter = InsertDynamoDB(target_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)
