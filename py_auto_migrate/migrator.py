from py_auto_migrate.migrate_models.migrate_mongodb import (
    MongoToMongo,
    MongoToMySQL,
    MongoToPostgres,
    MongoToSQLite,
    MongoToMaria,
    MongoToOracle,
    MongoToMSSQL
)

from py_auto_migrate.migrate_models.migrate_mysql import (
    MySQLToMongo,
    MySQLToMySQL,
    MySQLToPostgres,
    MySQLToSQLite,
    MySQLToMaria,
    MySQLToOracle,
    MySQLToMSSQL,
)

from py_auto_migrate.migrate_models.migrate_postgresql import (
    PostgresToMongo,
    PostgresToPostgres,
    PostgresToMySQL,
    PostgresToSQLite,
    PostgresToMaria,
    PostgresToOracle,
    PostgresToMSSQL
)

from py_auto_migrate.migrate_models.migrate_sqlite import (
    SQLiteToSQLite,
    SQLiteToPostgres,
    SQLiteToMongo,
    SQLiteToMySQL,
    SQLiteToMaria,
    SQLiteToOracle,
    SQLiteToMSSQL
)

from py_auto_migrate.migrate_models.migrate_mariadb import (
    MariaToSQLite,
    MariaToPostgres,
    MariaToMaria,
    MariaToMongo,
    MariaToMySQL,
    MariaToMSSQL,
    MariaToOracle
)

from py_auto_migrate.migrate_models.migrate_mssql import (
    MSSQLToMaria,
    MSSQLToPostgres,
    MSSQLToMSSQL,
    MSSQLToMongo,
    MSSQLToMySQL,
    MSSQLToOracle,
    MSSQLToSQLite
)


from py_auto_migrate.migrate_models.migrate_oracle import (
    OracleToMySQL,
    OracleToMaria,
    OracleToPostgres,
    OracleToSQLite,
    OracleToMSSQL,
    OracleToMongo,
    OracleToOracle,
)