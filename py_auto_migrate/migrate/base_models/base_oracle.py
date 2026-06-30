import pandas as pd
import oracledb
from py_auto_migrate.migrate.base_models.base import BaseModel


class BaseOracle(BaseModel):

    def __init__(self, oracle_uri):
        super().__init__(oracle_uri)


    def _parse_oracle_uri(self):

        uri = self.uri.replace("oracle://", "")
        user_pass, host_db = uri.split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:

            host, port = host_port.split(":")
        else:

            host, port = host_port, "1521"
        return user, password, host, port, db_name


    def _connect(self):

        user, password, host, port, db_name = self._parse_oracle_uri()
        dsn = f"{host}:{port}/{db_name}"

        return oracledb.connect(
            user=user,
            password=password,
            dsn=dsn
        )

    def get_tables(self):

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM user_tables")

        tables = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()
        return tables

    def read_table(self, table_name):

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM "{table_name}"')
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
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
                    pk.table_name AS dependency
                FROM user_constraints fk
                JOIN user_constraints pk
                    ON fk.r_constraint_name = pk.constraint_name
                WHERE fk.constraint_type = 'R'
                AND fk.table_name = :table_name
                """,
                {"table_name": table_name.upper()}
            )

            return [row[0] for row in cursor.fetchall()]

        finally:
            cursor.close()
            conn.close()