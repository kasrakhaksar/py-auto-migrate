import pymysql
import json
from py_auto_migrate.migrate.base_models.base import BaseModel


class BaseMariaDB(BaseModel):
    def __init__(self, maria_uri):
        super().__init__(maria_uri)

    def _parse_maria_uri(self, maria_uri=None):
        if maria_uri is None:
            maria_uri = self.uri
        maria_uri = maria_uri.replace("mariadb://", "").replace("mysql://", "")
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
        return pymysql.connect(host=host, port=port, user=user, password=password, database=db_name)

    def get_tables(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("SHOW TABLES")
        tables = [r[0] for r in cur.fetchall()]
        conn.close()
        return tables

    def read_table(self, table_name):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM `{table_name}`")
        rows = cur.fetchall()
        cur.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
        columns = [r[0] for r in cur.fetchall()]
        conn.close()
        data = [dict(zip(columns, row)) for row in rows]
        return json.dumps(data)