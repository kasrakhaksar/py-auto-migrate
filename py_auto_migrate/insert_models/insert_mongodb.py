from py_auto_migrate.base_models.base_mongodb import BaseMongoDB
from py_auto_migrate.insert_models.base import BaseInsert


class InsertMongoDB(BaseMongoDB, BaseInsert):
    def __init__(self, mongo_uri):
        super().__init__(mongo_uri)

    def insert(self, df, table_name):
        db = self._connect()
        if db is None:
            return

        if table_name in db.list_collection_names():
            return

        db[table_name].insert_many(df.to_dict("records"))