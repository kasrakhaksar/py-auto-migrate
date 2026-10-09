"""Database adapter registry and migration factory.

Register a backend once with its URI prefix, source adapter, target writer, and
capabilities. The migration matrix is derived from that registry, so adding a
backend does not require maintaining a second source/target map or enumerating
every source/target pair.
"""

from dataclasses import dataclass
from functools import partial
from typing import Any, Callable, Type

from py_auto_migrate.migrate.base_models.base_clickhouse import BaseClickHouse
from py_auto_migrate.migrate.base_models.base_dynamodb import BaseDynamoDB
from py_auto_migrate.migrate.base_models.base_elasticsearch import BaseElasticsearch
from py_auto_migrate.migrate.base_models.base_mariadb import BaseMariaDB
from py_auto_migrate.migrate.base_models.base_mongodb import BaseMongoDB
from py_auto_migrate.migrate.base_models.base_mssql import BaseMSSQL
from py_auto_migrate.migrate.base_models.base_mysql import BaseMySQL
from py_auto_migrate.migrate.base_models.base_oracle import BaseOracle
from py_auto_migrate.migrate.base_models.base_postgressql import BasePostgresSQL
from py_auto_migrate.migrate.base_models.base_redis import BaseRedis
from py_auto_migrate.migrate.base_models.base_sqlite import BaseSQLite

from py_auto_migrate.migrate.insert_models.insert_clickhouse import InsertClickHouse
from py_auto_migrate.migrate.insert_models.insert_dynamodb import InsertDynamoDB
from py_auto_migrate.migrate.insert_models.insert_elasticsearch import InsertElasticsearch
from py_auto_migrate.migrate.insert_models.insert_mariadb import InsertMariaDB
from py_auto_migrate.migrate.insert_models.insert_mongodb import InsertMongoDB
from py_auto_migrate.migrate.insert_models.insert_mssql import InsertMSSQL
from py_auto_migrate.migrate.insert_models.insert_mysql import InsertMySQL
from py_auto_migrate.migrate.insert_models.insert_oracle import InsertOracle
from py_auto_migrate.migrate.insert_models.insert_postgressql import InsertPostgresSQL
from py_auto_migrate.migrate.insert_models.insert_redis import InsertRedis
from py_auto_migrate.migrate.insert_models.insert_sqlite import InsertSQLite
from py_auto_migrate.migrate.migrate_models.base import BaseMigration


@dataclass(frozen=True)
class DatabaseAdapter:
    """One backend's read/write adapters and optional migration capabilities."""

    uri_prefix: str
    source: Type[Any]
    target: Type[Any]
    ai_supported: bool = False
    dependencies_supported: bool = False


DATABASES: dict[str, DatabaseAdapter] = {}

# These public dictionaries/lists are retained for compatibility with callers
# that imported the previous registry constants.
SOURCE_ADAPTERS: dict[str, Type[Any]] = {}
TARGET_WRITERS: dict[str, Type[Any]] = {}
ALL_DATABASES_LIST: list[str] = []
AI_SUPPORTED_DATABASES: list[str] = []
DEP_SUPPORTED_DATABASES: list[str] = []
MIGRATION_MAP: dict[tuple[str, str], Callable[..., BaseMigration]] = {}


def _migration_factory(source_type: str, target_type: str) -> Callable:
    """Return the existing ``(source_uri, target_uri)`` constructor shape."""
    return partial(
        BaseMigration,
        SOURCE_ADAPTERS[source_type],
        TARGET_WRITERS[target_type],
    )


def register_database(
    uri_prefix: str,
    source: Type[Any],
    target: Type[Any],
    *,
    ai_supported: bool = False,
    dependencies_supported: bool = False,
) -> None:
    """Register a backend and rebuild only the migration routes involving it."""
    normalized_prefix = uri_prefix.lower()
    if not normalized_prefix.endswith("://"):
        normalized_prefix += "://"
    if normalized_prefix in DATABASES:
        raise ValueError(f"Database URI prefix already registered: {normalized_prefix}")

    adapter = DatabaseAdapter(
        uri_prefix=normalized_prefix,
        source=source,
        target=target,
        ai_supported=ai_supported,
        dependencies_supported=dependencies_supported,
    )
    DATABASES[normalized_prefix] = adapter
    SOURCE_ADAPTERS[normalized_prefix] = source
    TARGET_WRITERS[normalized_prefix] = target
    ALL_DATABASES_LIST.append(normalized_prefix)
    if ai_supported:
        AI_SUPPORTED_DATABASES.append(normalized_prefix)
    if dependencies_supported:
        DEP_SUPPORTED_DATABASES.append(normalized_prefix)

    for registered_source in ALL_DATABASES_LIST:
        MIGRATION_MAP[(registered_source, normalized_prefix)] = _migration_factory(
            registered_source, normalized_prefix
        )
        MIGRATION_MAP[(normalized_prefix, registered_source)] = _migration_factory(
            normalized_prefix, registered_source
        )


register_database("mongodb://", BaseMongoDB, InsertMongoDB)
register_database("mysql://", BaseMySQL, InsertMySQL, ai_supported=True, dependencies_supported=True)
register_database("mariadb://", BaseMariaDB, InsertMariaDB, ai_supported=True, dependencies_supported=True)
register_database("postgresql://", BasePostgresSQL, InsertPostgresSQL, ai_supported=True, dependencies_supported=True)
register_database("mssql://", BaseMSSQL, InsertMSSQL, ai_supported=True, dependencies_supported=True)
register_database("oracle://", BaseOracle, InsertOracle, ai_supported=True, dependencies_supported=True)
register_database("redis://", BaseRedis, InsertRedis)
register_database("dynamodb://", BaseDynamoDB, InsertDynamoDB)
register_database("elasticsearch://", BaseElasticsearch, InsertElasticsearch)
register_database("sqlite://", BaseSQLite, InsertSQLite, ai_supported=True, dependencies_supported=True)
register_database("clickhouse://", BaseClickHouse, InsertClickHouse, ai_supported=True)
