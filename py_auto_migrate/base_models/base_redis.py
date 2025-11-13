import redis
import pandas as pd
import json


class BaseRedis:
    def __init__(self, redis_uri):
        self.redis_uri = redis_uri
        self._conn = None

    def _connect(self):
        if self._conn:
            return self._conn
        try:
            self._conn = redis.from_url(self.redis_uri)
            self._conn.ping()
            return self._conn
        except Exception as e:
            print(f"❌ Redis Connection Error: {e}")
            return None

    def get_keys(self, pattern='*'):
        conn = self._connect()
        if conn is None:
            return []
        try:
            return conn.keys(pattern)
        except Exception as e:
            print(f"❌ Error fetching keys: {e}")
            return []

    def read_key(self, key):
        conn = self._connect()
        if conn is None:
            return pd.DataFrame()
        try:
            value = conn.get(key)
            if value is None:
                print(f"❌ Key '{key}' not found or empty.")
                return pd.DataFrame()

            data = json.loads(value)

            if isinstance(data, dict) and all(str(k).isdigit() for k in data.keys()):
                data = list(data.values())

            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                print(f"⚠ Unexpected data format in key '{key}'.")
                return pd.DataFrame()

            return df.fillna(0)
        except Exception as e:
            print(f"❌ Error reading key '{key}': {e}")
            return pd.DataFrame()
