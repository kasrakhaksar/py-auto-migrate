import json
from py_auto_migrate.migrate.base_models.base_mongodb import BaseMongoDB
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery


class InsertMongoDB(BaseMongoDB, BaseInsert):
    def __init__(self, mongo_uri):
        super().__init__(mongo_uri)

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        db = self._connect()
        if db is None:
            return

        try:
            if isinstance(data, str):
                data = json.loads(data)

            if not data:
                return

            collection = db[table_name]

            existing_set = set()
            try:
                cursor = collection.find({}, {"_id": 0})
                for doc in cursor:
                    existing_set.add(json.dumps(doc, sort_keys=True))
            except Exception:
                existing_set = set()

            new_docs = []

            if isinstance(data, list):
                for item in data:
                    item_str = json.dumps(item, sort_keys=True)
                    if item_str not in existing_set:
                        new_docs.append(item)
                        existing_set.add(item_str)
            else:
                item_str = json.dumps(data, sort_keys=True)
                if item_str not in existing_set:
                    new_docs.append(data)

            if new_docs:
                collection.insert_many(new_docs, ordered=False)

            if ai_ask and ai_model:
                sample_item = new_docs[0] if new_docs else (data[0] if isinstance(data, list) else data)
                columns = [f"`{col}`" for col in sample_item.keys()] if isinstance(sample_item, dict) else []

                ai_query_obj = AIQuery(ai_ask, table_name, "mongodb", columns)
                generated_query = ai_query_obj.nosql_generate(model=ai_model)

                print(generated_query)

        except Exception:
            pass