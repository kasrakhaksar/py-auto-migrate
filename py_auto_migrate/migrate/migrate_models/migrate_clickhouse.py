from py_auto_migrate.migrate.migrate_models.base import BaseMigration
from py_auto_migrate.migrate.base_models.base_clickhouse import BaseClickHouse
from py_auto_migrate.migrate.insert_models.insert_clickhouse import InsertClickHouse

from py_auto_migrate.migrate.insert_models.insert_mssql import InsertMSSQL
from py_auto_migrate.migrate.insert_models.insert_mongodb import InsertMongoDB
from py_auto_migrate.migrate.insert_models.insert_postgressql import InsertPostgresSQL
from py_auto_migrate.migrate.insert_models.insert_mysql import InsertMySQL
from py_auto_migrate.migrate.insert_models.insert_mariadb import InsertMariaDB
from py_auto_migrate.migrate.insert_models.insert_oracle import InsertOracle
from py_auto_migrate.migrate.insert_models.insert_redis import InsertRedis
from py_auto_migrate.migrate.insert_models.insert_dynamodb import InsertDynamoDB
from py_auto_migrate.migrate.insert_models.insert_elasticsearch import InsertElasticsearch
from py_auto_migrate.migrate.insert_models.insert_sqlite import InsertSQLite




class BaseClickHouseMigration(BaseMigration, BaseClickHouse):

    def _initialize_source_connection(self):
        BaseClickHouse.__init__(self, self.source_uri)
    
    def read_table(self, table_name: str):
        return BaseClickHouse.read_table(self, table_name)
    
    def get_tables(self):
        return BaseClickHouse.get_tables(self)


class ClickHouseToMySQL(BaseClickHouseMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMySQL)


class ClickHouseToMongo(BaseClickHouseMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMongoDB)


class ClickHouseToPostgres(BaseClickHouseMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertPostgresSQL)


class ClickHouseToSQLite(BaseClickHouseMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertSQLite)


class ClickHouseToMaria(BaseClickHouseMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMariaDB)


class ClickHouseToMSSQL(BaseClickHouseMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMSSQL)


class ClickHouseToOracle(BaseClickHouseMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertOracle)


class ClickHouseToRedis(BaseClickHouseMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertRedis)


class ClickHouseToDynamoDB(BaseClickHouseMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertDynamoDB)


class ClickHouseToElastic(BaseClickHouseMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertElasticsearch)


class ClickHouseToClickHouse(BaseClickHouseMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertClickHouse)