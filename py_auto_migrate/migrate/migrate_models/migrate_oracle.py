from py_auto_migrate.migrate.migrate_models.base import BaseMigration
from py_auto_migrate.migrate.base_models.base_oracle import BaseOracle
from py_auto_migrate.migrate.insert_models.insert_oracle import InsertOracle

from py_auto_migrate.migrate.insert_models.insert_mysql import InsertMySQL
from py_auto_migrate.migrate.insert_models.insert_mariadb import InsertMariaDB
from py_auto_migrate.migrate.insert_models.insert_postgressql import InsertPostgresSQL
from py_auto_migrate.migrate.insert_models.insert_sqlite import InsertSQLite
from py_auto_migrate.migrate.insert_models.insert_mssql import InsertMSSQL
from py_auto_migrate.migrate.insert_models.insert_mongodb import InsertMongoDB
from py_auto_migrate.migrate.insert_models.insert_redis import InsertRedis
from py_auto_migrate.migrate.insert_models.insert_dynamodb import InsertDynamoDB
from py_auto_migrate.migrate.insert_models.insert_elasticsearch import InsertElasticsearch
from py_auto_migrate.migrate.insert_models.insert_clickhouse import InsertClickHouse



class BaseOracleMigration(BaseMigration, BaseOracle):

    def _initialize_source_connection(self):
        BaseOracle.__init__(self, self.source_uri)
    
    def read_table(self, table_name: str):
        return BaseOracle.read_table(self, table_name)
    
    def get_tables(self):
        return BaseOracle.get_tables(self)

    def get_foreignkey_dependencies(self, table_name):
        return BaseOracle.get_foreignkey_dependencies(self , table_name)


class OracleToMySQL(BaseOracleMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMySQL)


class OracleToMaria(BaseOracleMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMariaDB)


class OracleToPostgres(BaseOracleMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertPostgresSQL)


class OracleToSQLite(BaseOracleMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertSQLite)


class OracleToMSSQL(BaseOracleMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMSSQL)


class OracleToMongo(BaseOracleMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMongoDB)


class OracleToOracle(BaseOracleMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertOracle)


class OracleToRedis(BaseOracleMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertRedis)


class OracleToDynamoDB(BaseOracleMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertDynamoDB)


class OracleToElastic(BaseOracleMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertElasticsearch)


class OracleToClickHouse(BaseOracleMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertClickHouse)