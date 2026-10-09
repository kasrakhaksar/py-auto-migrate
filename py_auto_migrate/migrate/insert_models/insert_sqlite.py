import os
import sqlite3
from py_auto_migrate.migrate.base_models.base_sqlite import BaseSQLite
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery
from py_auto_migrate.migrate.utils.type_mapper import sql_type_mapper , sqlite_value_mapper
from py_auto_migrate.core.logging import get_logger

logger = get_logger(__name__)

class InsertSQLite(BaseSQLite, BaseInsert):
    def __init__(self, sqlite_uri):
        if sqlite_uri.startswith("sqlite:///"):
            sqlite_uri = sqlite_uri.replace("sqlite:///","",1)

        self.sqlite_path = sqlite_uri

        folder = os.path.dirname(
            self.sqlite_path
        )

        if folder:
            os.makedirs(
                folder,
                exist_ok=True
            )

        super().__init__(
            self.sqlite_path
        )

    def _connect(self):
        return sqlite3.connect(
            self.sqlite_path
        )

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        conn = self._connect()

        if conn is None:
            return

        try:
            columns = list(data.columns)

            column_defs = []

            for col, dtype in data.dtypes.items():
                sql_type = sql_type_mapper(
                    dtype,
                    "sqlite"
                )

                column_defs.append(
                    f'"{col}" {sql_type}'
                )

            cursor = conn.cursor()

            cursor.execute(
                f'''
                CREATE TABLE IF NOT EXISTS "{table_name}"
                (
                    {", ".join(column_defs)}
                )
                '''
            )

            rows = [
                tuple(
                    sqlite_value_mapper(value)
                    for value in row
                )
                for row in data[columns].itertuples(
                    index=False,
                    name=None
                )
            ]

            values = rows

            if values:
                placeholders = ", ".join(
                    ["?"] * len(columns)
                )

                cursor.executemany(
                    f'''
                    INSERT INTO "{table_name}"
                    VALUES ({placeholders})
                    ''',
                    values
                )

                conn.commit()

            if ai_ask and ai_model:
                ai_query_obj = AIQuery(
                    ai_ask,
                    table_name,
                    "sqlite",
                    column_defs
                )

                generated_query = ai_query_obj.sql_generate(
                    model=ai_model
                )

                cursor.execute(
                    generated_query
                )

                conn.commit()

        except Exception as e:
            logger.exception("Failed to insert data into SQLite table '%s'", table_name)
            return False

        finally:
            conn.close()

        return True
