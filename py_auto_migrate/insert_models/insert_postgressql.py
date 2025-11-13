from py_auto_migrate.base_models.base_postgressql import BasePostgresSQL
from py_auto_migrate.utils.helpers import map_dtype_to_postgres


class InsertPostgresSQL(BasePostgresSQL):
    def __init__(self, pg_uri):
        super().__init__(pg_uri)

    def insert(self, df, table_name):
        conn = self._connect()
        if conn is None:
            print(f"❌ Cannot connect to PostgreSQL database. Insert aborted.")
            return

        cur = conn.cursor()

        cur.execute("SELECT to_regclass(%s)", (table_name,))
        if cur.fetchone()[0]:
            print(f"⚠ Table '{table_name}' already exists in PostgreSQL. Skipping insert.")
            conn.close()
            return

        columns = ', '.join([f'"{col}" {map_dtype_to_postgres(df[col].dtype)}' for col in df.columns])
        cur.execute(f'CREATE TABLE "{table_name}" ({columns})')

        placeholders = ', '.join(['%s'] * len(df.columns))
        values = [tuple(row) for row in df.to_numpy()]
        cur.executemany(f'INSERT INTO "{table_name}" VALUES ({placeholders})', values)

        conn.commit()
        conn.close()
        print(f"✅ Inserted {len(df)} rows into PostgreSQL table '{table_name}'")