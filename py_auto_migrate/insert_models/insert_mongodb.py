from py_auto_migrate.base_models.base_mongodb import BaseMongoDB


class InsertMongoDB(BaseMongoDB):
    def __init__(self, mongo_uri):
        super().__init__(mongo_uri)

    def insert(self, df, collection_name):
        db = self._connect()
        if db is None:
            print(f"❌ Cannot connect to MongoDB. Insert aborted.")
            return

        if collection_name in db.list_collection_names():
            print(f"⚠ Collection '{collection_name}' already exists. Skipping insert.")
            return

        db[collection_name].insert_many(df.to_dict("records"))
        print(f"✅ Inserted {len(df)} rows into MongoDB collection '{collection_name}'")
