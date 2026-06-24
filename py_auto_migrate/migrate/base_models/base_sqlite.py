import pandas as pd
import sqlite3
from py_auto_migrate.migrate.base_models.base import BaseModel


class BaseSQLite(BaseModel):

    def __init__(self, sqlite_path):
        super().__init__(sqlite_path)

    def _connect(self):
        return sqlite3.connect(
            self.uri
        )

    def get_tables(self):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()
        return tables


    def read_table(self, table_name):
        conn = self._connect()
        df = pd.read_sql_query(f'SELECT * FROM "{table_name}"',conn)
        conn.close()

        return df
    
    def get_foreignkey_dependencies(self, table_name: str) -> list[str]:
        conn = self._connect()

        if conn is None:
            return []

        try:
            cursor = conn.cursor()

            cursor.execute(f"PRAGMA foreign_key_list('{table_name}')")

            return list({
                row[2]
                for row in cursor.fetchall()
            })

        finally:
            cursor.close()
            conn.close()