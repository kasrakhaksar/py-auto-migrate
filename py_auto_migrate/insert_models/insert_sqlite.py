import os
from py_auto_migrate.base_models.base_sqlite import BaseSQLite


class InsertSQLite(BaseSQLite):
    def __init__(self, sqlite_uri):
        if sqlite_uri.startswith("sqlite:///"):
            sqlite_uri = sqlite_uri.replace("sqlite:///", "", 1)
        os.makedirs(os.path.dirname(sqlite_uri), exist_ok=True)
        super().__init__(sqlite_uri)

    def insert(self, df, table_name):
        conn = self._connect()
        if conn is None:
            print(f"❌ Cannot connect to SQLite database. Insert aborted.")
            return

        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()
        print(f"✅ Inserted {len(df)} rows into SQLite table '{table_name}'")