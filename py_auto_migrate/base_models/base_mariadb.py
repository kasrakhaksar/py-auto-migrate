import pandas as pd
import pymysql


class BaseMariaDB:
    def __init__(self, maria_uri):
        self.maria_uri = maria_uri

    def _parse_maria_uri(self, maria_uri=None):
        if maria_uri is None:
            maria_uri = self.maria_uri
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
        df = pd.read_sql(f"SELECT * FROM `{table_name}`", conn)
        conn.close()
        return df.fillna(0)
