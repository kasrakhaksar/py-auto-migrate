import json
import pandas as pd
from py_auto_migrate.base_models.base_redis import BaseRedis
from py_auto_migrate.insert_models.base import BaseInsert


class InsertRedis(BaseRedis, BaseInsert):
    def __init__(self, redis_uri, db_index=None):
        super().__init__(redis_uri)
        self.db_index = db_index

    def insert(self, df: pd.DataFrame, table_name: str):
        conn = self._connect()
        if conn is None:
            return

        if df.empty:
            return

        data = df.fillna(0).to_dict(orient='records')
        value = json.dumps(data)

        conn.set(table_name, value)