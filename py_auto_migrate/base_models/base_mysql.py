from mysqlSaver import Connection
import pandas as pd


class BaseMySQL:
    def __init__(self, mysql_uri):
        self.mysql_uri = mysql_uri

    def _parse_mysql_uri(self, uri=None):
        if uri is None:
            uri = self.mysql_uri
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
        return Connection.connect(host, port, user, password, db_name)

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
        cursor.execute(f"SELECT * FROM `{table_name}`")
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        df = pd.DataFrame(data, columns=columns)
        if df.empty:
            print(f"❌ Table '{table_name}' is empty.")
        return df.fillna(0)
