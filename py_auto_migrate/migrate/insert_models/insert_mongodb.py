import pandas as pd
from py_auto_migrate.migrate.base_models.base_mongodb import BaseMongoDB
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery


class InsertMongoDB(BaseMongoDB, BaseInsert):
    def __init__(self, mongo_uri):
        super().__init__(mongo_uri)

    def insert(self, data: pd.DataFrame, table_name, ai_ask=None, ai_model=None):

        db = self._connect()
        if db is None or data.empty:
            return

        try:
            collection = db[table_name]

            existing_set = set()

            try:
                cursor = collection.find({}, {"_id": 0})

                for doc in cursor:
                    existing_set.add(tuple(doc.values()))

            except Exception:
                pass

            new_docs = []

            for _, row in data.iterrows():
                row_dict = row.to_dict()
                row_key = tuple(row_dict.values())

                if row_key not in existing_set:
                    new_docs.append(row_dict)
                    existing_set.add(row_key)

            if new_docs:
                collection.insert_many(new_docs, ordered=False)

            if ai_ask and ai_model:
                columns = [f"`{col}`" for col in data.columns]

                ai_query_obj = AIQuery(
                    ai_ask,
                    table_name,
                    "mongodb",
                    columns
                )

                generated_query = ai_query_obj.nosql_generate(model=ai_model)

                print(generated_query)

        except Exception:
            pass