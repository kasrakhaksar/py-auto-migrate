import pandas as pd
import pymysql
from py_auto_migrate.migrate.base_models.base_mysql import BaseMySQL
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery
from py_auto_migrate.migrate.utils.type_mapper import sql_type_mapper

class InsertMySQL(BaseMySQL, BaseInsert):
    def __init__(self, mysql_uri):
        self.mysql_uri = mysql_uri
        self._ensure_database()
        super().__init__(mysql_uri)

    def _ensure_database(self):
        host, port, user, password, db_name = self._parse_mysql_uri()

        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )

        cursor = conn.cursor()

        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{db_name}`"
        )

        conn.commit()
        conn.close()

    def insert(self, data: pd.DataFrame, table_name, ai_ask=None, ai_model=None):
        conn = self._connect()

        if conn is None:
            return

        if data is None or data.empty:
            return

        try:
            cursor = conn.cursor()

            cursor.execute(
                f"SHOW TABLES LIKE '{table_name}'"
            )

            table_exists = cursor.fetchone() is not None

            columns = list(data.columns)
            column_defs = []

            if not table_exists:
                for col, dtype in data.dtypes.items():
                    sql_type = sql_type_mapper(
                        dtype,
                        "mysql"
                    )

                    column_defs.append(
                        f'"{col}" {sql_type}'
                    )

                cursor.execute(
                    f"""
                    CREATE TABLE `{table_name}`
                    (
                        {', '.join(column_defs)}
                    )
                    """
                )

                conn.commit()
                existing_rows = set()

            else:
                cursor.execute(
                    f"SELECT * FROM `{table_name}`"
                )

                existing_rows = set(
                    cursor.fetchall()
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

                cursor.executemany(
                    f"""
                    INSERT INTO `{table_name}`
                    VALUES ({placeholders})
                    """,
                    values
                )

                conn.commit()

            if ai_ask and ai_model:
                ai_query_obj = AIQuery(
                    ai_ask,
                    table_name,
                    "mysql",
                    column_defs if not table_exists else columns
                )

                generated_query = ai_query_obj.sql_generate(
                    model=ai_model
                )

                cursor.execute(
                    generated_query
                )

                conn.commit()

        except Exception as e:
            print(e)

        finally:
            conn.close()