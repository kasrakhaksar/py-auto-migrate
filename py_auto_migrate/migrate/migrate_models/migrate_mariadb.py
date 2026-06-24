from py_auto_migrate.migrate.migrate_models.base import BaseMigration
from py_auto_migrate.migrate.base_models.base_mariadb import BaseMariaDB
from py_auto_migrate.migrate.insert_models.insert_mariadb import InsertMariaDB

from py_auto_migrate.migrate.insert_models.insert_mysql import InsertMySQL
from py_auto_migrate.migrate.insert_models.insert_mongodb import InsertMongoDB
from py_auto_migrate.migrate.insert_models.insert_sqlite import InsertSQLite
from py_auto_migrate.migrate.insert_models.insert_mssql import InsertMSSQL
from py_auto_migrate.migrate.insert_models.insert_postgressql import InsertPostgresSQL
from py_auto_migrate.migrate.insert_models.insert_oracle import InsertOracle
from py_auto_migrate.migrate.insert_models.insert_redis import InsertRedis
from py_auto_migrate.migrate.insert_models.insert_dynamodb import InsertDynamoDB
from py_auto_migrate.migrate.insert_models.insert_elasticsearch import InsertElasticsearch
from py_auto_migrate.migrate.insert_models.insert_clickhouse import InsertClickHouse



class BaseMariaMigration(BaseMigration, BaseMariaDB):

    def _initialize_source_connection(self):
        BaseMariaDB.__init__(self, self.source_uri)
    
    def read_table(self, table_name: str):
        return BaseMariaDB.read_table(self, table_name)
    
    def get_tables(self):
        return BaseMariaDB.get_tables(self)

    def get_foreignkey_dependencies(self, table_name):
        return BaseMariaDB.get_foreignkey_dependencies(self , table_name)

class MariaToMySQL(BaseMariaMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMySQL)


class MariaToPostgres(BaseMariaMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertPostgresSQL)


class MariaToSQLite(BaseMariaMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertSQLite)


class MariaToMaria(BaseMariaMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMariaDB)


class MariaToMongo(BaseMariaMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMongoDB)


class MariaToMSSQL(BaseMariaMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMSSQL)


class MariaToOracle(BaseMariaMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertOracle)


class MariaToRedis(BaseMariaMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertRedis)


class MariaToDynamoDB(BaseMariaMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertDynamoDB)


class MariaToElastic(BaseMariaMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertElasticsearch)


class MariaToClickHouse(BaseMariaMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertClickHouse)