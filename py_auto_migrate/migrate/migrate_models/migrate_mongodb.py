from py_auto_migrate.migrate.migrate_models.base import BaseMigration

from py_auto_migrate.migrate.base_models.base_mongodb import BaseMongoDB
from py_auto_migrate.migrate.insert_models.insert_mongodb import InsertMongoDB

from py_auto_migrate.migrate.insert_models.insert_mysql import InsertMySQL
from py_auto_migrate.migrate.insert_models.insert_sqlite import InsertSQLite
from py_auto_migrate.migrate.insert_models.insert_mssql import InsertMSSQL
from py_auto_migrate.migrate.insert_models.insert_postgressql import InsertPostgresSQL
from py_auto_migrate.migrate.insert_models.insert_mariadb import InsertMariaDB
from py_auto_migrate.migrate.insert_models.insert_oracle import InsertOracle
from py_auto_migrate.migrate.insert_models.insert_redis import InsertRedis
from py_auto_migrate.migrate.insert_models.insert_dynamodb import InsertDynamoDB
from py_auto_migrate.migrate.insert_models.insert_elasticsearch import InsertElasticsearch
from py_auto_migrate.migrate.insert_models.insert_clickhouse import InsertClickHouse



class BaseMongoMigration(BaseMigration, BaseMongoDB):

    def _initialize_source_connection(self):
        BaseMongoDB.__init__(self, self.source_uri)
    
    def read_table(self, table_name: str):
        return BaseMongoDB.read_table(self, table_name)
    
    def get_tables(self):
        return BaseMongoDB.get_tables(self)




class MongoToMySQL(BaseMongoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMySQL)


class MongoToPostgres(BaseMongoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertPostgresSQL)


class MongoToSQLite(BaseMongoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertSQLite)


class MongoToMongo(BaseMongoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMongoDB)


class MongoToMaria(BaseMongoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMariaDB)


class MongoToMSSQL(BaseMongoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMSSQL)


class MongoToOracle(BaseMongoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertOracle)


class MongoToRedis(BaseMongoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertRedis)


class MongoToDynamoDB(BaseMongoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertDynamoDB)


class MongoToElastic(BaseMongoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertElasticsearch)


class MongoToClickHouse(BaseMongoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertClickHouse)
