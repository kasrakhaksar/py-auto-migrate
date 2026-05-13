from py_auto_migrate.base_models.base_mongodb import BaseMongoDB
from py_auto_migrate.insert_models.base import BaseInsert
from py_auto_migrate.ai.ai_query import AIQuery
import json


class InsertMongoDB(BaseMongoDB, BaseInsert):
    def __init__(self, mongo_uri):
        super().__init__(mongo_uri)

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        db = self._connect()
        if db is None:
            return

        if isinstance(data, str):
            data = json.loads(data)
        
        if not data:
            return

        if table_name in db.list_collection_names():
            return


        db[table_name].insert_many(data)


        if ai_ask and ai_model:
            sample_item = data[0] if data else {}
            columns = [f"`{col}`" for col in sample_item.keys()]
            ai_query_obj = AIQuery(ai_ask, table_name, 'mongodb', columns)
            generated_query = ai_query_obj.nosql_generate(model=ai_model)
            
            try:
                print(f"AI-generated query for MongoDB: {generated_query}")
            except Exception as e:
                print(f"Error processing AI query: {e}")
                raise
            return

        