import click
from .migrator import MongoToMySQL, MongoToMongo , MySQLToMongo , MySQLToMySQL

@click.group()
def main():
    """Py-Auto-Migrate"""
    pass

@main.command()
@click.option('--source', required=True)
@click.option('--target', required=True)
@click.option('--table', required=False)
def migrate(source, target, table):
    if source.startswith("mongodb://") and target.startswith("mysql://"):
        m = MongoToMySQL(source, target)
        if table:
            m.migrate_one(table)
        else:
            m.migrate_all()

    elif source.startswith("mongodb://") and target.startswith("mongodb://"):
        m = MongoToMongo(source, target)
        if table:
            m.migrate_one(table)
        else:
            m.migrate_all()

    elif source.startswith("mysql://") and target.startswith("mysql://"):
        m = MySQLToMySQL(source, target)
        if table:
            m.migrate_one(table)
        else:
            m.migrate_all()

    elif source.startswith("mysql://") and target.startswith("mongodb://"):
        m = MySQLToMongo(source, target)
        if table:
            m.migrate_one(table)
        else:
            m.migrate_all()


    else:
        click.echo("❌ Migration type not supported.")

if __name__ == "__main__":
    main()
