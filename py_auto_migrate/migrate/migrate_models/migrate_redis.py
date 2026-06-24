from py_auto_migrate.migrate.migrate_models.base import BaseMigration
from py_auto_migrate.migrate.base_models.base_redis import BaseRedis
from py_auto_migrate.migrate.insert_models.insert_redis import InsertRedis

from py_auto_migrate.migrate.insert_models.insert_mssql import InsertMSSQL
from py_auto_migrate.migrate.insert_models.insert_mongodb import InsertMongoDB
from py_auto_migrate.migrate.insert_models.insert_sqlite import InsertSQLite
from py_auto_migrate.migrate.insert_models.insert_mysql import InsertMySQL
from py_auto_migrate.migrate.insert_models.insert_mariadb import InsertMariaDB
from py_auto_migrate.migrate.insert_models.insert_oracle import InsertOracle
from py_auto_migrate.migrate.insert_models.insert_postgressql import InsertPostgresSQL
from py_auto_migrate.migrate.insert_models.insert_dynamodb import InsertDynamoDB
from py_auto_migrate.migrate.insert_models.insert_elasticsearch import InsertElasticsearch
from py_auto_migrate.migrate.insert_models.insert_clickhouse import InsertClickHouse


class BaseRedisMigration(BaseMigration, BaseRedis):

    def _initialize_source_connection(self):
        BaseRedis.__init__(self, self.source_uri)
    
    def read_table(self, table_name: str):
        return BaseRedis.read_table(self, table_name)
    
    def get_tables(self):
        return BaseRedis.get_tables(self)


class RedisToPostgres(BaseRedisMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertPostgresSQL)


class RedisToRedis(BaseRedisMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertRedis)


class RedisToMySQL(BaseRedisMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMySQL)


class RedisToMaria(BaseRedisMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMariaDB)


class RedisToSQLite(BaseRedisMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertSQLite)


class RedisToMongo(BaseRedisMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMongoDB)


class RedisToMSSQL(BaseRedisMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMSSQL)


class RedisToOracle(BaseRedisMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertOracle)


class RedisToDynamoDB(BaseRedisMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertDynamoDB)


class RedisToElastic(BaseRedisMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertElasticsearch)


class RedisToClickHouse(BaseRedisMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertClickHouse)