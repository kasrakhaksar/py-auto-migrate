import json
from py_auto_migrate.migrate.base_models.base_oracle import BaseOracle
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery


class InsertOracle(BaseOracle, BaseInsert):
    def __init__(self, oracle_uri):
        super().__init__(oracle_uri)

    def _ensure_schema(self, conn):
        try:
            cur = conn.cursor()
            cur.execute("SELECT USER FROM dual")
            return cur.fetchone()[0]
        except Exception:
            return None

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        conn = self._conn()
        if conn is None:
            return

        try:
            if isinstance(data, str):
                data = json.loads(data)

            if not data:
                return

            cur = conn.cursor()

            schema = self._ensure_schema(conn)

            sample = data[0]
            columns = list(sample.keys())

            column_defs = []

            for col, val in sample.items():
                if isinstance(val, bool):
                    col_type = "NUMBER(1)"
                elif isinstance(val, int):
                    col_type = "NUMBER"
                elif isinstance(val, float):
                    col_type = "FLOAT"
                else:
                    col_type = "NVARCHAR2(4000)"

                column_defs.append(f'"{col}" {col_type}')

            try:
                cur.execute(
                    f'CREATE TABLE "{table_name}" ({", ".join(column_defs)})'
                )
                conn.commit()
            except Exception:
                pass

            cur.execute(f'SELECT * FROM "{table_name}"')
            existing_rows = set(cur.fetchall())

            values = []
            seen = set()

            placeholders = ", ".join([f":{i+1}" for i in range(len(columns))])

            for row in data:
                row_tuple = tuple(row[col] for col in columns)

                if row_tuple not in existing_rows and row_tuple not in seen:
                    values.append(row_tuple)
                    seen.add(row_tuple)

            if values:
                cur.executemany(
                    f'INSERT INTO "{table_name}" VALUES ({placeholders})',
                    values
                )
                conn.commit()

            if ai_ask and ai_model:
                ai_query_obj = AIQuery(ai_ask, table_name, "oracle", column_defs)
                generated_query = ai_query_obj.sql_generate(model=ai_model)

                try:
                    cur.execute(generated_query)
                    conn.commit()
                except Exception as e:
                    print(f"Error executing AI query: {e}")
                    raise

        finally:
            conn.close()