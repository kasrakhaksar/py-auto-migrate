import click
from .migrator import (
    MongoToMySQL, MongoToMongo, MySQLToMongo, MySQLToMySQL,
    PostgresToMySQL, PostgresToMongo, PostgresToPostgres,
    MySQLToPostgres, MongoToPostgres
)

@click.group(help="""
🚀 Py-Auto-Migrate CLI

This tool allows you to migrate data between different databases:

Supported databases:
- MongoDB
- MySQL
- PostgreSQL

Connection URI examples:

PostgreSQL:
  postgresql://<user>:<password>@<host>:<port>/<database>
  Example:
    postgresql://postgres:Kasrakhaksar1313@localhost:5432/testdb

MySQL:
  mysql://<user>:<password>@<host>:<port>/<database>
  Example:
    mysql://root:1234@localhost:3306/testdb

MongoDB:
  mongodb://<host>:<port>/<database>
  Example:
    mongodb://localhost:27017/testdb

Usage:

⚡ Migrate all tables/collections:
    python cli.py migrate --source "postgresql://user:pass@localhost:5432/db" --target "mysql://user:pass@localhost:3306/db"

 
⚡ Migrate a single table/collection:
    python cli.py migrate --source "mongodb://localhost:27017/db" --target "postgresql://user:pass@localhost:5432/db" --table "my_collection"
""")
def main():
    pass


@main.command(help="""
Migrate data between different databases.

Parameters:
  --source      Source DB URI (mysql:// | mongodb:// | postgresql://)
  --target      Target DB URI (mysql:// | mongodb:// | postgresql://)
  --table       Optional: Table/Collection name to migrate only that
""")
@click.option('--source', required=True, help="Source DB URI (mysql:// | mongodb:// | postgresql://)")
@click.option('--target', required=True, help="Target DB URI (mysql:// | mongodb:// | postgresql://)")
@click.option('--table', required=False, help="Table/Collection name (optional)")
def migrate(source, target, table):
    """Run migration"""
    # =================== MongoDB ===================
    if source.startswith("mongodb://") and target.startswith("mysql://"):
        m = MongoToMySQL(source, target)

    elif source.startswith("mongodb://") and target.startswith("mongodb://"):
        m = MongoToMongo(source, target)

    elif source.startswith("mongodb://") and target.startswith("postgresql://"):
        m = MongoToPostgres(source, target)

    # =================== MySQL ===================
    elif source.startswith("mysql://") and target.startswith("mysql://"):
        m = MySQLToMySQL(source, target)

    elif source.startswith("mysql://") and target.startswith("mongodb://"):
        m = MySQLToMongo(source, target)

    elif source.startswith("mysql://") and target.startswith("postgresql://"):
        m = MySQLToPostgres(source, target)

    # =================== PostgreSQL ===================
    elif source.startswith("postgresql://") and target.startswith("mysql://"):
        m = PostgresToMySQL(source, target)

    elif source.startswith("postgresql://") and target.startswith("mongodb://"):
        m = PostgresToMongo(source, target)

    elif source.startswith("postgresql://") and target.startswith("postgresql://"):
        m = PostgresToPostgres(source, target)

    else:
        click.echo("❌ Migration type not supported yet / نوع مهاجرت پشتیبانی نمی‌شود.")
        return

    # Run migration
    if table:
        m.migrate_one(table)
    else:
        m.migrate_all()


if __name__ == "__main__":
    main()
