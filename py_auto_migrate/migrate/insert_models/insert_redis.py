import json
from py_auto_migrate.migrate.base_models.base_redis import BaseRedis
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery


class InsertRedis(BaseRedis, BaseInsert):
    def __init__(self, redis_uri, db_index=None):
        super().__init__(redis_uri)
        self.db_index = db_index

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        conn = self._connect()
        if conn is None:
            return

        try:
            if isinstance(data, str):
                data = json.loads(data)

            if not data:
                return

            existing = conn.get(table_name)
            existing_data = set()

            if existing:
                try:
                    parsed = json.loads(existing)
                    if isinstance(parsed, list):
                        existing_data = set(json.dumps(x, sort_keys=True) for x in parsed)
                    else:
                        existing_data = {json.dumps(parsed, sort_keys=True)}
                except Exception:
                    existing_data = set()

            new_data = []

            if isinstance(data, list):
                for item in data:
                    item_str = json.dumps(item, sort_keys=True)
                    if item_str not in existing_data:
                        new_data.append(item)
                        existing_data.add(item_str)
            else:
                item_str = json.dumps(data, sort_keys=True)
                if item_str not in existing_data:
                    new_data.append(data)

            if new_data:
                if existing:
                    try:
                        merged = json.loads(existing)
                        if not isinstance(merged, list):
                            merged = [merged]
                    except Exception:
                        merged = []

                    merged.extend(new_data)
                    conn.set(table_name, json.dumps(merged))
                else:
                    conn.set(table_name, json.dumps(new_data))

            if ai_ask and ai_model:
                sample_item = new_data[0] if new_data else (data[0] if isinstance(data, list) else data)
                columns = [f"`{col}`" for col in (sample_item.keys() if isinstance(sample_item, dict) else [])]

                ai_query_obj = AIQuery(ai_ask, table_name, "redis", columns)
                generated_query = ai_query_obj.nosql_generate(model=ai_model)
                print(generated_query)

        finally:
            conn.close()