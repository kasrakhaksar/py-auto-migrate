import click

try:
    from .migrator import *
except ImportError:
    try:
        from py_auto_migrate.migrator import *
    except ImportError:
        from migrator import *


@click.group(help="""
🚀 Py-Auto-Migrate CLI

Easily migrate data between different database systems.

Supported databases:
- MongoDB
- MySQL
- MariaDB
- PostgreSQL
- Oracle
- SQL Server
- DynamoDB
- Redis
- Elastic Search
- SQLite
             

Connection URI examples:

PostgreSQL:
  postgresql://<user>:<password>@<host>:<port>/<database>


MySQL:
  mysql://<user>:<password>@<host>:<port>/<database>


MariaDB:
  mariadb://<user>:<password>@<host>:<port>/<database>


MongoDB:
  mongodb://<host>:<port>/<database>
  mongodb://username:password@<host>:<port>/<database>
   

SQL Server (SQL Auth):
  mssql://<user>:<password>@<host>:<port>/<database>
SQL Server (Windows Auth):
  mssql://@<host>:<port>/<database>

             
Redis:
  redis://[:password]@<host>:<port>/<db>
  redis://<host>:<port>/<db>


Oracle:
  oracle://<user>:<password>@<host>:<port>/<service_name>


DynamoDB:
  dynamodb://<aws_access_key>:<aws_secret_key>@<host>:<port>/<table>?region=<region>
             

Elastic Search:
    elasticsearch://username:password@localhost:9200
             

SQLite:
  sqlite:///<path_to_sqlite_file>



Usage:

⚡ Migrate all tables/collections:
    py-auto-migrate migrate --source "postgresql://user:pass@localhost:5432/db" --target "mysql://user:pass@localhost:3306/db"

⚡ Migrate a single table/collection:
    py-auto-migrate migrate --source "mariadb://user:pass@localhost:3306/db" --target "mongodb://username:password@<host>:<port>/<database>" --table "users"
             

""")


def main():
    pass


@main.command(help="""
📤 Perform migration between databases.

Parameters:
  --source      Source DB URI 
  --target      Target DB URI
  --table       (Optional) Migrate only one table/collection
""")
@click.option('--source', required=True, help="Source DB URI")
@click.option('--target', required=True, help="Target DB URI")
@click.option('--table', required=False, help="Table/Collection name (optional)")
def migrate(source, target, table):
    """Run migration"""

    # =================== MongoDB ===================
    if source.startswith("mongodb://"):
        if target.startswith("mysql://"):
            m = MongoToMySQL(source, target)
        elif target.startswith("mariadb://"):
            m = MongoToMaria(source, target)
        elif target.startswith("mongodb://"):
            m = MongoToMongo(source, target)
        elif target.startswith("postgresql://"):
            m = MongoToPostgres(source, target)
        elif target.startswith("sqlite://"):
            m = MongoToSQLite(source, target)
        elif target.startswith("mssql://"):
            m = MongoToMSSQL(source, target)
        elif target.startswith("oracle://"):
            m = MongoToOracle(source, target)
        elif target.startswith("redis://"):
            m = MongoToRedis(source, target)
        elif target.startswith("dynamodb://"):
            m = MongoToDynamoDB(source, target)
        elif target.startswith("elasticsearch://"):
            m = MongoToElastic(source, target)
        else:
            m = None

    # =================== MySQL ===================
    elif source.startswith("mysql://"):
        if target.startswith("mysql://"):
            m = MySQLToMySQL(source, target)
        elif target.startswith("mariadb://"):
            m = MySQLToMaria(source, target)
        elif target.startswith("mongodb://"):
            m = MySQLToMongo(source, target)
        elif target.startswith("postgresql://"):
            m = MySQLToPostgres(source, target)
        elif target.startswith("sqlite://"):
            m = MySQLToSQLite(source, target)
        elif target.startswith("mssql://"):
            m = MySQLToMSSQL(source, target)
        elif target.startswith("oracle://"):
            m = MySQLToOracle(source, target)
        elif target.startswith("redis://"):
            m = MySQLToRedis(source, target)
        elif target.startswith("dynamodb://"):
            m = MySQLToDynamoDB(source, target)
        elif target.startswith("elasticsearch://"):
            m = MySQLToElastic(source, target)            
        else:
            m = None

    # =================== MariaDB ===================
    elif source.startswith("mariadb://"):
        if target.startswith("mysql://"):
            m = MariaToMySQL(source, target)
        elif target.startswith("mariadb://"):
            m = MariaToMaria(source, target)
        elif target.startswith("mongodb://"):
            m = MariaToMongo(source, target)
        elif target.startswith("postgresql://"):
            m = MariaToPostgres(source, target)
        elif target.startswith("sqlite://"):
            m = MariaToSQLite(source, target)
        elif target.startswith("mssql://"):
            m = MariaToMSSQL(source, target)
        elif target.startswith("oracle://"):
            m = MariaToOracle(source, target)
        elif target.startswith("redis://"):
            m = MariaToRedis(source, target)
        elif target.startswith("dynamodb://"):
            m = MariaToDynamoDB(source, target)
        elif target.startswith("elasticsearch://"):
            m = MariaDBToElastic(source, target)            
        else:
            m = None

    # =================== PostgreSQL ===================
    elif source.startswith("postgresql://"):
        if target.startswith("mysql://"):
            m = PostgresToMySQL(source, target)
        elif target.startswith("mariadb://"):
            m = PostgresToMaria(source, target)
        elif target.startswith("mongodb://"):
            m = PostgresToMongo(source, target)
        elif target.startswith("postgresql://"):
            m = PostgresToPostgres(source, target)
        elif target.startswith("sqlite://"):
            m = PostgresToSQLite(source, target)
        elif target.startswith("mssql://"):
            m = PostgresToMSSQL(source, target)
        elif target.startswith("oracle://"):
            m = PostgresToOracle(source, target)
        elif target.startswith("redis://"):
            m = PostgresToRedis(source, target)
        elif target.startswith("dynamodb://"):
            m = PostgresToDynamoDB(source, target)
        elif target.startswith("elasticsearch://"):
            m = PostgresToElastic(source, target)
        else:
            m = None

    # =================== SQL Server ===================
    elif source.startswith("mssql://") or source.startswith("MSSQL://"):
        if target.startswith("mysql://"):
            m = MSSQLToMySQL(source, target)
        elif target.startswith("mariadb://"):
            m = MSSQLToMaria(source, target)
        elif target.startswith("mongodb://"):
            m = MSSQLToMongo(source, target)
        elif target.startswith("postgresql://"):
            m = MSSQLToPostgres(source, target)
        elif target.startswith("sqlite://"):
            m = MSSQLToSQLite(source, target)
        elif target.startswith("oracle://"):
            m = MSSQLToOracle(source, target)
        elif target.startswith("mssql://") or target.startswith("MSSQL://"):
            m = MSSQLToMSSQL(source, target)
        elif target.startswith("redis://"):
            m = MSSQLToRedis(source, target)
        elif target.startswith("dynamodb://"):
            m = MSSQLToDynamoDB(source, target)
        elif target.startswith("elasticsearch://"):
            m = MSSQLToElastic(source, target)
        else:
            m = None

    # =================== Oracle ===================
    elif source.startswith("oracle://"):
        if target.startswith("mysql://"):
            m = OracleToMySQL(source, target)
        elif target.startswith("postgresql://"):
            m = OracleToPostgres(source, target)
        elif target.startswith("sqlite://"):
            m = OracleToSQLite(source, target)
        elif target.startswith("mariadb://"):
            m = OracleToMaria(source, target)
        elif target.startswith("mssql://"):
            m = OracleToMSSQL(source, target)
        elif target.startswith("mongodb://"):
            m = OracleToMongo(source, target)
        elif target.startswith("oracle://"):
            m = OracleToOracle(source, target)
        elif target.startswith("redis://"):
            m = OracleToRedis(source, target)
        elif target.startswith("dynamodb://"):
            m = OracleToDynamoDB(source, target)
        elif target.startswith("elasticsearch://"):
            m = OracleToElastic(source, target)
        else:
            m = None


    # =================== Elasticsearch ===================
    if source.startswith("elasticsearch://"):
        if target.startswith("mysql://"):
            m = ElasticToMySQL(source, target)
        elif target.startswith("mariadb://"):
            m = ElasticToMaria(source, target)
        elif target.startswith("mongodb://"):
            m = ElasticToMongo(source, target)
        elif target.startswith("postgresql://"):
            m = ElasticToPostgres(source, target)
        elif target.startswith("sqlite://"):
            m = ElasticToSQLite(source, target)
        elif target.startswith("mssql://"):
            m = ElasticToMSSQL(source, target)
        elif target.startswith("oracle://"):
            m = ElasticToOracle(source, target)
        elif target.startswith("redis://"):
            m = ElasticToRedis(source, target)
        elif target.startswith("dynamodb://"):
            m = ElasticToDynamoDB(source, target)
        elif target.startswith("elasticsearch://"):
            m = ElasticToElastic(source, target)
        else:
            m = None

    # =================== Redis ===================
    elif source.startswith("redis://"):
        if target.startswith("mysql://"):
            m = RedisToMySQL(source, target)
        elif target.startswith("mariadb://"):
            m = RedisToMaria(source, target)
        elif target.startswith("mongodb://"):
            m = RedisToMongo(source, target)
        elif target.startswith("postgresql://"):
            m = RedisToPostgres(source, target)
        elif target.startswith("sqlite://"):
            m = RedisToSQLite(source, target)
        elif target.startswith("mssql://"):
            m = RedisToMSSQL(source, target)
        elif target.startswith("oracle://"):
            m = RedisToOracle(source, target)
        elif target.startswith("redis://"):
            m = RedisToRedis(source, target)
        elif target.startswith("dynamodb://"):
            m = RedisToDynamoDB(source, target)
        elif target.startswith("elasticsearch://"):
            m = RedisToElastic(source, target)
        else:
            m = None

    # =================== DynamoDB ===================
    elif source.startswith("dynamodb://"):
        if target.startswith("mongodb://"):
            m = DynamoToMongo(source, target)
        elif target.startswith("mysql://"):
            m = DynamoToMySQL(source, target)
        elif target.startswith("postgresql://"):
            m = DynamoToPostgres(source, target)
        elif target.startswith("mariadb://"):
            m = DynamoToMaria(source, target)
        elif target.startswith("sqlite://"):
            m = DynamoToSQLite(source, target)
        elif target.startswith("mssql://"):
            m = DynamoToMSSQL(source, target)
        elif target.startswith("oracle://"):
            m = DynamoToOracle(source, target)
        elif target.startswith("redis://"):
            m = DynamoToRedis(source, target)
        elif target.startswith("dynamodb://"):
            m = DynamoToDynamo(source, target)
        elif target.startswith("elasticsearch://"):
            m = DynamoToElastic(source, target)
        else:
            m = None

    # =================== SQLite ===================
    elif source.startswith("sqlite://"):
        src_path = source.replace("sqlite:///", "")
        tgt_path = target.replace(
            "sqlite:///", "") if target.startswith("sqlite://") else target

        if target.startswith("mysql://"):
            m = SQLiteToMySQL(src_path, tgt_path)
        elif target.startswith("mariadb://"):
            m = SQLiteToMaria(src_path, tgt_path)
        elif target.startswith("postgresql://"):
            m = SQLiteToPostgres(src_path, tgt_path)
        elif target.startswith("mongodb://"):
            m = SQLiteToMongo(src_path, tgt_path)
        elif target.startswith("sqlite://"):
            m = SQLiteToSQLite(src_path, tgt_path)
        elif target.startswith("mssql://") or target.startswith("MSSQL://"):
            m = SQLiteToMSSQL(src_path, tgt_path)
        elif target.startswith("oracle://"):
            m = SQLiteToOracle(src_path, tgt_path)
        elif target.startswith("redis://"):
            m = SQLiteToRedis(source, target)
        elif target.startswith("dynamodb://"):
            m = SQLiteToDynamoDB(source, target)
        elif target.startswith("elasticsearch://"):
            m = SQLiteToElastic(source, target)
        else:
            m = None

    else:
        m = None

    if not m:
        click.echo("❌ Migration type not supported yet.")
        return

    if table:
        m.migrate_one(table)
    else:
        m.migrate_all()


if __name__ == "__main__":
    main()