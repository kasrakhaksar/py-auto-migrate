from py_auto_migrate.base_models.base_mariadb import BaseMariaDB
from py_auto_migrate.insert_models.insert_mariadb import InsertMariaDB


from py_auto_migrate.insert_models.insert_mysql import InsertMySQL
from py_auto_migrate.insert_models.insert_mongodb import InsertMongoDB
from py_auto_migrate.insert_models.insert_sqlite import InsertSQLite
from py_auto_migrate.insert_models.insert_mssql import InsertMSSQL
from py_auto_migrate.insert_models.insert_postgressql import InsertPostgresSQL
from py_auto_migrate.insert_models.insert_oracle import InsertOracle
from py_auto_migrate.insert_models.insert_redis import InsertRedis
from py_auto_migrate.insert_models.insert_dynamodb import InsertDynamoDB



# ========= MariaDB → MySQL =========
class MariaToMySQL(BaseMariaDB):
    def __init__(self, maria_uri, mysql_uri):
        super().__init__(maria_uri)
        self.inserter = InsertMySQL(mysql_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= MariaDB → PostgreSQL =========
class MariaToPostgres(BaseMariaDB):
    def __init__(self, maria_uri, pg_uri):
        super().__init__(maria_uri)
        self.inserter = InsertPostgresSQL(pg_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= MariaDB → SQLite =========
class MariaToSQLite(BaseMariaDB):
    def __init__(self, maria_uri, sqlite_uri):
        super().__init__(maria_uri)
        self.inserter = InsertSQLite(sqlite_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= MariaDB → MariaDB =========
class MariaToMaria(BaseMariaDB):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri)
        self.inserter = InsertMariaDB(target_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= MariaDB → Mongo =========
class MariaToMongo(BaseMariaDB):
    def __init__(self, maria_uri, mongo_uri):
        super().__init__(maria_uri)
        self.inserter = InsertMongoDB(mongo_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= MariaDB → SQL Server =========
class MariaToMSSQL(BaseMariaDB):
    def __init__(self, maria_uri, mssql_uri):
        super().__init__(maria_uri)
        self.inserter = InsertMSSQL(mssql_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)



# ========= MariaDB → Oracle =========
class MariaToOracle(BaseMariaDB):
    def __init__(self, maria_uri, oracle_uri):
        super().__init__(maria_uri)
        self.inserter = InsertOracle(oracle_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)



# ========= MariaDB → Redis =========
class MariaToRedis(BaseMariaDB):
    def __init__(self, maria_uri, redis_uri):
        super().__init__(maria_uri)
        self.inserter = InsertRedis(redis_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)



# ========= MariaDB → Dynamo =========
class MariaToDynamoDB(BaseMariaDB):
    def __init__(self, maria_uri, dynamo_uri):
        super().__init__(maria_uri)
        self.inserter = InsertDynamoDB(dynamo_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)