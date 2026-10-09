"""Application exceptions used across the CLI, dashboard and adapters."""


class PyAutoMigrateError(Exception):
    """Base class for expected application failures."""


class ConfigurationError(PyAutoMigrateError):
    """Invalid application or migration configuration."""


class InvalidURIError(ConfigurationError):
    """A database URI is missing or uses an unsupported scheme."""


class UnsupportedMigrationError(ConfigurationError):
    """The requested source/target combination is not supported."""


class ConnectionError(PyAutoMigrateError):
    """A source or target database connection could not be established."""


class SourceReadError(PyAutoMigrateError):
    """Reading metadata or data from a source database failed."""


class TargetWriteError(PyAutoMigrateError):
    """Writing data to a target database failed."""


class MigrationError(PyAutoMigrateError):
    """A migration operation failed."""


class AIQueryError(PyAutoMigrateError):
    """Generating or executing an AI-assisted query failed."""
