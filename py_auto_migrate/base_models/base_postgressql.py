import psycopg2
import pandas as pd


class BasePostgresSQL:
    def __init__(self, pg_uri):
        self.pg_uri = pg_uri

    def _connect(self):
        user_pass, host_db = self.pg_uri.replace(
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
            print(f"❌ PostgreSQL Connection Error: {e}")
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
            return pd.DataFrame()
        df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)
        conn.close()
        if df.empty:
            print(f"❌ Table '{table_name}' is empty.")
        return df.fillna(0)
