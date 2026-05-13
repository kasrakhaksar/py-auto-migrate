import json
from py_auto_migrate.base_models.base_redis import BaseRedis
from py_auto_migrate.insert_models.base import BaseInsert
from py_auto_migrate.ai.ai_query import AIQuery


class InsertRedis(BaseRedis, BaseInsert):
    def __init__(self, redis_uri, db_index=None):
        super().__init__(redis_uri)
        self.db_index = db_index

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        conn = self._connect()
        if conn is None:
            return

        if isinstance(data, str):
            data = json.loads(data)
        
        if not data:
            return
        

        value = json.dumps(data)
        conn.set(table_name, value)


        if ai_ask and ai_model:
            sample_item = data[0] if isinstance(data, list) and data else data
            columns = [f"`{col}`" for col in (sample_item.keys() if isinstance(sample_item, dict) else [])]
            ai_query_obj = AIQuery(ai_ask, table_name, 'redis', columns)
            generated_query = ai_query_obj.nosql_generate(model=ai_model)
            
            try:
                print(f"AI-generated query for Redis: {generated_query}")
            except Exception as e:
                print(f"Error processing AI query: {e}")
                raise
            return
