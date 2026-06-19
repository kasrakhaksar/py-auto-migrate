import pandas as pd
import redis
from py_auto_migrate.migrate.base_models.base import BaseModel


class BaseRedis(BaseModel):

    def __init__(self, redis_uri):
        super().__init__(redis_uri)


    def _connect(self):
        try:
            conn = redis.from_url(
                self.uri
            )
            conn.ping()
            return conn
        except Exception:
            return None



    def get_tables(self):

        conn = self._connect()
        if conn is None:
            return []

        try:

            keys = conn.keys("*")
            return [
                key.decode("utf-8")
                if isinstance(key, bytes)
                else key
                for key in keys
            ]

        except Exception:
            return []



    def read_table(self, table_name):

        conn = self._connect()

        if conn is None:
            return pd.DataFrame()

        try:
            value = conn.get(table_name)
            if value is None:
                return pd.DataFrame()

            if isinstance(value, bytes):
                value = value.decode( "utf-8")

            return pd.DataFrame(value if isinstance(value, list) else [value])

        except Exception:
            return pd.DataFrame()