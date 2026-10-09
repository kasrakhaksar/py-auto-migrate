import pandas as pd
from elasticsearch import Elasticsearch, helpers
from py_auto_migrate.migrate.base_models.base import BaseModel
from py_auto_migrate.core.logging import get_logger

logger = get_logger(__name__)


class BaseElasticsearch(BaseModel):

    def __init__(self, es_uri):
        super().__init__(es_uri)

    def _connect(self):
        self.uri = self.uri.replace('elasticsearch://','http://')
        try:
            es = Elasticsearch([self.uri])
            return es

        except Exception:
            logger.exception("Elasticsearch connection failed")
            return None

    def get_tables(self):
        es = self._connect()

        if es is None:
            
            return []

        try:
            indices = es.indices.get_alias(index="*")
            return list(indices)

        except Exception:
            logger.exception("Failed to list Elasticsearch indices")
            return []

    def read_table(self, index_name):

        es = self._connect()



        try:
            records = [
                hit["_source"] | {"_id": hit["_id"]}
                for hit in helpers.scan(
                    es,
                    index=index_name,
                    query={"query": {"match_all": {}}},
                    size=1000,
                )
            ]

            if not records:
                return pd.DataFrame()

            df = pd.DataFrame(records)
            return df

        except Exception:
            logger.exception("Failed to read Elasticsearch index '%s'", index_name)
            return pd.DataFrame()
