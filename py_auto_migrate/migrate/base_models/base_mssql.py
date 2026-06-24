import pandas as pd
import pyodbc
from py_auto_migrate.migrate.base_models.base import BaseModel


class BaseMSSQL(BaseModel):

    def __init__(self, mssql_uri):
        super().__init__(mssql_uri)


    def _parse_mssql_uri(self, uri=None):

        if uri is None:
            uri = self.uri

        uri = uri.replace("mssql://", "")

        if uri.startswith("@") or "@" not in uri:
            if uri.startswith("@"):
                uri = uri[1:]

            host_port, db_name = uri.split("/", 1)
            if ":" in host_port:
                host, port = host_port.split(":")
            else:
                host, port = host_port, "1433"

            return {
                "auth": "windows",
                "host": host,
                "port": port,
                "database": db_name
            }

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

            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={cfg['host']},{cfg['port']};"
                f"DATABASE={cfg['database']};"
                "Trusted_Connection=yes;"
            )
        else:
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={cfg['host']},{cfg['port']};"
                f"DATABASE={cfg['database']};"
                f"UID={cfg['user']};"
                f"PWD={cfg['password']};"
            )

        return pyodbc.connect(conn_str)

    def get_tables(self):

        conn = self._connect()

        cur = conn.cursor()

        cur.execute(
            """
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE='BASE TABLE'
            """
        )

        tables = [ row[0] for row in cur.fetchall()]
        conn.close()
        return tables

    def read_table(self, table_name):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute( f"SELECT * FROM [{table_name}]")
        rows = cur.fetchall()

        columns = [ desc[0] for desc in cur.description]
        conn.close()
        return pd.DataFrame(rows, columns=columns)
    
    
    def get_foreignkey_dependencies(self, table_name: str) -> list[str]:
        conn = self._connect()

        if conn is None:
            return []

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT DISTINCT
                    referenced_table.name AS dependency
                FROM sys.foreign_keys fk
                JOIN sys.tables parent_table
                    ON fk.parent_object_id = parent_table.object_id
                JOIN sys.tables referenced_table
                    ON fk.referenced_object_id = referenced_table.object_id
                WHERE parent_table.name = ?;
                """,
                (table_name,)
            )

            return [row[0] for row in cursor.fetchall()]

        finally:
            cursor.close()
            conn.close()