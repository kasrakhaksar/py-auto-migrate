import pandas as pd
import pymysql
from py_auto_migrate.migrate.base_models.base import BaseModel


class BaseMariaDB(BaseModel):

    def __init__(self, maria_uri):
        super().__init__(maria_uri)

    def _parse_maria_uri(self, maria_uri=None):

        if maria_uri is None:
            maria_uri = self.uri

        maria_uri = (
            maria_uri
            .replace("mariadb://", "")
            .replace("mysql://", "")
        )

        user_pass, host_db = maria_uri.split("@")
        user, password = user_pass.split(":")

        host_port, db_name = host_db.split("/")

        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)

        else:
            host, port = host_port, 3306

        return host, port, user, password, db_name


    def _connect(self):

        host, port, user, password, db_name = self._parse_maria_uri()

        return pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name
        )


    def get_tables(self):

        conn = self._connect()

        cur = conn.cursor()

        cur.execute("SHOW TABLES")

        tables = [
            row[0]
            for row in cur.fetchall()
        ]

        conn.close()

        return tables


    def read_table(self, table_name):

        conn = self._connect()

        cur = conn.cursor()

        cur.execute(
            f"SELECT * FROM `{table_name}`"
        )

        rows = cur.fetchall()

        columns = [
            desc[0]
            for desc in cur.description
        ]

        conn.close()

        return pd.DataFrame(
            rows,
            columns=columns
        )
    
    def get_foreignkey_dependencies(self, table_name: str) -> list[str]:
        conn = self._connect()

        if conn is None:
            return []

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT DISTINCT
                    REFERENCED_TABLE_NAME AS dependency
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = %s
                AND REFERENCED_TABLE_NAME IS NOT NULL;
                """,
                (table_name,)
            )

            return [row[0] for row in cursor.fetchall()]

        finally:
            cursor.close()
            conn.close()