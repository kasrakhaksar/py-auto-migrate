from py_auto_migrate.migrate.migrate_models.base import BaseMigration
from py_auto_migrate.migrate.base_models.base_postgressql import BasePostgresSQL
from py_auto_migrate.migrate.insert_models.insert_postgressql import InsertPostgresSQL

from py_auto_migrate.migrate.insert_models.insert_mssql import InsertMSSQL
from py_auto_migrate.migrate.insert_models.insert_mongodb import InsertMongoDB
from py_auto_migrate.migrate.insert_models.insert_sqlite import InsertSQLite
from py_auto_migrate.migrate.insert_models.insert_mysql import InsertMySQL
from py_auto_migrate.migrate.insert_models.insert_mariadb import InsertMariaDB
from py_auto_migrate.migrate.insert_models.insert_oracle import InsertOracle
from py_auto_migrate.migrate.insert_models.insert_redis import InsertRedis
from py_auto_migrate.migrate.insert_models.insert_dynamodb import InsertDynamoDB
from py_auto_migrate.migrate.insert_models.insert_elasticsearch import InsertElasticsearch
from py_auto_migrate.migrate.insert_models.insert_clickhouse import InsertClickHouse



    

class BasePostgresMigration(BaseMigration, BasePostgresSQL):

    def _initialize_source_connection(self):
        BasePostgresSQL.__init__(self, self.source_uri)
    
    def read_table(self, table_name: str):
        return BasePostgresSQL.read_table(self, table_name)
    
    def get_tables(self):
        return BasePostgresSQL.get_tables(self)
    
    def get_foreignkey_dependencies(self, table_name):
        return BasePostgresSQL.get_foreignkey_dependencies(self , table_name)




class PostgresToMySQL(BasePostgresMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMySQL)


class PostgresToMongo(BasePostgresMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMongoDB)


class PostgresToSQLite(BasePostgresMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertSQLite)


class PostgresToPostgres(BasePostgresMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertPostgresSQL)


class PostgresToMaria(BasePostgresMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMariaDB)


class PostgresToMSSQL(BasePostgresMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMSSQL)


class PostgresToOracle(BasePostgresMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertOracle)


class PostgresToRedis(BasePostgresMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertRedis)


class PostgresToDynamoDB(BasePostgresMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertDynamoDB)


class PostgresToElastic(BasePostgresMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertElasticsearch)


class PostgresToClickHouse(BasePostgresMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertClickHouse)