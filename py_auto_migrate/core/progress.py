"""Thread-safe migration progress reporting."""

from dataclasses import asdict, dataclass
from threading import Lock
from typing import Callable

from py_auto_migrate.core.logging import get_logger


logger = get_logger(__name__)


@dataclass(frozen=True)
class ProgressSnapshot:
    status: str = "pending"
    total_tables: int = 0
    completed_tables: int = 0
    current_table: str | None = None
    current_table_index: int = 0
    current_table_total: int = 0
    current_table_processed: int = 0
    total_records: int = 0
    processed_records: int = 0
    errors: int = 0
    error_message: str | None = None

    @property
    def percent(self) -> float:
        if self.current_table_total <= 0:
            return 100.0 if self.status in {"completed", "completed_with_errors"} else 0.0
        return round(self.current_table_processed / self.current_table_total * 100, 2)

    def to_dict(self) -> dict:
        result = asdict(self)
        result["percent"] = self.percent
        return result


class ProgressTracker:
    """Report row-based progress to one or more consumers."""

    def __init__(self, on_update: Callable[[ProgressSnapshot], None] | None = None):
        self._lock = Lock()
        self._snapshot = ProgressSnapshot()
        self._on_update = on_update

    @property
    def snapshot(self) -> ProgressSnapshot:
        with self._lock:
            return self._snapshot

    def _publish(self, snapshot: ProgressSnapshot) -> None:
        if self._on_update:
            try:
                self._on_update(snapshot)
            except Exception:
                logger.exception("Progress callback failed")

    def _replace(self, **changes) -> None:
        with self._lock:
            snapshot = ProgressSnapshot(**{**asdict(self._snapshot), **changes})
            self._snapshot = snapshot
        self._publish(snapshot)

    def start(self, total_tables: int) -> None:
        self._replace(status="running", total_tables=total_tables)

    def start_table(self, table_name: str, total_records: int, table_index: int) -> None:
        self._replace(
            status="running",
            current_table=table_name,
            current_table_index=table_index,
            current_table_total=total_records,
            current_table_processed=0,
            total_records=self.snapshot.total_records + total_records,
        )

    def advance(self, records: int) -> None:
        snapshot = self.snapshot
        processed = min(
            snapshot.current_table_total,
            snapshot.current_table_processed + records,
        )
        self._replace(
            current_table_processed=processed,
            processed_records=snapshot.processed_records + records,
        )

    def complete_table(self, success: bool = True, error_message: str | None = None) -> None:
        snapshot = self.snapshot
        self._replace(
            current_table_processed=snapshot.current_table_total if success else snapshot.current_table_processed,
            completed_tables=snapshot.completed_tables + (1 if success else 0),
            errors=snapshot.errors + (0 if success else 1),
            error_message=error_message,
        )

    def finish(self) -> None:
        snapshot = self.snapshot
        self._replace(
            status="completed_with_errors" if snapshot.errors else "completed"
        )

    def fail(self, message: str) -> None:
        self._replace(status="failed", error_message=message)
