import pandas as pd
import json
from py_auto_migrate.migrate.base_models.base_redis import BaseRedis
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery

class InsertRedis(BaseRedis, BaseInsert):
    def __init__(self, redis_uri, db_index=None):
        super().__init__(redis_uri)
        self.db_index = db_index

    def insert(self, data: pd.DataFrame, table_name, ai_ask=None, ai_model=None):
        conn = self._connect()

        if conn is None:
            return

        if data is None or data.empty:
            return

        try:
            existing = conn.get(
                table_name
            )

            existing_data = []

            if existing:
                if isinstance(existing, bytes):
                    existing = existing.decode(
                        "utf-8"
                    )

                try:
                    existing_data = json.loads(
                        existing
                    )

                    if not isinstance(existing_data, list):
                        existing_data = [
                            existing_data
                        ]

                except Exception:
                    existing_data = []

            existing_set = set(
                json.dumps(
                    item,
                    sort_keys=True
                )
                for item in existing_data
            )

            new_data = []

            rows = data.to_dict(
                orient="records"
            )

            for item in rows:
                item_str = json.dumps(
                    item,
                    sort_keys=True
                )

                if item_str not in existing_set:
                    new_data.append(item)

                    existing_set.add(
                        item_str
                    )

            if new_data:
                existing_data.extend(
                    new_data
                )

                conn.set(
                    table_name,
                    json.dumps(
                        existing_data,
                        default=str
                    )
                )

            if ai_ask and ai_model:
                sample_item = (
                    new_data[0]
                    if new_data
                    else rows[0]
                )

                columns = [
                    f"`{col}`"
                    for col in sample_item.keys()
                ]

                ai_query_obj = AIQuery(
                    ai_ask,
                    table_name,
                    "redis",
                    columns
                )

                generated_query = ai_query_obj.nosql_generate(
                    model=ai_model
                )

                print(
                    generated_query
                )

        finally:
            conn.close()