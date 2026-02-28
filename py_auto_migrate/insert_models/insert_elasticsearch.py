from elasticsearch import helpers
from py_auto_migrate.base_models.base_elasticsearch import BaseElasticsearch
from py_auto_migrate.insert_models.base import BaseInsert


class InsertElasticsearch(BaseElasticsearch, BaseInsert):
    def __init__(self, es_uri):
        super().__init__(es_uri)

    def insert(self, df, table_name):
        es = self._connect()
        if es is None:
            return

        if es.indices.exists(index=table_name):
            return

        es.indices.create(index=table_name, ignore=400)

        try:
            actions = [
                {
                    "_index": table_name,
                    "_source": row.to_dict()
                }
                for _, row in df.iterrows()
            ]

            helpers.bulk(es, actions)

        except Exception as e:
            pass