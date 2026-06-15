import json
from pymongo import MongoClient
from urllib.parse import urlparse
from py_auto_migrate.migrate.base_models.base import BaseModel


class BaseMongoDB(BaseModel):
    def __init__(self, mongo_uri):
        super().__init__(mongo_uri)

    def _connect(self):
        try:
            parsed = urlparse(self.uri)
            db_name = parsed.path.lstrip('/')

            if not db_name:
                db_name = 'admin'

            auth_source = 'admin'

            if parsed.query:
                query_params = dict(param.split('=')
                                    for param in parsed.query.split('&') if '=' in param)
                auth_source = query_params.get('authSource', 'admin')

            client = MongoClient(
                host=parsed.hostname,
                port=parsed.port or 27017,
                username=parsed.username,
                password=parsed.password,
                authSource=auth_source,
                serverSelectionTimeoutMS=5000
            )

            client.admin.command('ping')
            return client[db_name]

        except Exception as e:
            print(f"❌ MongoDB Connection Error: {e}")
            return None

    def get_tables(self):
        db = self._connect()
        if db is None:
            return []
        try:
            return db.list_collection_names()
        except Exception as e:
            print(f"❌ Error getting collections: {e}")
            return []

    def read_table(self, collection_name):
        db = self._connect()
        if db is None:
            return []

        try:
            data = list(db[collection_name].find())
            if not data:
                print(f"❌ Collection '{collection_name}' is empty.")
                return []

            for doc in data:
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])

            return json.dumps(data)
        except Exception as e:
            print(f"❌ Error reading collection '{collection_name}': {e}")
            return []