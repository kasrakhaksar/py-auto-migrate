import json
import pyodbc
from py_auto_migrate.migrate.base_models.base_mssql import BaseMSSQL
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery


class InsertMSSQL(BaseMSSQL, BaseInsert):
    def __init__(self, mssql_uri):
        self.mssql_uri = mssql_uri
        self._ensure_database()
        super().__init__(mssql_uri)

    def _ensure_database(self):
        conn = self._connect()

        try:
            cur = conn.cursor()

            db_name = conn.getinfo(pyodbc.SQL_DATABASE_NAME)

            cur.execute(f"""
                IF NOT EXISTS (
                    SELECT name FROM sys.databases WHERE name = '{db_name}'
                )
                BEGIN
                    CREATE DATABASE [{db_name}]
                END
            """)

            conn.commit()

        finally:
            conn.close()

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        conn = self._connect()
        if conn is None:
            return

        try:
            if isinstance(data, str):
                data = json.loads(data)

            if not data:
                return

            cur = conn.cursor()

            cur.execute(f"""
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_NAME = '{table_name}'
            """)

            table_exists = cur.fetchone()[0] > 0

            columns = list(data[0].keys())
            column_defs = []

            if not table_exists:
                for col, val in data[0].items():
                    if isinstance(val, bool):
                        col_type = "BIT"
                    elif isinstance(val, int):
                        col_type = "BIGINT"
                    elif isinstance(val, float):
                        col_type = "FLOAT"
                    else:
                        col_type = "NVARCHAR(MAX)"

                    column_defs.append(f"[{col}] {col_type}")

                cur.execute(
                    f"CREATE TABLE [{table_name}] ({', '.join(column_defs)})"
                )
                conn.commit()

                existing_rows = set()

            else:
                cur.execute(f"SELECT * FROM [{table_name}]")
                existing_rows = set(cur.fetchall())

            values = []
            seen = set()

            for row in data:
                row_tuple = tuple(row[col] for col in columns)

                if row_tuple not in existing_rows and row_tuple not in seen:
                    values.append(row_tuple)
                    seen.add(row_tuple)

            if values:
                placeholders = ", ".join(["?"] * len(columns))

                cur.fast_executemany = True
                cur.executemany(
                    f"INSERT INTO [{table_name}] VALUES ({placeholders})",
                    values
                )
                conn.commit()

            if ai_ask and ai_model:
                ai_query_obj = AIQuery(
                    ai_ask,
                    table_name,
                    "mssql",
                    column_defs if not table_exists else columns,
                )

                generated_query = ai_query_obj.sql_generate(model=ai_model)

                try:
                    cur.execute(generated_query)
                    conn.commit()
                except Exception as e:
                    print(f"Error executing AI query: {e}")
                    raise

        finally:
            conn.close()