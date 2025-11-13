import json
import pandas as pd
from py_auto_migrate.base_models.base_redis import BaseRedis


class InsertRedis(BaseRedis):
    def __init__(self, redis_uri, db_index=None):
        super().__init__(redis_uri)
        self.db_index = db_index

    def insert(self, df: pd.DataFrame, key_name: str):
        conn = self._connect()
        if conn is None:
            print("❌ Cannot connect to Redis. Insert aborted.")
            return

        if df.empty:
            print(f"❌ DataFrame is empty. Nothing to insert.")
            return

        data = df.fillna(0).to_dict(orient='records')
        value = json.dumps(data)

        conn.set(key_name, value)
        print(
            f"✅ Inserted {len(df)} rows into Redis key '{key_name}' in database {self.db_index if self.db_index is not None else 0}")