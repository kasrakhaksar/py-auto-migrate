import pyodbc
from py_auto_migrate.migrate.base_models.base_mssql import BaseMSSQL
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery
from py_auto_migrate.migrate.utils.type_mapper import sql_type_mapper


class InsertMSSQL(BaseMSSQL, BaseInsert):

    def __init__(self, mssql_uri):
        super().__init__(mssql_uri)
        self._ensure_database()

    def _ensure_database(self):

        cfg = self._parse_mssql_uri()
        db_name = cfg["database"]

        if cfg["auth"] == "windows":

            conn_str = (
                "DRIVER={ODBC Driver 18 for SQL Server};"
                f"SERVER={cfg['host']},{cfg['port']};"
                "DATABASE=master;"
                "Trusted_Connection=yes;"
                "Encrypt=no;"
                "TrustServerCertificate=yes;"
            )

        else:

            conn_str = (
                "DRIVER={ODBC Driver 18 for SQL Server};"
                f"SERVER={cfg['host']},{cfg['port']};"
                "DATABASE=master;"
                f"UID={cfg['user']};"
                f"PWD={cfg['password']};"
                "Encrypt=no;"
                "TrustServerCertificate=yes;"
            )

        conn = pyodbc.connect(conn_str, autocommit=True)

        try:

            cur = conn.cursor()

            cur.execute(
                "SELECT DB_ID(?)",
                (db_name,)
            )

            exists = cur.fetchone()[0]

            if exists is None:
                cur.execute(f"CREATE DATABASE [{db_name}]")

        finally:
            conn.close()

    def insert(self, data, table_name, ai_ask=None, ai_model=None):

        conn = self._connect()

        if conn is None:
            return

        try:

            cur = conn.cursor()

            cur.execute(
                f"""
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_NAME = '{table_name}'
                """
            )

            table_exists = cur.fetchone()[0] > 0

            columns = list(data.columns)
            column_defs = []

            if not table_exists:

                for col, dtype in data.dtypes.items():

                    sql_type = sql_type_mapper(
                        dtype,
                        "mssql"
                    )

                    column_defs.append(
                        f"[{col}] {sql_type}"
                    )

                cur.execute(
                    f"""
                    CREATE TABLE [{table_name}]
                    (
                        {', '.join(column_defs)}
                    )
                    """
                )

                conn.commit()
                existing_rows = set()

            else:

                cur.execute(
                    f"SELECT * FROM [{table_name}]"
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
                    ["?"] * len(columns)
                )

                cur.fast_executemany = True

                cur.executemany(
                    f"""
                    INSERT INTO [{table_name}]
                    VALUES ({placeholders})
                    """,
                    values
                )

                conn.commit()

            if ai_ask and ai_model:

                ai_query_obj = AIQuery(
                    ai_ask,
                    table_name,
                    "mssql",
                    column_defs if not table_exists else columns
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
