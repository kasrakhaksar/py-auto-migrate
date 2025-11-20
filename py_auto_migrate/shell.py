import shlex
import os
from py_auto_migrate.cli import migrate
from rich.console import Console
from rich.markup import escape
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style

console = Console()

style = Style.from_dict({
    'prompt': 'bold cyan',
    'command': 'bold yellow',
    'info': 'green',
    'error': 'bold red',
})


def repl():
    console.print("🚀 [info]Welcome to Py-Auto-Migrate Shell[/info]")
    console.print(
        "Type [command]help[/command] for usage, or [command]exit[/command] to quit.\n"
    )

    history = InMemoryHistory()
    session = PromptSession(
        history=history,
        auto_suggest=AutoSuggestFromHistory()
    )

    while True:
        try:
            cmd = session.prompt(
                [('class:prompt', "py-auto-migrate> ")],
                style=style
            ).strip()

            if not cmd:
                continue

            if cmd.lower() in ["exit", "quit"]:
                console.print("👋 [info]Exiting Py-Auto-Migrate.[/info]")
                break

            if cmd.lower() == "help":
                console.print("""
[bold cyan]Py-Auto-Migrate Interactive Shell[/bold cyan]
---------------------------------------------------------

This shell allows you to migrate data between different databases interactively.

[bold green]Supported Databases:[/bold green]
  • MongoDB
  • MySQL
  • MariaDB
  • PostgreSQL
  • Oracle
  • SQL Server
  • DynamoDB
  • Redis
  • Elastic Search
  • SQLite

[bold green]Available Commands:[/bold green]
  [command]migrate --source "<uri>" --target "<uri>" [--table <name>][/command]
      → Migrate data from one database to another.
        Use [--table] to migrate a single table or collection (optional).


[bold green]Connection URI Examples:[/bold green]
  PostgreSQL:
    postgresql://<user>:<password>@<host>:<port>/<database>

  MySQL:
    mysql://<user>:<password>@<host>:<port>/<database>

  MariaDB:
    mariadb://<user>:<password>@<host>:<port>/<database>

  MongoDB:
    mongodb://<host>:<port>/<database>
    mongodb://username:password@<host>:<port>/<database>
                              
  Redis:
    redis://[:password]@<host>:<port>/<db>
    redis://<host>:<port>/<db>


  SQL Server (SQL Auth):
    mssql://<user>:<password>@<host>:<port>/<database>
  SQL Server (Windows Auth):
    mssql://@<host>:<port>/<database>

  Oracle:
    oracle://<user>:<password>@<host>:<port>/<service_name>
                              
  DynamoDB:
    dynamodb://<aws_access_key>:<aws_secret_key>@<host>:<port>/<table>?region=<region>
                              

  Elastic Search:
    elasticsearch://username:password@localhost:9200
                              
  SQLite:
    sqlite:///<path_to_sqlite_file>

[bold green]Usage Examples:[/bold green]
  ➤ Migrate entire database:
    [command]migrate --source "postgresql://user:pass@localhost:5432/db" --target "mysql://user:pass@localhost:3306/db"[/command]

  ➤ Migrate one table only:
    [command]migrate --source "sqlite:///C:/data/mydb.sqlite" --target "postgresql://user:pass@localhost:5432/db" --table customers[/command]

                              
[bold green]Notes:[/bold green]
  • Table/collection names are case-sensitive.
  • Existing tables in target databases will NOT be replaced.

---------------------------------------------------------
Type [command]exit[/command] to leave this shell.
                """, highlight=False)
                continue

            if cmd.lower() in ["cls", "clear"]:
                os.system("cls" if os.name == "nt" else "clear")
                continue

            args = shlex.split(cmd)
            if args[0] == "migrate":
                migrate.main(
                    args=args[1:],
                    prog_name="py-auto-migrate",
                    standalone_mode=False
                )
            else:
                console.print(
                    f"❌ [error]Unknown command: {escape(args[0])}[/error]"
                )

        except KeyboardInterrupt:
            console.print("\n⚠ [info]Use 'exit' to quit safely.[/info]")
        except Exception as e:
            console.print(f"⚠ [error]Error: {escape(str(e))}[/error]")


if __name__ == "__main__":
    repl()
