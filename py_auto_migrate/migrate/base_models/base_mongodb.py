import pandas as pd
from pymongo import MongoClient
from urllib.parse import urlparse
from py_auto_migrate.migrate.base_models.base import BaseModel
from py_auto_migrate.migrate.utils.type_mapper import infer_data_types


class BaseMongoDB(BaseModel):

    def __init__(self, mongo_uri):
        super().__init__(mongo_uri)

    def _connect(self):

        try:
            parsed = urlparse(self.uri)
            db_name = parsed.path.lstrip("/")

            if not db_name:
                db_name = "admin"
            auth_source = "admin"

            if parsed.query:
                query_params = dict(
                    param.split("=")
                    for param in parsed.query.split("&")
                    if "=" in param
                )
                auth_source = query_params.get(
                    "authSource",
                    "admin"
                )
            client = MongoClient(
                host=parsed.hostname,
                port=parsed.port or 27017,
                username=parsed.username,
                password=parsed.password,
                authSource=auth_source,
                serverSelectionTimeoutMS=5000
            )

            client.admin.command("ping")
            return client[db_name]


        except Exception as e:
            print( f"❌ MongoDB Connection Error: {e}")

            return None



    def get_tables(self):

        db = self._connect()

        if db is None:
            return []


        try:
            return db.list_table_names()
        except Exception as e:
            print(f"❌ Error getting collections: {e}")
            return []
    def read_table(self, table_name):

        db = self._connect()
        if db is None:
            return pd.DataFrame()
        try:
            data = list(db[table_name].find())

            if not data:
                print(f"❌ Collection '{table_name}' is empty.")
                return pd.DataFrame()

            for doc in data:
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])

                    

            df = pd.DataFrame(data)
            df = infer_data_types(df)

            return df
        
        except :
            return pd.DataFrame()