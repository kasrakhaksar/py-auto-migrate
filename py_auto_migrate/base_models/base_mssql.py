import pyodbc
import pandas as pd


class BaseMSSQL:
    def __init__(self, mssql_uri):
        self.mssql_uri = mssql_uri

    def _parse_mssql_uri(self, uri=None):
        if uri is None:
            uri = self.mssql_uri
        uri = uri.replace("mssql://", "")
        if uri.startswith("@") or "@" not in uri:
            if uri.startswith("@"):
                uri = uri[1:]
            host_port, db_name = uri.split("/", 1)
            if ":" in host_port:
                host, port = host_port.split(":")
            else:
                host, port = host_port, "1433"
            return {"auth": "windows", "host": host, "port": port, "database": db_name}
        else:
            user_pass, host_db = uri.split("@", 1)
            user, password = user_pass.split(":", 1)
            host_port, db_name = host_db.split("/", 1)
            if ":" in host_port:
                host, port = host_port.split(":")
            else:
                host, port = host_port, "1433"
            return {
                "auth": "sql",
                "host": host,
                "port": port,
                "database": db_name,
                "user": user,
                "password": password
            }

    def _connect(self):
        cfg = self._parse_mssql_uri()
        if cfg["auth"] == "windows":
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={cfg['host']},{cfg['port']};DATABASE={cfg['database']};Trusted_Connection=yes;"
        else:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={cfg['host']},{cfg['port']};DATABASE={cfg['database']};UID={cfg['user']};PWD={cfg['password']};"
        return pyodbc.connect(conn_str)

    def get_tables(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
        tables = [r[0] for r in cur.fetchall()]
        conn.close()
        return tables

    def read_table(self, table_name):
        conn = self._connect()
        df = pd.read_sql(f"SELECT * FROM [{table_name}]", conn)
        conn.close()
        return df.fillna(0)
