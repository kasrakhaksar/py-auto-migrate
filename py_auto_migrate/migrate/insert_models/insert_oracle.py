from py_auto_migrate.migrate.base_models.base_oracle import BaseOracle
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery
from py_auto_migrate.migrate.utils.type_mapper import sql_type_mapper


class InsertOracle(BaseOracle, BaseInsert):
    def __init__(self, oracle_uri):
        super().__init__(oracle_uri)

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        conn = self._connect()

        if conn is None:
            return

        try:
            cur = conn.cursor()

            cur.execute(
                """
                SELECT COUNT(*)
                FROM USER_TABLES
                WHERE TABLE_NAME = :1
                """,
                (table_name.upper(),)
            )

            table_exists = cur.fetchone()[0] > 0

            columns = list(data.columns)
            column_defs = []

            if not table_exists:
                for col, dtype in data.dtypes.items():
                    sql_type = sql_type_mapper(
                        dtype,
                        "oracle"
                    )

                    column_defs.append(
                        f'"{col}" {sql_type}'
                    )

                cur.execute(
                    f'''
                    CREATE TABLE "{table_name}"
                    (
                        {", ".join(column_defs)}
                    )
                    '''
                )

                conn.commit()

                values = list(
                    data[columns].itertuples(
                        index=False,
                        name=None
                    )
                )

            else:
                cur.execute(
                    f'SELECT * FROM "{table_name}"'
                )

                existing_rows = set(
                    cur.fetchall()
                )

                values = []
                seen = set()

                rows = list(
                    data[columns].itertuples(
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
                    f":{i+1}"
                    for i in range(len(columns))
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
                    column_defs if column_defs else columns
                )

                generated_query = ai_query_obj.sql_generate(
                    model=ai_model
                )

                cur.execute(generated_query)

                conn.commit()

        except Exception as e:
            print(e)
            return False

        finally:
            conn.close()
            
        return True