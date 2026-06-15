try:
    from py_auto_migrate.cli import get_uri
    from py_auto_migrate.migrate.mapping import MIGRATION_MAP

except:
    from ..cli import get_uri
    from ..migrate.mapping import MIGRATION_MAP



def execute_migration( source, target, table=None, ai_ask=None,ai_model=None):

    source_type = get_uri(source)
    target_type = get_uri(target)

    if not source_type:
        raise Exception("Invalid source URI")

    if not target_type:
        raise Exception("Invalid target URI")

    migration_class = MIGRATION_MAP.get((source_type, target_type))

    if not migration_class:
        raise Exception(
            f"Migration from {source_type} to {target_type} not supported"
        )

    migration = migration_class(source,target)

    if ai_ask and not ai_model:
        ai_model = "gpt-3.5-turbo"

    if ai_ask and table:
        migration.migrate_one( table, ai_ask,ai_model)

    elif ai_ask and not table:

        tables = migration.get_tables()

        for tbl in tables:
            migration.migrate_one( tbl, ai_ask, ai_model)

    elif table:
        migration.migrate_one(table)

    else:
        migration.migrate_all()

    return {
        "success": True
    }