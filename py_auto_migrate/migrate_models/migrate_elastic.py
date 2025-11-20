from py_auto_migrate.base_models.base_elasticsearch import BaseElasticsearch
from py_auto_migrate.insert_models.insert_elasticsearch import InsertElasticsearch


from py_auto_migrate.insert_models.insert_mssql import InsertMSSQL
from py_auto_migrate.insert_models.insert_mongodb import InsertMongoDB
from py_auto_migrate.insert_models.insert_postgressql import InsertPostgresSQL
from py_auto_migrate.insert_models.insert_mysql import InsertMySQL
from py_auto_migrate.insert_models.insert_mariadb import InsertMariaDB
from py_auto_migrate.insert_models.insert_oracle import InsertOracle
from py_auto_migrate.insert_models.insert_redis import InsertRedis
from py_auto_migrate.insert_models.insert_dynamodb import InsertDynamoDB
from py_auto_migrate.insert_models.insert_sqlite import InsertSQLite


# ========= Elasticsearch → MySQL =========
class ElasticToMySQL(BaseElasticsearch):
    def __init__(self, elastic_uri, mysql_uri):
        super().__init__(elastic_uri)
        self.inserter = InsertMySQL(mysql_uri)

    def migrate_one(self, index_name):
        df = self.read_index(index_name)
        if not df.empty:
            self.inserter.insert(df, index_name)

    def migrate_all(self):
        for index in self.get_indices():
            print(f"➡ Migrating index: {index}")
            self.migrate_one(index)


# ========= Elasticsearch → MongoDB =========
class ElasticToMongo(BaseElasticsearch):
    def __init__(self, elastic_uri, mongo_uri):
        super().__init__(elastic_uri)
        self.inserter = InsertMongoDB(mongo_uri)

    def migrate_one(self, index_name):
        df = self.read_index(index_name)
        if not df.empty:
            self.inserter.insert(df, index_name)

    def migrate_all(self):
        for index in self.get_indices():
            print(f"➡ Migrating index: {index}")
            self.migrate_one(index)


# ========= Elasticsearch → SQLite =========
class ElasticToSQLite(BaseElasticsearch):
    def __init__(self, elastic_uri, sqlite_path):
        super().__init__(elastic_uri)
        self.inserter = InsertSQLite(sqlite_path)

    def migrate_one(self, index_name):
        df = self.read_index(index_name)
        if not df.empty:
            self.inserter.insert(df, index_name)

    def migrate_all(self):
        for index in self.get_indices():
            print(f"➡ Migrating index: {index}")
            self.migrate_one(index)


# ========= Elasticsearch → PostgreSQL =========
class ElasticToPostgres(BaseElasticsearch):
    def __init__(self, elastic_uri, pg_uri):
        super().__init__(elastic_uri)
        self.inserter = InsertPostgresSQL(pg_uri)

    def migrate_one(self, index_name):
        df = self.read_index(index_name)
        if not df.empty:
            self.inserter.insert(df, index_name)

    def migrate_all(self):
        for index in self.get_indices():
            print(f"➡ Migrating index: {index}")
            self.migrate_one(index)



# ========= Elasticsearch → MariaDB =========
class ElasticToMaria(BaseElasticsearch):
    def __init__(self, elastic_uri, maria_uri):
        super().__init__(elastic_uri)
        self.inserter = InsertMariaDB(maria_uri)

    def migrate_one(self, index_name):
        df = self.read_index(index_name)
        if not df.empty:
            self.inserter.insert(df, index_name)

    def migrate_all(self):
        for index in self.get_indices():
            print(f"➡ Migrating index: {index}")
            self.migrate_one(index)


# ========= Elasticsearch → SQL Server =========
class ElasticToMSSQL(BaseElasticsearch):
    def __init__(self, elastic_uri, mssql_uri):
        super().__init__(elastic_uri)
        self.inserter = InsertMSSQL(mssql_uri)

    def migrate_one(self, index_name):
        df = self.read_index(index_name)
        if not df.empty:
            self.inserter.insert(df, index_name)

    def migrate_all(self):
        for index in self.get_indices():
            print(f"➡ Migrating index: {index}")
            self.migrate_one(index)


# ========= Elasticsearch → Oracle =========
class ElasticToOracle(BaseElasticsearch):
    def __init__(self, elastic_uri, oracle_uri):
        super().__init__(elastic_uri)
        self.inserter = InsertOracle(oracle_uri)

    def migrate_one(self, index_name):
        df = self.read_index(index_name)
        if not df.empty:
            self.inserter.insert(df, index_name)

    def migrate_all(self):
        for index in self.get_indices():
            print(f"➡ Migrating index: {index}")
            self.migrate_one(index)


# ========= Elasticsearch → Redis =========
class ElasticToRedis(BaseElasticsearch):
    def __init__(self, elastic_uri, redis_uri):
        super().__init__(elastic_uri)
        self.inserter = InsertRedis(redis_uri)

    def migrate_one(self, index_name):
        df = self.read_index(index_name)
        if not df.empty:
            self.inserter.insert(df, index_name)

    def migrate_all(self):
        for index in self.get_indices():
            print(f"➡ Migrating index: {index}")
            self.migrate_one(index)


# ========= Elasticsearch → DynamoDB =========
class ElasticToDynamoDB(BaseElasticsearch):
    def __init__(self, elastic_uri, dynamo_uri):
        super().__init__(elastic_uri)
        self.inserter = InsertDynamoDB(dynamo_uri)

    def migrate_one(self, index_name):
        df = self.read_index(index_name)
        if not df.empty:
            self.inserter.insert(df, index_name)

    def migrate_all(self):
        for index in self.get_indices():
            print(f"➡ Migrating index: {index}")
            self.migrate_one(index)


# ========= Elasticsearch → Elasticsearch =========
class ElasticToElastic(BaseElasticsearch):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri)
        self.inserter = InsertElasticsearch(target_uri)

    def migrate_one(self, index_name):
        df = self.read_index(index_name)
        if not df.empty:
            self.inserter.insert(df, index_name)

    def migrate_all(self):
        for index in self.get_indices():
            print(f"➡ Migrating index: {index}")
            self.migrate_one(index)