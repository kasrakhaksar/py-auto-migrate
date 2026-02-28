from py_auto_migrate.base_models.base_postgressql import BasePostgresSQL
from py_auto_migrate.utils.helpers import map_dtype_to_postgres
from py_auto_migrate.insert_models.base import BaseInsert


class InsertPostgresSQL(BasePostgresSQL, BaseInsert):
    def __init__(self, pg_uri):
        super().__init__(pg_uri)

    def insert(self, df, table_name):
        conn = self._connect()
        if conn is None:
            return

        cur = conn.cursor()

        cur.execute("SELECT to_regclass(%s)", (table_name,))
        if cur.fetchone()[0]:
            conn.close()
            return

        columns = ', '.join([f'"{col}" {map_dtype_to_postgres(df[col].dtype)}' for col in df.columns])
        cur.execute(f'CREATE TABLE "{table_name}" ({columns})')

        placeholders = ', '.join(['%s'] * len(df.columns))
        values = [tuple(row) for row in df.to_numpy()]
        cur.executemany(f'INSERT INTO "{table_name}" VALUES ({placeholders})', values)

        conn.commit()
        conn.close()