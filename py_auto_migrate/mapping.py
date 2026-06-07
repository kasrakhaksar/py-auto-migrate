from py_auto_migrate.migrate_models.migrate_mongodb import *
from py_auto_migrate.migrate_models.migrate_mysql import *
from py_auto_migrate.migrate_models.migrate_postgresql import *
from py_auto_migrate.migrate_models.migrate_sqlite import *
from py_auto_migrate.migrate_models.migrate_mariadb import *
from py_auto_migrate.migrate_models.migrate_mssql import *
from py_auto_migrate.migrate_models.migrate_oracle import *
from py_auto_migrate.migrate_models.migrate_redis import *
from py_auto_migrate.migrate_models.migrate_dynamodb import *
from py_auto_migrate.migrate_models.migrate_elastic import *
from py_auto_migrate.migrate_models.migrate_clickhouse import *


ALL_DATABASES_LIST = ["mongodb://", "mysql://", "mariadb://", "postgresql://",
                   "mssql://", "oracle://", "elasticsearch://",
                   "redis://", "dynamodb://", "sqlite://", "clickhouse://"]


AI_SUPPORTED_DATABASES = ['postgresql://', 'mysql://', 'mariadb://', 'sqlite://', 'oracle://' , 'mssql://']


MIGRATION_MAP = {
    # MongoDB
    ("mongodb://", "mysql://"): MongoToMySQL,
    ("mongodb://", "mariadb://"): MongoToMaria,
    ("mongodb://", "mongodb://"): MongoToMongo,
    ("mongodb://", "postgresql://"): MongoToPostgres,
    ("mongodb://", "sqlite://"): MongoToSQLite,
    ("mongodb://", "mssql://"): MongoToMSSQL,
    ("mongodb://", "oracle://"): MongoToOracle,
    ("mongodb://", "redis://"): MongoToRedis,
    ("mongodb://", "dynamodb://"): MongoToDynamoDB,
    ("mongodb://", "elasticsearch://"): MongoToElastic,
    ("mongodb://", "clickhouse://"): MongoToClickHouse,

    # MySQL
    ("mysql://", "mysql://"): MySQLToMySQL,
    ("mysql://", "mariadb://"): MySQLToMaria,
    ("mysql://", "mongodb://"): MySQLToMongo,
    ("mysql://", "postgresql://"): MySQLToPostgres,
    ("mysql://", "sqlite://"): MySQLToSQLite,
    ("mysql://", "mssql://"): MySQLToMSSQL,
    ("mysql://", "oracle://"): MySQLToOracle,
    ("mysql://", "redis://"): MySQLToRedis,
    ("mysql://", "dynamodb://"): MySQLToDynamoDB,
    ("mysql://", "elasticsearch://"): MySQLToElastic,
    ("mysql://", "clickhouse://"): MySQLToClickHouse,

    # MariaDB
    ("mariadb://", "mysql://"): MariaToMySQL,
    ("mariadb://", "mariadb://"): MariaToMaria,
    ("mariadb://", "mongodb://"): MariaToMongo,
    ("mariadb://", "postgresql://"): MariaToPostgres,
    ("mariadb://", "sqlite://"): MariaToSQLite,
    ("mariadb://", "mssql://"): MariaToMSSQL,
    ("mariadb://", "oracle://"): MariaToOracle,
    ("mariadb://", "redis://"): MariaToRedis,
    ("mariadb://", "dynamodb://"): MariaToDynamoDB,
    ("mariadb://", "elasticsearch://"): MariaToElastic,
    ("mariadb://", "clickhouse://"): MariaToClickHouse,

    # PostgreSQL
    ("postgresql://", "mysql://"): PostgresToMySQL,
    ("postgresql://", "mariadb://"): PostgresToMaria,
    ("postgresql://", "mongodb://"): PostgresToMongo,
    ("postgresql://", "postgresql://"): PostgresToPostgres,
    ("postgresql://", "sqlite://"): PostgresToSQLite,
    ("postgresql://", "mssql://"): PostgresToMSSQL,
    ("postgresql://", "oracle://"): PostgresToOracle,
    ("postgresql://", "redis://"): PostgresToRedis,
    ("postgresql://", "dynamodb://"): PostgresToDynamoDB,
    ("postgresql://", "elasticsearch://"): PostgresToElastic,
    ("postgresql://", "clickhouse://"): PostgresToClickHouse,

    # MSSQL
    ("mssql://", "mysql://"): MSSQLToMySQL,
    ("mssql://", "mariadb://"): MSSQLToMaria,
    ("mssql://", "mongodb://"): MSSQLToMongo,
    ("mssql://", "postgresql://"): MSSQLToPostgres,
    ("mssql://", "sqlite://"): MSSQLToSQLite,
    ("mssql://", "oracle://"): MSSQLToOracle,
    ("mssql://", "mssql://"): MSSQLToMSSQL,
    ("mssql://", "redis://"): MSSQLToRedis,
    ("mssql://", "dynamodb://"): MSSQLToDynamoDB,
    ("mssql://", "elasticsearch://"): MSSQLToElastic,
    ("mssql://", "clickhouse://"): MSSQLToClickHouse,

    # Oracle
    ("oracle://", "mysql://"): OracleToMySQL,
    ("oracle://", "mariadb://"): OracleToMaria,
    ("oracle://", "mongodb://"): OracleToMongo,
    ("oracle://", "postgresql://"): OracleToPostgres,
    ("oracle://", "sqlite://"): OracleToSQLite,
    ("oracle://", "mssql://"): OracleToMSSQL,
    ("oracle://", "oracle://"): OracleToOracle,
    ("oracle://", "redis://"): OracleToRedis,
    ("oracle://", "dynamodb://"): OracleToDynamoDB,
    ("oracle://", "elasticsearch://"): OracleToElastic,
    ("oracle://", "clickhouse://"): OracleToClickHouse,

    # Elasticsearch
    ("elasticsearch://", "mysql://"): ElasticToMySQL,
    ("elasticsearch://", "mariadb://"): ElasticToMaria,
    ("elasticsearch://", "mongodb://"): ElasticToMongo,
    ("elasticsearch://", "postgresql://"): ElasticToPostgres,
    ("elasticsearch://", "sqlite://"): ElasticToSQLite,
    ("elasticsearch://", "mssql://"): ElasticToMSSQL,
    ("elasticsearch://", "oracle://"): ElasticToOracle,
    ("elasticsearch://", "redis://"): ElasticToRedis,
    ("elasticsearch://", "dynamodb://"): ElasticToDynamoDB,
    ("elasticsearch://", "elasticsearch://"): ElasticToElastic,
    ("elasticsearch://", "clickhouse://"): ElasticToClickHouse,

    # Redis
    ("redis://", "mysql://"): RedisToMySQL,
    ("redis://", "mariadb://"): RedisToMaria,
    ("redis://", "mongodb://"): RedisToMongo,
    ("redis://", "postgresql://"): RedisToPostgres,
    ("redis://", "sqlite://"): RedisToSQLite,
    ("redis://", "mssql://"): RedisToMSSQL,
    ("redis://", "oracle://"): RedisToOracle,
    ("redis://", "redis://"): RedisToRedis,
    ("redis://", "dynamodb://"): RedisToDynamoDB,
    ("redis://", "elasticsearch://"): RedisToElastic,
    ("redis://", "clickhouse://"): RedisToClickHouse,

    # DynamoDB
    ("dynamodb://", "mysql://"): DynamoToMySQL,
    ("dynamodb://", "mariadb://"): DynamoToMaria,
    ("dynamodb://", "mongodb://"): DynamoToMongo,
    ("dynamodb://", "postgresql://"): DynamoToPostgres,
    ("dynamodb://", "sqlite://"): DynamoToSQLite,
    ("dynamodb://", "mssql://"): DynamoToMSSQL,
    ("dynamodb://", "oracle://"): DynamoToOracle,
    ("dynamodb://", "redis://"): DynamoToRedis,
    ("dynamodb://", "dynamodb://"): DynamoToDynamo,
    ("dynamodb://", "elasticsearch://"): DynamoToElastic,
    ("dynamodb://", "clickhouse://"): DynamoToClickHouse,

    # SQLite
    ("sqlite://", "mysql://"): SQLiteToMySQL,
    ("sqlite://", "mariadb://"): SQLiteToMaria,
    ("sqlite://", "mongodb://"): SQLiteToMongo,
    ("sqlite://", "postgresql://"): SQLiteToPostgres,
    ("sqlite://", "sqlite://"): SQLiteToSQLite,
    ("sqlite://", "mssql://"): SQLiteToMSSQL,
    ("sqlite://", "oracle://"): SQLiteToOracle,
    ("sqlite://", "redis://"): SQLiteToRedis,
    ("sqlite://", "dynamodb://"): SQLiteToDynamoDB,
    ("sqlite://", "elasticsearch://"): SQLiteToElastic,
    ("sqlite://", "clickhouse://"): SQLiteToClickHouse,

    # ClickHouse
    ("clickhouse://", "mysql://"): ClickHouseToMySQL,
    ("clickhouse://", "mariadb://"): ClickHouseToMaria,
    ("clickhouse://", "mongodb://"): ClickHouseToMongo,
    ("clickhouse://", "postgresql://"): ClickHouseToPostgres,
    ("clickhouse://", "sqlite://"): ClickHouseToSQLite,
    ("clickhouse://", "mssql://"): ClickHouseToMSSQL,
    ("clickhouse://", "oracle://"): ClickHouseToOracle,
    ("clickhouse://", "redis://"): ClickHouseToRedis,
    ("clickhouse://", "dynamodb://"): ClickHouseToDynamoDB,
    ("clickhouse://", "elasticsearch://"): ClickHouseToElastic,
    ("clickhouse://", "clickhouse://"): ClickHouseToClickHouse,
}



