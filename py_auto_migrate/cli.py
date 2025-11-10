import click

try:
    from .migrator import (
        MongoToMySQL, MongoToMongo, MongoToPostgres, MongoToSQLite, MongoToMaria, MongoToMSSQL, MongoToOracle,
        MySQLToMongo, MySQLToMySQL, MySQLToPostgres, MySQLToSQLite, MySQLToMaria, MySQLToMSSQL, MySQLToOracle,
        PostgresToMongo, PostgresToPostgres, PostgresToMySQL, PostgresToSQLite, PostgresToMaria, PostgresToMSSQL, PostgresToOracle,
        SQLiteToMySQL, SQLiteToPostgres, SQLiteToMongo, SQLiteToSQLite, SQLiteToMaria, SQLiteToMSSQL, SQLiteToOracle,
        MariaToMySQL, MariaToMongo, MariaToPostgres, MariaToSQLite, MariaToMaria, MariaToMSSQL, MariaToOracle,
        MSSQLToMySQL, MSSQLToMongo, MSSQLToPostgres, MSSQLToSQLite, MSSQLToMaria, MSSQLToMSSQL, MSSQLToOracle,
        OracleToMySQL, OracleToMongo, OracleToPostgres, OracleToSQLite, OracleToMaria, OracleToMSSQL, OracleToOracle
    )
except ImportError:
    try:
        from py_auto_migrate.migrator import (
            MongoToMySQL, MongoToMongo, MongoToPostgres, MongoToSQLite, MongoToMaria, MongoToMSSQL, MongoToOracle,
            MySQLToMongo, MySQLToMySQL, MySQLToPostgres, MySQLToSQLite, MySQLToMaria, MySQLToMSSQL, MySQLToOracle,
            PostgresToMongo, PostgresToPostgres, PostgresToMySQL, PostgresToSQLite, PostgresToMaria, PostgresToMSSQL, PostgresToOracle,
            SQLiteToMySQL, SQLiteToPostgres, SQLiteToMongo, SQLiteToSQLite, SQLiteToMaria, SQLiteToMSSQL, SQLiteToOracle,
            MariaToMySQL, MariaToMongo, MariaToPostgres, MariaToSQLite, MariaToMaria, MariaToMSSQL, MariaToOracle,
            MSSQLToMySQL, MSSQLToMongo, MSSQLToPostgres, MSSQLToSQLite, MSSQLToMaria, MSSQLToMSSQL, MSSQLToOracle,
            OracleToMySQL, OracleToMongo, OracleToPostgres, OracleToSQLite, OracleToMaria, OracleToMSSQL, OracleToOracle
        )
    except ImportError:
        from migrator import (
            MongoToMySQL, MongoToMongo, MongoToPostgres, MongoToSQLite, MongoToMaria, MongoToMSSQL, MongoToOracle,
            MySQLToMongo, MySQLToMySQL, MySQLToPostgres, MySQLToSQLite, MySQLToMaria, MySQLToMSSQL, MySQLToOracle,
            PostgresToMongo, PostgresToPostgres, PostgresToMySQL, PostgresToSQLite, PostgresToMaria, PostgresToMSSQL, PostgresToOracle,
            SQLiteToMySQL, SQLiteToPostgres, SQLiteToMongo, SQLiteToSQLite, SQLiteToMaria, SQLiteToMSSQL, SQLiteToOracle,
            MariaToMySQL, MariaToMongo, MariaToPostgres, MariaToSQLite, MariaToMaria, MariaToMSSQL, MariaToOracle,
            MSSQLToMySQL, MSSQLToMongo, MSSQLToPostgres, MSSQLToSQLite, MSSQLToMaria, MSSQLToMSSQL, MSSQLToOracle,
            OracleToMySQL, OracleToMongo, OracleToPostgres, OracleToSQLite, OracleToMaria, OracleToMSSQL, OracleToOracle
        )


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

Oracle:
  oracle://<user>:<password>@<host>:<port>/<service_name>


SQLite:
  sqlite:///<path_to_sqlite_file>



Usage:

⚡ Migrate all tables/collections:
    py-auto-migrate migrate --source "postgresql://user:pass@localhost:5432/db" --target "mysql://user:pass@localhost:3306/db"

⚡ Migrate a single table/collection:
    py-auto-migrate migrate --source "mariadb://user:pass@localhost:3306/db" --target "mongodb://localhost:27017/db" --table "users"
""")
def main():
    pass


@main.command(help="""
📤 Perform migration between databases.

Parameters:
  --source      Source DB URI (mysql:// | mariadb:// | mongodb:// | postgresql:// | mssql:// | sqlite:// | oracle://)
  --target      Target DB URI (mysql:// | mariadb:// | mongodb:// | postgresql:// | mssql:// | sqlite:// | oracle://)
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
