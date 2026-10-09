try:
    from py_auto_migrate.cli import get_uri
    from py_auto_migrate.migrate.mapping import MIGRATION_MAP
    from py_auto_migrate.core.exceptions import InvalidURIError, UnsupportedMigrationError

except ImportError:
    from ..cli import get_uri
    from ..migrate.mapping import MIGRATION_MAP
    from ..core.exceptions import InvalidURIError, UnsupportedMigrationError



def execute_migration(
    source,
    target,
    table=None,
    ai_ask=None,
    ai_model=None,
    progress=None,
    skip_existing=False,
    progress_batch_size=None,
):

    source_type = get_uri(source)
    target_type = get_uri(target)

    if not source_type:
        raise InvalidURIError("Invalid source URI")

    if not target_type:
        raise InvalidURIError("Invalid target URI")

    migration_class = MIGRATION_MAP.get((source_type, target_type))

    if not migration_class:
        raise UnsupportedMigrationError(
            f"Migration from {source_type} to {target_type} not supported"
        )

    migration = migration_class(
        source,
        target,
        progress=progress,
        skip_existing=skip_existing,
        progress_batch_size=progress_batch_size,
    )

    if ai_ask and not ai_model:
        ai_model = "gpt-3.5-turbo"

    if table:
        migration.migrate_one(table, ai_ask, ai_model)
    else:
        migration.migrate_all(ai_ask, ai_model)

    return {
        "success": True,
        "summary": migration.summary,
    }
