import pandas as pd
from pymongo import MongoClient
from urllib.parse import urlparse


class BaseMongoDB:
    def __init__(self, mongo_uri):
        self.mongo_uri = mongo_uri

    def _connect(self):
        try:
            parsed = urlparse(self.mongo_uri)
            db_name = parsed.path.lstrip('/')

            if parsed.username and parsed.password:
                uri = f"mongodb://{parsed.username}:{parsed.password}@{parsed.hostname}"
                if parsed.port:
                    uri += f":{parsed.port}"
                uri += f"/{db_name}"
            else:
                uri = self.mongo_uri

            client = MongoClient(uri)
            return client[db_name]

        except Exception as e:
            print(f"❌ MongoDB Connection Error: {e}")
            return None

    def get_collections(self):
        db = self._connect()
        if db is None:
            return []
        return db.list_collection_names()

    def read_collection(self, collection_name):
        db = self._connect()
        if db is None:
            return pd.DataFrame()
        data = list(db[collection_name].find())
        if not data:
            print(f"❌ Collection '{collection_name}' is empty.")
            return pd.DataFrame()
        df = pd.DataFrame(data)
        if "_id" in df.columns:
            df = df.drop(columns="_id")
        return df.fillna(0)