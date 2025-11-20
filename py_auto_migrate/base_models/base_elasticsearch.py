import pandas as pd
from elasticsearch import Elasticsearch



class BaseElasticsearch:
    def __init__(self, es_uri):
        self.es_uri = es_uri

    def _connect(self):
        try:
            es = Elasticsearch(self.es_uri)
            if not es.ping():
                print("❌ Cannot connect to Elasticsearch server!")
                return None
            return es
        except Exception as e:
            print(f"❌ Elasticsearch Connection Error: {e}")
            return None

    def get_indices(self):
        es = self._connect()
        if es is None:
            return []
        try:
            indices = es.indices.get_alias("*").keys()
            return list(indices)
        except Exception as e:
            print(f"❌ Error getting indices: {e}")
            return []

    def read_index(self, index_name, size=10000):
        es = self._connect()
        if es is None:
            return pd.DataFrame()

        try:
            query = {
                "query": {"match_all": {}},
                "size": size
            }

            result = es.search(index=index_name, body=query)

            hits = result.get("hits", {}).get("hits", [])
            if not hits:
                print(f"❌ Index '{index_name}' is empty or not found.")
                return pd.DataFrame()

            records = [hit["_source"] | {"_id": hit["_id"]} for hit in hits]

            df = pd.DataFrame(records)
            return df

        except Exception as e:
            print(f"❌ Error reading index '{index_name}': {e}")
            return pd.DataFrame()
