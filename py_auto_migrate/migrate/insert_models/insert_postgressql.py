import psycopg2
from urllib.parse import urlparse
from py_auto_migrate.migrate.base_models.base_postgressql import BasePostgresSQL
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery
from py_auto_migrate.migrate.utils.type_mapper import sql_type_mapper

class InsertPostgresSQL(BasePostgresSQL, BaseInsert):
    def __init__(self, pg_uri):
        self.pg_uri = pg_uri
        self._ensure_database()
        super().__init__(pg_uri)

    def _ensure_database(self):
        parsed = urlparse(self.pg_uri)

        db_name = parsed.path.lstrip("/")

        base_uri = self.pg_uri.replace(
            f"/{db_name}",
            "/postgres"
        )

        conn = psycopg2.connect(base_uri)
        conn.autocommit = True

        cur = conn.cursor()

        cur.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )

        exists = cur.fetchone()

        if not exists:
            cur.execute(
                f'CREATE DATABASE "{db_name}"'
            )

        cur.close()
        conn.close()

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        conn = self._connect()

        if conn is None:
            return

        try:
            cur = conn.cursor()

            cur.execute(
                "SELECT to_regclass(%s)",
                (table_name,)
            )

            table_exists = cur.fetchone()[0] is not None

            columns = list(data.columns)
            column_defs = []
            
            if not table_exists:
                for col, dtype in data.dtypes.items():
                    sql_type = sql_type_mapper(
                        dtype,
                        "postgresql"
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
                    data[columns]
                    .itertuples(
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
                    ["%s"] * len(columns)
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
                    "postgresql",
                    column_defs if column_defs else columns
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
            return False

        finally:
            conn.close()

        return True