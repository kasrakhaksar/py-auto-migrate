import sqlite3
import json
from py_auto_migrate.migrate.base_models.base import BaseModel


class BaseSQLite(BaseModel):
    def __init__(self, sqlite_path):
        super().__init__(sqlite_path)

    def _connect(self):
        return sqlite3.connect(self.uri)

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
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM "{table_name}"')
        rows = cursor.fetchall()
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        columns = [col[1] for col in cursor.fetchall()]
        cursor.close()
        conn.close()
        data = [dict(zip(columns, row)) for row in rows]
        return json.dumps(data)