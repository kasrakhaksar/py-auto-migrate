import click
import threading
import webbrowser
import uvicorn
import time
import warnings
warnings.filterwarnings('ignore')
import logging

from py_auto_migrate.core.logging import configure_logging, get_logger
from py_auto_migrate.core.exceptions import PyAutoMigrateError
from py_auto_migrate.core.progress import ProgressSnapshot, ProgressTracker


logger = get_logger(__name__)

try:
    from py_auto_migrate.migrate.mapping import MIGRATION_MAP, ALL_DATABASES_LIST , AI_SUPPORTED_DATABASES , DEP_SUPPORTED_DATABASES
except ImportError:
    from .migrate.mapping import MIGRATION_MAP, ALL_DATABASES_LIST , AI_SUPPORTED_DATABASES , DEP_SUPPORTED_DATABASES




def get_uri(uri):
    for prefix in ALL_DATABASES_LIST:
        if uri.startswith(prefix):
            return prefix.lower()
    return None


def _render_progress(snapshot: ProgressSnapshot) -> None:
    """Render row-based progress without enabling a progress bar by default."""
    if not snapshot.current_table:
        return

    width = 32
    completed = int(width * snapshot.percent / 100)
    bar = "=" * completed + "-" * (width - completed)
    message = (
        f"\r[{bar}] {snapshot.percent:6.2f}% "
        f"{snapshot.current_table_processed}/{snapshot.current_table_total} rows "
        f"({snapshot.current_table})"
    )
    click.echo(message, nl=snapshot.status in {"completed", "completed_with_errors"})


def _render_migration_summary(summary: dict) -> None:
    click.echo("\nMigration summary:")
    click.echo(
        f"Tables: {summary['tables_succeeded']} succeeded, "
        f"{summary['tables_failed']} failed, {summary['tables_empty']} empty, "
        f"{summary['tables_already_present']} already up to date "
        f"({summary['tables_total']} total)"
    )
    click.echo(
        f"Rows: {summary['rows_read']} read, "
        f"{summary['rows_submitted']} submitted successfully, "
        f"{summary['rows_skipped_existing']} already present"
    )
    for result in summary["table_results"]:
        if result["status"] == "failed":
            click.echo(f"  Failed: {result['table']} — {result['error']}")


@click.group(help="""

Py-Auto-Migrate

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
dynamodb://<aws_access_key>:<aws_secret_key>@<host>:<port>/?region=<region>
            

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
             
⚡ Migrate table forigen key dependency (Source must be a relational database):
    py-auto-migrate migrate --source "mssql://<user>:<password>@<host>:<port>/<database>" --target "mariadb://<user>:<password>@<host>:<port>/<database>" --table "orders" --dep

🤖 Migrate with AI query (Target must be a relational database):
    py-auto-migrate migrate --source "postgresql://user:pass@localhost:5432/db" --target "mysql://user:pass@localhost:3306/db" --ai-ask "only users older than 30" --ai-model "gpt-3.5-turbo"

             

             

🖥️ Dashboard :
             
For easier and more convenient migration operations, Py-Auto-Migrate provides a dedicated web dashboard.

Usage:
⚡  py-auto-migrate dashboard
             
🔗 Default dashboard URL:
    http://localhost:8123
             

or:
⚡  py-auto-migrate dashboard --host "localhost" --port 8000
   
            

✨ Dashboard Features:
    Easily configure source and target connections
    Select specific tables for migration
    View logs and errors in real-time
    Run migrations with a single click
    AI query support in a graphical interface
    Monitor migration progress
    Manage multiple migration jobs

""")
@click.option('--verbose', is_flag=True, help='Enable detailed debug logging.')
@click.option('--log-file', type=click.Path(dir_okay=False), help='Write logs to this file.')
def main(verbose, log_file):
    configure_logging(logging.DEBUG if verbose else logging.INFO, log_file)



@main.command(help="""

Perform migration between databases.

Parameters:
--source      Source DB URI 
--target      Target DB URI
--table       (Optional) Migrate only one table
--ai-ask      (Optional) Natural language query
--ai-model    (Optional) OpenAI model (default: gpt-3.5-turbo)
--dep         (Optional) Enable forigen key dependency mode
--pgbar       (Optional) Show row-based progress in the terminal
--skip-existing (Optional) Skip source rows already present in the target (disabled by default)

""")


@click.option('--source', required=True, help="Source DB URI")
@click.option('--target', required=True, help="Target DB URI")
@click.option('--table', required=False, help="(optional) Table name")
@click.option('--ai-ask', required=False, help="(optional) Natural language query for AI (e.g., 'i want to insert users with age > 25')")
@click.option('--ai-model', required=False, help="(optional) OpenAI model (default: gpt-3.5-turbo)")
@click.option('--dep', is_flag=True, help='(optional) Enable forigen key dependency mode')
@click.option('--pgbar', is_flag=True, help='Show row-based migration progress in the terminal.')
@click.option('--skip-existing', is_flag=True, help='Skip source rows already present in the target (disabled by default).')


def migrate(source, target, table, ai_ask, ai_model, dep, pgbar, skip_existing):


    source_type = get_uri(source)
    target_type = get_uri(target)

    if not source_type or not target_type:
        click.echo("❌ Invalid source or target URI format.")
        return


    if ai_ask and target_type not in AI_SUPPORTED_DATABASES:
        click.echo(f"❌ Sorry, AI queries are not supported for {target_type.upper()} database.")
        click.echo(f"✅ Supported databases: {', '.join(AI_SUPPORTED_DATABASES)}")
        return
    

    if dep and source_type not in DEP_SUPPORTED_DATABASES:
        click.echo(f"❌ Sorry, dependency mode are not supported for {source_type.upper()} database.")
        click.echo(f"✅ Supported databases: {', '.join(DEP_SUPPORTED_DATABASES)}")
        return


    migration_class = MIGRATION_MAP.get((source_type, target_type))

    if not migration_class:
        click.echo(
            f"❌ Migration from {source_type} to {target_type} not supported yet.")
        return


    try:
        progress = ProgressTracker(_render_progress) if pgbar else None
        migration = migration_class(
            source,
            target,
            progress=progress,
            skip_existing=skip_existing,
        )

        if ai_ask and not ai_model:
            ai_model = 'gpt-3.5-turbo'

        if table:
            migration.migrate_one(table, ai_ask, ai_model ,dep)
        else:
            migration.migrate_all(ai_ask, ai_model ,dep)

        _render_migration_summary(migration.summary)

    except PyAutoMigrateError:
        logger.exception("Migration failed")
        raise click.ClickException("Migration failed. Check the log for details.")
    except Exception as exc:
        logger.exception("Unexpected migration failure")
        raise click.ClickException(str(exc)) from exc
    


@main.command()
@click.option('--host', default='127.0.0.1', help='dashboard host')
@click.option('--port', default=8123, type=int, help='dashboard port')
def dashboard(host, port):
    
    def run():
        uvicorn.run(
            "py_auto_migrate.dashboard.app:app",
            host=host,
            port=port,
            reload=False
        )

    threading.Thread(
        target=run,
        daemon=True
    ).start()

    webbrowser.open(
        f"http://{host}:{port}"
    )

    click.echo(
        f"Dashboard running on http://{host}:{port}"
    )

    while True:
        time.sleep(1)

  
if __name__ == "__main__":
    main()
