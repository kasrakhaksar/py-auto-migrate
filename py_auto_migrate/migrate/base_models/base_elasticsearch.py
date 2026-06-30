import pandas as pd
from elasticsearch import Elasticsearch
from py_auto_migrate.migrate.base_models.base import BaseModel
from py_auto_migrate.migrate.utils.type_mapper import infer_data_types


class BaseElasticsearch(BaseModel):

    def __init__(self, es_uri):
        super().__init__(es_uri)

    def _connect(self):
        self.uri = self.uri.replace('elasticsearch://','http://')
        try:
            es = Elasticsearch([self.uri])
            return es

        except Exception as e:
            print(e)

    def get_tables(self):
        es = self._connect()

        if es is None:
            
            return []

        try:
            indices = es.indices.get_alias(index="*")
            return list(indices)

        except Exception as e:
            return []

    def read_table(self, index_name):

        es = self._connect()



        try:
            query = {
                "query": {
                    "match_all": {}
                },
                "size": 10000
            }
            result = es.search(
                index=index_name,
                body=query
            )

            hits = result.get("hits",{}).get("hits",[])
            if not hits:
                return pd.DataFrame()

            records = [
                hit["_source"] | {"_id": hit["_id"]}
                for hit in hits
            ]


            df = pd.DataFrame(records)
            df = infer_data_types(df)
            return df

        except Exception:
            return pd.DataFrame()