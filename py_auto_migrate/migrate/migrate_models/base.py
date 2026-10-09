import datetime
import json
import math
from collections import Counter
from decimal import Decimal
from typing import Any, Type
from uuid import UUID

import numpy as np
import pandas as pd
from bson.decimal128 import Decimal128
from py_auto_migrate.migrate.utils.type_mapper import normalize_datetime
from py_auto_migrate.core.logging import get_logger
from py_auto_migrate.core.progress import ProgressTracker


logger = get_logger(__name__)
PROGRESS_BATCH_SIZE = 1000


class BaseMigration:
    """Coordinate a migration between a source adapter and a target writer."""

    def __init__(
        self,
        source_class: Type[Any],
        target_class: Type[Any],
        source_uri: str,
        target_uri: str,
        progress: ProgressTracker | None = None,
        skip_existing: bool = False,
        progress_batch_size: int | None = PROGRESS_BATCH_SIZE,
    ):
        self.source_uri = source_uri
        self.target_uri = target_uri
        self.source = source_class(source_uri)
        self.inserter = target_class(target_uri)
        self.progress = progress
        self.skip_existing = skip_existing
        if progress_batch_size is not None and progress_batch_size <= 0:
            raise ValueError("progress_batch_size must be positive or None")
        self.progress_batch_size = progress_batch_size
        self._target_tables_cache: set[str] | None = None
        self.summary = {
            "tables_total": 0,
            "tables_succeeded": 0,
            "tables_failed": 0,
            "tables_empty": 0,
            "tables_already_present": 0,
            "rows_read": 0,
            "rows_submitted": 0,
            "rows_skipped_existing": 0,
            "table_results": [],
        }

    def read_table(self, table_name: str) -> Any:
        return self.source.read_table(table_name)

    def get_tables(self) -> list:
        return self.source.get_tables()

    
    def get_foreignkey_dependencies(self, table_name: str) -> list[str]:
        return self.source.get_foreignkey_dependencies(table_name)
    
        

    def migrate_one(
        self,
        table_name: str,
        ai_ask=None,
        ai_model=None,
        dep=False,
        _table_index: int = 1,
        _finish_progress: bool = True,
    ) -> None:
        self._migrate_dataframe(
            table_name,
            self.read_table(table_name),
            ai_ask,
            ai_model,
            _table_index,
        )

        if dep:
            for rel_table in self.get_foreignkey_dependencies(table_name):
                self._migrate_dataframe(
                    rel_table,
                    self.read_table(rel_table),
                    table_index=_table_index,
                )

        if self.progress and _finish_progress:
            self.progress.finish()

    def _migrate_dataframe(
        self,
        table_name: str,
        df: Any,
        ai_ask=None,
        ai_model=None,
        table_index: int = 1,
    ) -> None:
        self.summary["tables_total"] += 1
        if df is None or df.empty:
            logger.warning("No data returned for table '%s'", table_name)
            self.summary["tables_empty"] += 1
            self.summary["table_results"].append({
                "table": table_name,
                "status": "empty",
                "rows_read": 0,
                "rows_submitted": 0,
                "error": None,
            })
            if self.progress:
                self.progress.start_table(table_name, 0, table_index)
                self.progress.complete_table()
            return

        df = normalize_datetime(df)
        row_count = len(df)
        self.summary["rows_read"] += row_count
        submitted_before = self.summary["rows_submitted"]

        rows_skipped = 0
        if self.skip_existing:
            df, rows_skipped = self._remove_rows_already_in_target(table_name, df)
            self.summary["rows_skipped_existing"] += rows_skipped

        if df.empty:
            logger.info(
                "All %s source rows for '%s' are already present in the target",
                rows_skipped,
                table_name,
            )
            self.summary["tables_already_present"] += 1
            self.summary["table_results"].append({
                "table": table_name,
                "status": "already_present",
                "rows_read": row_count,
                "rows_submitted": 0,
                "rows_skipped_existing": rows_skipped,
                "error": None,
            })
            if self.progress:
                self.progress.start_table(table_name, 0, table_index)
                self.progress.complete_table()
            return

        if self.progress:
            self.progress.start_table(table_name, len(df), table_index)

        logger.info("Migrating table '%s'", table_name)
        migrate_state = self._write_dataframe(
            df, table_name, ai_ask, ai_model
        )
        if migrate_state is True:
            logger.info("Completed table '%s'", table_name)
            self.summary["tables_succeeded"] += 1
            self.summary["table_results"].append({
                "table": table_name,
                "status": "succeeded",
                "rows_read": row_count,
                "rows_submitted": self.summary["rows_submitted"] - submitted_before,
                "rows_skipped_existing": rows_skipped,
                "error": None,
            })
            if self.progress:
                self.progress.complete_table()
            if self._target_tables_cache is not None:
                self._target_tables_cache.add(table_name)
        else:
            logger.error("Target writer reported a failure for table '%s'", table_name)
            self.summary["tables_failed"] += 1
            self.summary["table_results"].append({
                "table": table_name,
                "status": "failed",
                "rows_read": row_count,
                "rows_submitted": self.summary["rows_submitted"] - submitted_before,
                "rows_skipped_existing": rows_skipped,
                "error": f"Failed to write table '{table_name}'",
            })
            if self.progress:
                self.progress.complete_table(False, f"Failed to write table '{table_name}'")

    @staticmethod
    def _canonical_row(row: dict) -> str:
        """Build a stable key for comparing records across database drivers."""
        def normalize(value):
            if value is None or value is pd.NA or value is pd.NaT:
                return None
            if isinstance(value, np.generic):
                return normalize(value.item())
            if isinstance(value, float) and math.isnan(value):
                return None
            if isinstance(value, pd.Timestamp):
                return {"$datetime": value.isoformat()}
            if isinstance(value, datetime.datetime):
                return {"$datetime": value.isoformat()}
            if isinstance(value, datetime.date):
                return {"$datetime": datetime.datetime.combine(value, datetime.time.min).isoformat()}
            if isinstance(value, datetime.time):
                return value.isoformat()
            if isinstance(value, datetime.timedelta):
                return str(value)
            if isinstance(value, Decimal):
                if value.is_nan():
                    return None
                return {"$decimal": str(value)}
            if isinstance(value, Decimal128):
                decimal_value = value.to_decimal()
                if decimal_value.is_nan():
                    return None
                return {"$decimal": str(decimal_value)}
            if isinstance(value, UUID):
                return str(value)
            if isinstance(value, bytes):
                return {"$bytes": value.hex()}
            if isinstance(value, dict):
                return {str(key): normalize(item) for key, item in value.items()}
            if isinstance(value, (list, tuple)):
                return [normalize(item) for item in value]
            try:
                missing = pd.isna(value)
                if isinstance(missing, (bool, np.bool_)) and missing:
                    return None
            except (TypeError, ValueError):
                pass
            return value

        return json.dumps(normalize(row), sort_keys=True, separators=(",", ":"), default=str)

    def _remove_rows_already_in_target(self, table_name: str, source_df: Any):
        """Skip only the number of exact source-row copies already in target.

        A multiset count preserves duplicate rows that occur more often in the
        source than in the target, unlike set-based deduplication.
        """
        if self._target_tables_cache is None:
            self._target_tables_cache = set(self.inserter.get_tables())
        if table_name not in self._target_tables_cache:
            return source_df, 0

        target_df = self.inserter.read_table(table_name)
        if target_df is None or target_df.empty:
            return source_df, 0

        target_df = normalize_datetime(target_df)
        target_df = target_df.reindex(columns=source_df.columns)
        existing_counts = Counter(
            self._canonical_row(row.to_dict())
            for _, row in target_df.iterrows()
        )

        keep_indexes = []
        skipped = 0
        for index, row in source_df.iterrows():
            row_key = self._canonical_row(row.to_dict())
            if existing_counts[row_key] > 0:
                existing_counts[row_key] -= 1
                skipped += 1
            else:
                keep_indexes.append(index)

        return source_df.loc[keep_indexes], skipped


    def migrate_all(self , ai_ask=None, ai_model=None , dep=False) -> None:

        tables = self.get_tables()

        if self.progress:
            self.progress.start(len(tables))

        for i, table_name in enumerate(tables, 1):
            logger.info("Migration progress [%s/%s]: %s", i, len(tables), table_name)
            self.migrate_one(
                table_name,
                ai_ask,
                ai_model,
                dep,
                _table_index=i,
                _finish_progress=False,
            )

        if self.progress:
            self.progress.finish()

    def _write_dataframe(self, df, table_name, ai_ask=None, ai_model=None):
        """Write once by default; optionally batch for finer progress updates."""
        batch_size = self.progress_batch_size if self.progress else None
        if batch_size is None:
            state = self.inserter.insert(df, table_name, ai_ask, ai_model)
            if state is True:
                self.summary["rows_submitted"] += len(df)
                if self.progress:
                    self.progress.advance(len(df))
            return state

        total_rows = len(df)
        for start in range(0, total_rows, batch_size):
            end = min(start + batch_size, total_rows)
            is_last_batch = end == total_rows
            state = self.inserter.insert(
                df.iloc[start:end],
                table_name,
                ai_ask if is_last_batch else None,
                ai_model if is_last_batch else None,
            )
            if state is not True:
                return False
            self.summary["rows_submitted"] += end - start
            self.progress.advance(end - start)

        return True
