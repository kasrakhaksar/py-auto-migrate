import click
import shlex
import os
from py_auto_migrate.cli import migrate


def repl():
    print("🚀 Welcome to Py-Auto-Migrate Shell")
    print("Type 'help' for usage, 'cls' to clear screen, or 'exit' to quit.\n")

    while True:
        try:
            cmd = input("py-auto-migrate> ").strip()
            if not cmd:
                continue

            if cmd in ["exit", "quit"]:
                print("👋 Exiting Py-Auto-Migrate.")
                break

            if cmd == "help":
                print("""
Available commands:
    migrate --source "<uri>" --target "<uri>" [--table <name>]
    cls / clear   -> Clear the screen
    exit / quit   -> Exit the shell
                      
note: [--table <name>] is optional

Examples:
    migrate --source "postgresql://user:pass@localhost:5432/db" --target "mysql://user:pass@localhost:3306/db"
    migrate --source "mongodb://localhost:27017/db" --target "sqlite:///C:/mydb.sqlite" --table "users"
""")
                continue

            if cmd in ["cls", "clear"]:
                os.system("cls" if os.name == "nt" else "clear")
                continue

            args = shlex.split(cmd)
            if args[0] == "migrate":
                migrate.main(args=args[1:], prog_name="py-auto-migrate", standalone_mode=False)
            else:
                print("❌ Unknown command:", args[0])

        except Exception as e:
            print("⚠ Error:", e)


if __name__ == "__main__":
    repl()
