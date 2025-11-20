from py_auto_migrate.base_models.base_oracle import BaseOracle
from py_auto_migrate.insert_models.insert_oracle import InsertOracle


from py_auto_migrate.insert_models.insert_mysql import InsertMySQL
from py_auto_migrate.insert_models.insert_mariadb import InsertMariaDB
from py_auto_migrate.insert_models.insert_postgressql import InsertPostgresSQL
from py_auto_migrate.insert_models.insert_sqlite import InsertSQLite
from py_auto_migrate.insert_models.insert_mssql import InsertMSSQL
from py_auto_migrate.insert_models.insert_mongodb import InsertMongoDB
from py_auto_migrate.insert_models.insert_redis import InsertRedis
from py_auto_migrate.insert_models.insert_dynamodb import InsertDynamoDB
from py_auto_migrate.insert_models.insert_elasticsearch import InsertElasticsearch


# ========= Oracle → MySQL =========
class OracleToMySQL(BaseOracle):
    def __init__(self, oracle_uri, mysql_uri):
        super().__init__(oracle_uri)
        self.inserter = InsertMySQL(mysql_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= Oracle → MAriaDB =========
class OracleToMaria(BaseOracle):
    def __init__(self, oracle_uri, maria_uri):
        super().__init__(oracle_uri)
        self.inserter = InsertMariaDB(maria_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)

# ========= Oracle → Postgres =========
class OracleToPostgres(BaseOracle):
    def __init__(self, oracle_uri, pg_uri):
        super().__init__(oracle_uri)
        self.inserter = InsertPostgresSQL(pg_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)

# ========= Oracle → SQLite =========
class OracleToSQLite(BaseOracle):
    def __init__(self, oracle_uri, sqlite_uri):
        super().__init__(oracle_uri)
        self.inserter = InsertSQLite(sqlite_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)

# ========= Oracle → SQL Server =========
class OracleToMSSQL(BaseOracle):
    def __init__(self, oracle_uri, mssql_uri):
        super().__init__(oracle_uri)
        self.inserter = InsertMSSQL(mssql_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)

# ========= Oracle → MongoDB =========
class OracleToMongo(BaseOracle):
    def __init__(self, oracle_uri, mongo_uri):
        super().__init__(oracle_uri)
        self.inserter = InsertMongoDB(mongo_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)

# ========= Oracle → Oracle =========
class OracleToOracle(BaseOracle):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri)
        self.inserter = InsertOracle(target_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)



# ========= Oracle → Redis =========
class OracleToRedis(BaseOracle):
    def __init__(self, oracle_uri, redis_uri):
        super().__init__(oracle_uri)
        self.inserter = InsertRedis(redis_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)



# ========= Oracle → Dynamo =========
class OracleToDynamoDB(BaseOracle):
    def __init__(self, oracle_uri, dynamo_uri):
        super().__init__(oracle_uri)
        self.inserter = InsertDynamoDB(dynamo_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)



# ========= Oracle → ElasticSearch =========
class OracleToElastic(BaseOracle):
    def __init__(self, oracle_uri, elastic_uri):
        super().__init__(oracle_uri)
        self.inserter = InsertElasticsearch(elastic_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)