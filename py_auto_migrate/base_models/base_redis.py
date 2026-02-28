import redis
import pandas as pd
import json
from py_auto_migrate.base_models.base import BaseModel


class BaseRedis(BaseModel):
    def __init__(self, redis_uri):
        super().__init__(redis_uri)

    def _connect(self):
        try:
            conn = redis.from_url(self.uri)
            conn.ping()
            return conn
        except Exception as e:
            return None

    def get_tables(self):
        conn = self._connect()
        if conn is None:
            return []
        try:
            keys = conn.keys('*')
            return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
        except Exception as e:
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
                value = value.decode('utf-8')
            
            data = json.loads(value)

            if isinstance(data, dict) and all(str(k).isdigit() for k in data.keys()):
                data = list(data.values())

            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                return pd.DataFrame()

            return df.fillna(0)
        except Exception as e:
            return pd.DataFrame()