import click

try:
    from py_auto_migrate.mapping import MIGRATION_MAP, ALL_DATABASES_LIST , AI_SUPPORTED_DATABASES
except ImportError:
    try:
        from .mapping import MIGRATION_MAP, ALL_DATABASES_LIST , AI_SUPPORTED_DATABASES
    except ImportError:
        from mapping import MIGRATION_MAP, ALL_DATABASES_LIST , AI_SUPPORTED_DATABASES


def get_uri(uri):
    for prefix in ALL_DATABASES_LIST:
        if uri.startswith(prefix):
            return prefix.lower()
    return None

@click.group(help="""
🚀 Py-Auto-Migrate

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
  dynamodb://<aws_access_key>:<aws_secret_key>@<host>:<port>/<database>?region=<region>
             

Elastic Search:
  elasticsearch://username:password@localhost:9200
             

SQLite:
  sqlite:///<path_to_sqlite_file>


Click House:
  clickhouse://<user>:<password>@<host>:<port>/<database>


Usage:

⚡ Migrate all tables:
    py-auto-migrate migrate --source "postgresql://user:pass@localhost:5432/db" --target "mysql://user:pass@localhost:3306/db"

⚡ Migrate a single table:
    py-auto-migrate migrate --source "mariadb://user:pass@localhost:3306/db" --target "mongodb://username:password@<host>:<port>/<database>" --table "users"

🤖 Migrate with AI query (Target must be a relational database):
    py-auto-migrate migrate --source "postgresql://user:pass@localhost:5432/db" --target "mysql://user:pass@localhost:3306/db" --ai-ask "only users older than 30" --ai-model "gpt-3.5-turbo"
""")


def main():
    pass


@main.command(help="""
📤 Perform migration between databases.

Parameters:
  --source      Source DB URI 
  --target      Target DB URI
  --table       (Optional) Migrate only one table
  --ai-ask      (Optional) Natural language query
  --ai-model    (Optional) OpenAI model (default: gpt-3.5-turbo)
""")
@click.option('--source', required=True, help="Source DB URI")
@click.option('--target', required=True, help="Target DB URI")
@click.option('--table', required=False, help="(optional) Table name")
@click.option('--ai-ask', required=False, help="(optional) Natural language query for AI (e.g., 'i want to insert users with age > 25')")
@click.option('--ai-model', required=False, help="(optional) OpenAI model (default: gpt-3.5-turbo)")

def migrate(source, target, table, ai_ask, ai_model):

    source_type = get_uri(source)
    target_type = get_uri(target)

    if not source_type or not target_type:
        click.echo("❌ Invalid source or target URI format.")
        return

    if ai_ask and target_type not in AI_SUPPORTED_DATABASES:
        click.echo(f"❌ Sorry, AI queries are not supported for {target_type.upper()} database.")
        click.echo(f"✅ AI supported databases: {', '.join(AI_SUPPORTED_DATABASES)}")
        return

    migration_class = MIGRATION_MAP.get((source_type, target_type))

    if not migration_class:
        click.echo(
            f"❌ Migration from {source_type} to {target_type} not supported yet.")
        return

    try:
        migration = migration_class(source, target)

        if ai_ask and not ai_model:
            ai_model = 'gpt-3.5-turbo'

        if ai_ask and table:
            click.echo(f"🤖 Using AI query: {ai_ask}")
            click.echo(f"📤 Migrating single table: {table} with AI filter")
            migration.migrate_one(table, ai_ask, ai_model)
        
        elif ai_ask and not table:
            click.echo(f"🤖 Using AI query: {ai_ask}")
            click.echo(f"📤 Migrating all tables with AI filter")
            tables = migration.get_tables()
            for tbl in tables:
                click.echo(f"  → Migrating table: {tbl}")
                migration.migrate_one(tbl, ai_ask, ai_model)
        
        elif not ai_ask and table:
            click.echo(f"📤 Migrating single table: {table}")
            migration.migrate_one(table)
        
        else:
            click.echo(f"📤 Migrating all tables from {source_type} to {target_type}")       
            migration.migrate_all()

        click.echo("✅ Migration completed successfully!")

    except Exception as e:
        click.echo(f"❌ Migration failed: {str(e)}")
        raise
    

  
if __name__ == "__main__":
    main()