import click

try:
    from .migrator import (
        MongoToMySQL, MongoToMongo, MySQLToMongo, MySQLToMySQL,
        PostgresToMySQL, PostgresToMongo, PostgresToPostgres,
        MySQLToPostgres, MongoToPostgres,
        MongoToSQLite, MySQLToSQLite, PostgresToSQLite,
        SQLiteToMySQL, SQLiteToPostgres, SQLiteToMongo, SQLiteToSQLite,
        MariaToMySQL, MariaToMongo, MariaToPostgres, MariaToSQLite, MariaToMaria
    )
except ImportError:
    try:
        from py_auto_migrate.migrator import (
            MongoToMySQL, MongoToMongo, MySQLToMongo, MySQLToMySQL,
            PostgresToMySQL, PostgresToMongo, PostgresToPostgres,
            MySQLToPostgres, MongoToPostgres,
            MongoToSQLite, MySQLToSQLite, PostgresToSQLite,
            SQLiteToMySQL, SQLiteToPostgres, SQLiteToMongo, SQLiteToSQLite,
            MariaToMySQL, MariaToMongo, MariaToPostgres, MariaToSQLite, MariaToMaria
        )
    except ImportError:
        from migrator import (
            MongoToMySQL, MongoToMongo, MySQLToMongo, MySQLToMySQL,
            PostgresToMySQL, PostgresToMongo, PostgresToPostgres,
            MySQLToPostgres, MongoToPostgres,
            MongoToSQLite, MySQLToSQLite, PostgresToSQLite,
            SQLiteToMySQL, SQLiteToPostgres, SQLiteToMongo, SQLiteToSQLite,
            MariaToMySQL, MariaToMongo, MariaToPostgres, MariaToSQLite, MariaToMaria
        )


@click.group(help="""
🚀 Py-Auto-Migrate CLI

Easily migrate data between different database systems.

Supported databases:
- MongoDB
- MySQL
- MariaDB
- PostgreSQL
- SQLite

Connection URI examples:

PostgreSQL:
  postgresql://<user>:<password>@<host>:<port>/<database>
  Example:
    postgresql://postgres:1234@localhost:5432/testdb

MySQL:
  mysql://<user>:<password>@<host>:<port>/<database>
  Example:
    mysql://root:1234@localhost:3306/testdb

MariaDB:
  mariadb://<user>:<password>@<host>:<port>/<database>
  Example:
    mariadb://root:1234@localhost:3306/mydb

MongoDB:
  mongodb://<host>:<port>/<database>
  Example:
    mongodb://localhost:27017/testdb

SQLite:
  sqlite:///<path_to_sqlite_file>
  Example:
    sqlite:///C:/databases/mydb.sqlite

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
  --source      Source DB URI (mysql:// | mariadb:// | mongodb:// | postgresql:// | sqlite://)
  --target      Target DB URI (mysql:// | mariadb:// | mongodb:// | postgresql:// | sqlite://)
  --table       (Optional) Migrate only one table/collection
""")
@click.option('--source', required=True, help="Source DB URI (mysql:// | mariadb:// | mongodb:// | postgresql:// | sqlite://)")
@click.option('--target', required=True, help="Target DB URI (mysql:// | mariadb:// | mongodb:// | postgresql:// | sqlite://)")
@click.option('--table', required=False, help="Table/Collection name (optional)")
def migrate(source, target, table):
    """Run migration"""

    # =================== MongoDB ===================
    if source.startswith("mongodb://") and target.startswith("mysql://"):
        m = MongoToMySQL(source, target)
    elif source.startswith("mongodb://") and target.startswith("mariadb://"):
        m = MariaToMongo(source, target)
    elif source.startswith("mongodb://") and target.startswith("mongodb://"):
        m = MongoToMongo(source, target)
    elif source.startswith("mongodb://") and target.startswith("postgresql://"):
        m = MongoToPostgres(source, target)
    elif source.startswith("mongodb://") and target.startswith("sqlite://"):
        m = MongoToSQLite(source, target)

    # =================== MySQL ===================
    elif source.startswith("mysql://") and target.startswith("mysql://"):
        m = MySQLToMySQL(source, target)
    elif source.startswith("mysql://") and target.startswith("mongodb://"):
        m = MySQLToMongo(source, target)
    elif source.startswith("mysql://") and target.startswith("postgresql://"):
        m = MySQLToPostgres(source, target)
    elif source.startswith("mysql://") and target.startswith("sqlite://"):
        m = MySQLToSQLite(source, target)
    elif source.startswith("mysql://") and target.startswith("mariadb://"):
        m = MariaToMySQL(source, target)

    # =================== MariaDB ===================
    elif source.startswith("mariadb://") and target.startswith("mariadb://"):
        m = MariaToMaria(source, target)
    elif source.startswith("mariadb://") and target.startswith("mysql://"):
        m = MariaToMySQL(source, target)
    elif source.startswith("mariadb://") and target.startswith("mongodb://"):
        m = MariaToMongo(source, target)
    elif source.startswith("mariadb://") and target.startswith("postgresql://"):
        m = MariaToPostgres(source, target)
    elif source.startswith("mariadb://") and target.startswith("sqlite://"):
        m = MariaToSQLite(source, target)

    # =================== PostgreSQL ===================
    elif source.startswith("postgresql://") and target.startswith("mysql://"):
        m = PostgresToMySQL(source, target)
    elif source.startswith("postgresql://") and target.startswith("mariadb://"):
        m = MariaToPostgres(source, target)
    elif source.startswith("postgresql://") and target.startswith("mongodb://"):
        m = PostgresToMongo(source, target)
    elif source.startswith("postgresql://") and target.startswith("postgresql://"):
        m = PostgresToPostgres(source, target)
    elif source.startswith("postgresql://") and target.startswith("sqlite://"):
        m = PostgresToSQLite(source, target)

    # =================== SQLite ===================
    elif source.startswith("sqlite://") and target.startswith("mysql://"):
        m = SQLiteToMySQL(source.replace("sqlite:///", ""), target)
    elif source.startswith("sqlite://") and target.startswith("mariadb://"):
        m = MariaToSQLite(source.replace("sqlite:///", ""), target)
    elif source.startswith("sqlite://") and target.startswith("postgresql://"):
        m = SQLiteToPostgres(source.replace("sqlite:///", ""), target)
    elif source.startswith("sqlite://") and target.startswith("mongodb://"):
        m = SQLiteToMongo(source.replace("sqlite:///", ""), target)
    elif source.startswith("sqlite://") and target.startswith("sqlite://"):
        m = SQLiteToSQLite(source.replace("sqlite:///", ""), target.replace("sqlite:///", ""))

    else:
        click.echo("❌ Migration type not supported yet.")
        return

    if table:
        m.migrate_one(table)
    else:
        m.migrate_all()


if __name__ == "__main__":
    main()
