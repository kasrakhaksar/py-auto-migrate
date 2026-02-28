import click

try:
    from py_auto_migrate.mapping import MIGRATION_MAP, ALL_DATABASES_LIST
except ImportError:
    try:
        from .mapping import MIGRATION_MAP, ALL_DATABASES_LIST
    except ImportError:
        from mapping import MIGRATION_MAP, ALL_DATABASES_LIST


def get_uri(uri):
    for prefix in ALL_DATABASES_LIST:
        if uri.startswith(prefix):
            return prefix.lower()
    return None


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
- Click House
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


Click House:
  clickhouse://<user>:<password>@<host>:<port>/<database>


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

    source_type = get_uri(source)
    target_type = get_uri(target)

    if not source_type or not target_type:
        click.echo("❌ Invalid source or target URI format.")
        return

    migration_class = MIGRATION_MAP.get((source_type, target_type))

    if not migration_class:
        click.echo(
            f"❌ Migration from {source_type} to {target_type} not supported yet.")
        return

    if source_type == "sqlite://":
        source = source.replace("sqlite:///", "")
        if target_type == "sqlite://":
            target = target.replace("sqlite:///", "")

    try:
        migration = migration_class(source, target)

        if table:
            click.echo(f"📤 Migrating single table/collection: {table}")
            migration.migrate_one(table)
        else:
            click.echo(
                f"📤 Migrating all tables/collections from {source_type} to {target_type}")
            migration.migrate_all()

        click.echo("✅ Migration completed successfully!")

    except Exception as e:
        click.echo(f"❌ Migration failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
