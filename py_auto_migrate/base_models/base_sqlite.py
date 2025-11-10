import sqlite3
import pandas as pd


class BaseSQLite:
    def __init__(self, sqlite_path):
        self.sqlite_path = sqlite_path

    def _connect(self):
        return sqlite3.connect(self.sqlite_path)

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
        df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)
        conn.close()
        if df.empty:
            print(f"❌ Table '{table_name}' is empty.")
        return df.fillna(0)
