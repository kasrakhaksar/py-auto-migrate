import os
import json
import sqlite3
from py_auto_migrate.migrate.base_models.base_sqlite import BaseSQLite
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery


class InsertSQLite(BaseSQLite, BaseInsert):
    def __init__(self, sqlite_uri):
        if sqlite_uri.startswith("sqlite:///"):
            sqlite_uri = sqlite_uri.replace("sqlite:///", "", 1)

        self.sqlite_path = sqlite_uri
        os.makedirs(os.path.dirname(self.sqlite_path), exist_ok=True)
        super().__init__(self.sqlite_path)

    def _connect(self):
        return sqlite3.connect(self.sqlite_path)

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        conn = self._connect()
        if conn is None:
            return

        try:
            if isinstance(data, str):
                data = json.loads(data)

            if not data:
                return

            columns = list(data[0].keys())
            column_defs = []

            for col in columns:
                sample_value = data[0][col]

                if isinstance(sample_value, int):
                    col_type = "INTEGER"
                elif isinstance(sample_value, float):
                    col_type = "REAL"
                else:
                    col_type = "TEXT"

                column_defs.append(f'"{col}" {col_type}')

            cursor = conn.cursor()

            cursor.execute(
                f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(column_defs)})'
            )

            cursor.execute(f'SELECT * FROM "{table_name}"')
            existing_rows = set(cursor.fetchall())

            values = []
            seen = set()

            for row in data:
                row_tuple = tuple(row[col] for col in columns)

                if row_tuple not in existing_rows and row_tuple not in seen:
                    values.append(row_tuple)
                    seen.add(row_tuple)

            if values:
                placeholders = ", ".join(["?"] * len(columns))

                cursor.executemany(
                    f'INSERT INTO "{table_name}" VALUES ({placeholders})',
                    values
                )

                conn.commit()

            if ai_ask and ai_model:
                ai_query_obj = AIQuery(ai_ask, table_name, "sqlite", column_defs)
                generated_query = ai_query_obj.sql_generate(model=ai_model)

                try:
                    cursor.execute(generated_query)
                    conn.commit()
                except Exception as e:
                    print(f"Error executing AI query: {e}")
                    raise

        finally:
            conn.close()