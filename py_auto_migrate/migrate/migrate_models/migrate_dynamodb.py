from py_auto_migrate.migrate.migrate_models.base import BaseMigration
from py_auto_migrate.migrate.base_models.base_dynamodb import BaseDynamoDB
from py_auto_migrate.migrate.insert_models.insert_dynamodb import InsertDynamoDB

from py_auto_migrate.migrate.insert_models.insert_mysql import InsertMySQL
from py_auto_migrate.migrate.insert_models.insert_mongodb import InsertMongoDB
from py_auto_migrate.migrate.insert_models.insert_sqlite import InsertSQLite
from py_auto_migrate.migrate.insert_models.insert_mssql import InsertMSSQL
from py_auto_migrate.migrate.insert_models.insert_postgressql import InsertPostgresSQL
from py_auto_migrate.migrate.insert_models.insert_oracle import InsertOracle
from py_auto_migrate.migrate.insert_models.insert_redis import InsertRedis
from py_auto_migrate.migrate.insert_models.insert_mariadb import InsertMariaDB
from py_auto_migrate.migrate.insert_models.insert_elasticsearch import InsertElasticsearch
from py_auto_migrate.migrate.insert_models.insert_clickhouse import InsertClickHouse



class BaseDynamoMigration(BaseMigration, BaseDynamoDB):

    def _initialize_source_connection(self):
        BaseDynamoDB.__init__(self, self.source_uri)
    
    def read_table(self, table_name: str):
        return BaseDynamoDB.read_table(self, table_name)
    
    def get_tables(self):
        return BaseDynamoDB.get_tables(self)


class DynamoToMongo(BaseDynamoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMongoDB)


class DynamoToMySQL(BaseDynamoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMySQL)


class DynamoToPostgres(BaseDynamoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertPostgresSQL)


class DynamoToSQLite(BaseDynamoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertSQLite)


class DynamoToMSSQL(BaseDynamoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMSSQL)


class DynamoToOracle(BaseDynamoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertOracle)


class DynamoToRedis(BaseDynamoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertRedis)


class DynamoToMaria(BaseDynamoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertMariaDB)


class DynamoToDynamo(BaseDynamoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertDynamoDB)


class DynamoToElastic(BaseDynamoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertElasticsearch)


class DynamoToClickHouse(BaseDynamoMigration):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri, target_uri, InsertClickHouse)