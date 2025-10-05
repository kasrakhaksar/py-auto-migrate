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

            if cmd in ["exit", "quit"]:
                console.print("👋 [info]Exiting Py-Auto-Migrate.[/info]")
                break

            if cmd == "help":
                console.print("""
Available commands:
    [command]migrate --source "<uri>" --target "<uri>" [--table <name>][/command]
    [command]cls[/command] / [command]clear[/command]   -> Clear the screen
    [command]exit[/command] / [command]quit[/command]   -> Exit the shell
                      
note: [command][--table <name>][/command] is optional

Examples:
    [command]migrate --source "postgresql://user:pass@localhost:5432/db" --target "mysql://user:pass@localhost:3306/db"[/command]
    [command]migrate --source "mongodb://localhost:27017/db" --target "sqlite:///C:/mydb.sqlite" --table "users"[/command]
""", highlight=False)
                continue

            if cmd in ["cls", "clear"]:
                os.system("cls" if os.name == "nt" else "clear")
                continue

            args = shlex.split(cmd)
            if args[0] == "migrate":
                migrate.main(args=args[1:], prog_name="py-auto-migrate", standalone_mode=False)
            else:
                console.print(f"❌ [error]Unknown command: {escape(args[0])}[/error]")

        except Exception as e:
            console.print(f"⚠ [error]Error: {escape(str(e))}[/error]")

if __name__ == "__main__":
    repl()
