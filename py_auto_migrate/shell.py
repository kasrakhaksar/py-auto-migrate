import shlex
import os
import click
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
    console.print("Type [command]help[/command] for usage, or [command]exit[/command] to quit.\n")

    history = InMemoryHistory()
    session = PromptSession(history=history, auto_suggest=AutoSuggestFromHistory())

    while True:
        try:
            cmd = session.prompt([('class:prompt', "py-auto-migrate> ")], style=style).strip()
            if not cmd:
                continue

            # ==== Exit ====
            if cmd in ["exit", "quit"]:
                console.print("👋 [info]Exiting Py-Auto-Migrate.[/info]")
                break

            # ==== Help ====
            if cmd == "help":
                console.print("""
[bold cyan]Py-Auto-Migrate Interactive Shell[/bold cyan]
---------------------------------------------------------

This shell allows you to migrate data between different databases interactively.

[bold green]Supported Databases:[/bold green]
  • MongoDB
  • MySQL
  • MariaDB
  • PostgreSQL
  • SQLite

[bold green]Available Commands:[/bold green]
  [command]migrate --source "<uri>" --target "<uri>" [--table <name>][/command]
      → Migrate data from one database to another.
        Use [--table] to migrate a single table or collection (optional).

                              
  [command]exit[/command] or [command]quit[/command]
      → Exit the interactive shell.

[bold green]Connection URI Examples:[/bold green]
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

[bold green]Usage Examples:[/bold green]
  ➤ Migrate entire database:
    [command]migrate --source "postgresql://user:pass@localhost:5432/db" --target "mysql://user:pass@localhost:3306/db"[/command]

  ➤ Migrate from MariaDB to MongoDB:
    [command]migrate --source "mariadb://root:1234@localhost:3306/source_db" --target "mongodb://localhost:27017/target_db"[/command]

  ➤ Migrate one table only:
    [command]migrate --source "sqlite:///C:/data/mydb.sqlite" --target "postgresql://user:pass@localhost:5432/db" --table "customers"[/command]

  ➤ Migrate from MongoDB to SQLite:
    [command]migrate --source "mongodb://localhost:27017/db" --target "sqlite:///C:/mydb.sqlite" --table "users"[/command]

[bold green]Notes:[/bold green]
  • Table/collection names are case-sensitive.
  • Existing tables in target databases will NOT be replaced.
  • Compatible with live servers for MySQL, MariaDB, PostgreSQL, and MongoDB.

---------------------------------------------------------
Type [command]exit[/command] to leave this shell.
                """, highlight=False)
                continue

            # ==== Clear Screen ====
            if cmd in ["cls", "clear"]:
                os.system("cls" if os.name == "nt" else "clear")
                continue

            # ==== Migrate Command ====
            args = shlex.split(cmd)
            if args[0] == "migrate":
                migrate.main(args=args[1:], prog_name="py-auto-migrate", standalone_mode=False)
            else:
                console.print(f"❌ [error]Unknown command: {escape(args[0])}[/error]")

        except Exception as e:
            console.print(f"⚠ [error]Error: {escape(str(e))}[/error]")


if __name__ == "__main__":
    repl()
