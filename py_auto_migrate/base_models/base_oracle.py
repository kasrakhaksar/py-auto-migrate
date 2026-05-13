import oracledb
import json
from py_auto_migrate.base_models.base import BaseModel


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

    def _conn(self):
        user, password, host, port, db_name = self._parse_oracle_uri()
        dsn = f"{host}:{port}/{db_name}"
        return oracledb.connect(user=user, password=password, dsn=dsn)

    def get_tables(self):
        conn = self._conn()
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM user_tables")
        tables = [r[0] for r in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tables

    def read_table(self, table_name):
        conn = self._conn()
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM "{table_name}"')
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        conn.close()
        data = [dict(zip(columns, row)) for row in rows]
        return json.dumps(data)