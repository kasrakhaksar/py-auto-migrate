from elasticsearch import helpers
from py_auto_migrate.base_models.base_elasticsearch import BaseElasticsearch


class InsertElasticsearch(BaseElasticsearch):
    def __init__(self, es_uri):
        super().__init__(es_uri)

    def insert(self, df, index_name):
        es = self._connect()
        if es is None:
            print("❌ Cannot connect to Elasticsearch. Insert aborted.")
            return

        if es.indices.exists(index=index_name):
            print(f"⚠ Index '{index_name}' already exists. Skipping insert.")
            return

        es.indices.create(index=index_name, ignore=400)

        try:
            actions = [
                {
                    "_index": index_name,
                    "_source": row.to_dict()
                }
                for _, row in df.iterrows()
            ]

            helpers.bulk(es, actions)

            print(f"✅ Inserted {len(df)} rows into Elasticsearch index '{index_name}'")

        except Exception as e:
            print(f"❌ Error inserting into Elasticsearch: {e}")
