import json
from elasticsearch import Elasticsearch
from py_auto_migrate.base_models.base import BaseModel


class BaseElasticsearch(BaseModel):
    def __init__(self, es_uri):
        super().__init__(es_uri)

    def _connect(self):
        try:
            es = Elasticsearch(self.uri)
            if not es.ping():
                return None
            return es
        except Exception as e:
            return None

    def get_tables(self):
        es = self._connect()
        if es is None:
            return []
        try:
            indices = es.indices.get_alias("*").keys()
            return list(indices)
        except Exception as e:
            return []

    def read_table(self, index_name):
        es = self._connect()
        if es is None:
            return []

        try:
            query = {
                "query": {"match_all": {}},
                "size": 10000
            }

            result = es.search(index=index_name, body=query)

            hits = result.get("hits", {}).get("hits", [])
            if not hits:
                return []

            records = [hit["_source"] | {"_id": hit["_id"]} for hit in hits]

            return json.dumps(records)

        except Exception as e:
            return []