import pymysql
import json
from py_auto_migrate.migrate.base_models.base_mariadb import BaseMariaDB
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery


class InsertMariaDB(BaseMariaDB, BaseInsert):
    def __init__(self, maria_uri):
        self.maria_uri = maria_uri
        self._ensure_database()
        super().__init__(maria_uri)

    def _ensure_database(self):
        host, port, user, password, db_name = self._parse_maria_uri()

        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )

        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
        conn.commit()
        conn.close()

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        conn = self._connect()
        if conn is None:
            return

        try:
            if isinstance(data, str):
                data = json.loads(data)

            if not data:
                return

            cursor = conn.cursor()

            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            table_exists = cursor.fetchone() is not None

            columns = list(data[0].keys())
            column_defs = []

            if not table_exists:
                for col, val in data[0].items():
                    if isinstance(val, bool):
                        col_type = "TINYINT(1)"
                    elif isinstance(val, int):
                        col_type = "BIGINT"
                    elif isinstance(val, float):
                        col_type = "DOUBLE"
                    else:
                        col_type = "TEXT"

                    column_defs.append(f"`{col}` {col_type}")

                cursor.execute(
                    f"CREATE TABLE `{table_name}` ({', '.join(column_defs)})"
                )
                conn.commit()

                existing_rows = set()

            else:
                cursor.execute(f"SELECT * FROM `{table_name}`")
                existing_rows = set(cursor.fetchall())

            values = []
            seen = set()

            for row in data:
                row_tuple = tuple(row[col] for col in columns)

                if row_tuple not in existing_rows and row_tuple not in seen:
                    values.append(row_tuple)
                    seen.add(row_tuple)

            if values:
                placeholders = ", ".join(["%s"] * len(columns))

                cursor.executemany(
                    f"INSERT INTO `{table_name}` VALUES ({placeholders})",
                    values
                )
                conn.commit()

            if ai_ask and ai_model:
                ai_query_obj = AIQuery(
                    ai_ask,
                    table_name,
                    "mariadb",
                    column_defs if not table_exists else columns,
                )

                generated_query = ai_query_obj.sql_generate(model=ai_model)

                try:
                    cursor.execute(generated_query)
                    conn.commit()
                except Exception as e:
                    print(f"Error executing AI query: {e}")
                    raise

        finally:
            conn.close()