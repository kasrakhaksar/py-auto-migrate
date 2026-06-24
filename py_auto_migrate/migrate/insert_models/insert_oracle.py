from py_auto_migrate.migrate.base_models.base_oracle import BaseOracle
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery
from py_auto_migrate.migrate.utils.type_mapper import sql_type_mapper

class InsertOracle(BaseOracle, BaseInsert):
    def __init__(self, oracle_uri):
        super().__init__(oracle_uri)

    def _ensure_schema(self, conn):
        try:
            cur = conn.cursor()

            cur.execute(
                "SELECT USER FROM dual"
            )

            return cur.fetchone()[0]

        except Exception:
            return None

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        conn = self._conn()

        if conn is None:
            return

        if data is None or data.empty:
            return

        try:
            cur = conn.cursor()

            self._ensure_schema(conn)

            columns = list(data.columns)
            column_defs = []

            for col, dtype in data.dtypes.items():
                sql_type = sql_type_mapper(
                    dtype,
                    "oracle"
                )

                column_defs.append(
                    f'"{col}" {sql_type}'
                )

            try:
                cur.execute(
                    f'''
                    CREATE TABLE "{table_name}"
                    (
                        {", ".join(column_defs)}
                    )
                    '''
                )

                conn.commit()

            except Exception:
                pass

            cur.execute(
                f'SELECT * FROM "{table_name}"'
            )

            existing_rows = set(
                cur.fetchall()
            )

            values = []
            seen = set()

            rows = list(
                data[columns]
                .itertuples(
                    index=False,
                    name=None
                )
            )

            for row in rows:
                if row not in existing_rows and row not in seen:
                    values.append(row)
                    seen.add(row)

            if values:
                placeholders = ", ".join(
                    [
                        f":{i+1}"
                        for i in range(len(columns))
                    ]
                )

                cur.executemany(
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
                    "oracle",
                    column_defs
                )

                generated_query = ai_query_obj.sql_generate(
                    model=ai_model
                )

                cur.execute(
                    generated_query
                )

                conn.commit()

        except Exception as e:
            print(e)

        finally:
            conn.close()