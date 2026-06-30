import re
import pymysql

from py_auto_migrate.migrate.base_models.base_mysql import BaseMySQL
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery
from py_auto_migrate.migrate.utils.type_mapper import sql_type_mapper


class InsertMySQL(BaseMySQL, BaseInsert):
    def __init__(self, mysql_uri):
        super().__init__(mysql_uri)
        self._ensure_database()

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

    @staticmethod
    def _validate_identifier(name):
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(name)):
            raise ValueError(f"Invalid SQL identifier: {name}")
        return name

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        conn = self._connect()

        if conn is None:
            return


        try:
            cursor = conn.cursor()
            table_name = self._validate_identifier(table_name)
            cursor.execute(
                "SHOW TABLES LIKE %s",
                (table_name,)
            )

            table_exists = cursor.fetchone() is not None

            columns = [self._validate_identifier(c) for c in data.columns]
            column_defs = []

            if not table_exists:

                for col, dtype in zip(columns, data.dtypes):
                    sql_type = sql_type_mapper(
                        dtype,
                        "mysql"
                    )

                    column_defs.append(
                        f"`{col}` {sql_type}"
                    )

                create_query = f"""
                CREATE TABLE `{table_name}` (
                    {', '.join(column_defs)}
                )
                """

                cursor.execute(create_query)
                conn.commit()

                existing_rows = set()

            else:

                cursor.execute(
                    f"SELECT * FROM `{table_name}`"
                )

                existing_rows = set(
                    cursor.fetchall()
                )

            rows = list(
                data[columns].itertuples(
                    index=False,
                    name=None
                )
            )

            values = []
            seen = set()

            for row in rows:
                if row not in existing_rows and row not in seen:
                    values.append(row)
                    seen.add(row)

            if values:

                placeholders = ", ".join(
                    ["%s"] * len(columns)
                )

                column_names = ", ".join(
                    f"`{c}`" for c in columns
                )

                insert_query = f"""
                INSERT INTO `{table_name}` ({column_names})
                VALUES ({placeholders})
                """

                cursor.executemany(
                    insert_query,
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
            return False
            
        finally:
            conn.close()

        return True