import pandas as pd
import pymysql
from py_auto_migrate.migrate.base_models.base import BaseModel


class BaseMySQL(BaseModel):

    def __init__(self, mysql_uri):
        super().__init__(mysql_uri)


    def _parse_mysql_uri(self, uri=None):

        if uri is None:
            uri = self.uri

        uri = uri.replace("mysql://", "")
        user_pass, host_db = uri.split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")

        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)

        else:
            host, port = host_port, 3306

        return host, port, user, password, db_name



    def _connect(self, db_name=None):

        host, port, user, password, uri_db = self._parse_mysql_uri()

        if db_name is None:
            db_name = uri_db

        return pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name
        )

    def get_tables(self):

        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute("SHOW TABLES")

        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        return tables



    def read_table(self, table_name):

        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT * FROM `{table_name}`"
        )

        rows = cursor.fetchall()
        columns = [
            desc[0]
            for desc in cursor.description
        ]

        conn.close()

        return pd.DataFrame(rows, columns=columns )