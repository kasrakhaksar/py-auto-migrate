import psycopg2
import json
from py_auto_migrate.migrate.base_models.base import BaseModel


class BasePostgresSQL(BaseModel):
    def __init__(self, pg_uri):
        super().__init__(pg_uri)

    def _connect(self):
        user_pass, host_db = self.uri.replace(
            "postgresql://", "").split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host, port = host_port, 5432
        try:
            return psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db_name)
        except Exception as e:
            return None

    def get_tables(self):
        conn = self._connect()
        if conn is None:
            return []
        cursor = conn.cursor()
        cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tables

    def read_table(self, table_name):
        conn = self._connect()
        if conn is None:
            return []
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM "{table_name}"')
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        cursor.close()
        conn.close()
        data = [dict(zip(colnames, row)) for row in rows]
        return json.dumps(data)