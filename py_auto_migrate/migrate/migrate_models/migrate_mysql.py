from py_auto_migrate.migrate.migrate_models.base import BaseMigration

from py_auto_migrate.migrate.base_models.base_mysql import BaseMySQL
from py_auto_migrate.migrate.insert_models.insert_mysql import InsertMySQL

from py_auto_migrate.migrate.insert_models.insert_mssql import InsertMSSQL
from py_auto_migrate.migrate.insert_models.insert_mongodb import InsertMongoDB
from py_auto_migrate.migrate.insert_models.insert_sqlite import InsertSQLite
from py_auto_migrate.migrate.insert_models.insert_postgressql import InsertPostgresSQL
from py_auto_migrate.migrate.insert_models.insert_mariadb import InsertMariaDB
from py_auto_migrate.migrate.insert_models.insert_oracle import InsertOracle
from py_auto_migrate.migrate.insert_models.insert_redis import InsertRedis
from py_auto_migrate.migrate.insert_models.insert_dynamodb import InsertDynamoDB
from py_auto_migrate.migrate.insert_models.insert_elasticsearch import InsertElasticsearch
from py_auto_migrate.migrate.insert_models.insert_clickhouse import InsertClickHouse



class BaseMySQLMigration(BaseMigration, BaseMySQL):

    def _initialize_source_connection(self):
        BaseMySQL.__init__(self, self.source_uri)
    
    def read_table(self, table_name: str):
        return BaseMySQL.read_table(self, table_name)
    
    def get_tables(self):
        return BaseMySQL.get_tables(self)
    
    def get_foreignkey_dependencies(self, table_name):
        return BaseMySQL.get_foreignkey_dependencies(self , table_name)


class MySQLToPostgres(BaseMySQLMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertPostgresSQL)


class MySQLToMongo(BaseMySQLMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMongoDB)


class MySQLToSQLite(BaseMySQLMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertSQLite)


class MySQLToMySQL(BaseMySQLMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMySQL)


class MySQLToMaria(BaseMySQLMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMariaDB)


class MySQLToMSSQL(BaseMySQLMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMSSQL)


class MySQLToOracle(BaseMySQLMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertOracle)


class MySQLToRedis(BaseMySQLMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertRedis)


class MySQLToDynamoDB(BaseMySQLMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertDynamoDB)


class MySQLToElastic(BaseMySQLMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertElasticsearch)


class MySQLToClickHouse(BaseMySQLMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertClickHouse)