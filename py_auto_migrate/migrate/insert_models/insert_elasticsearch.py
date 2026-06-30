from elasticsearch import helpers
from py_auto_migrate.migrate.base_models.base_elasticsearch import BaseElasticsearch
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery

class InsertElasticsearch(BaseElasticsearch, BaseInsert):
    def __init__(self, es_uri):
        super().__init__(es_uri)

    def _ensure_index(self, es, index_name):
        if not es.indices.exists(index=index_name):
            es.indices.create(
                index=index_name,
                ignore=400
            )

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        es = self._connect()

        if es is None:
            return


        try:
            self._ensure_index(
                es,
                table_name
            )

            existing_set = set()

            try:
                query = {
                    "query": {
                        "match_all": {}
                    }
                }

                res = es.search(
                    index=table_name,
                    body=query,
                    size=10000
                )

                for hit in res["hits"]["hits"]:
                    existing_set.add(
                        tuple(hit["_source"].values())
                    )

            except Exception:
                existing_set = set()

            records = data.to_dict(
                orient="records"
            )

            new_docs = []

            for item in records:
                key = tuple(item.values())

                if key not in existing_set:
                    new_docs.append(item)
                    existing_set.add(key)

            if new_docs:
                actions = [
                    {
                        "_index": table_name,
                        "_source": item
                    }
                    for item in new_docs
                ]

                helpers.bulk(
                    es,
                    actions
                )

            if ai_ask and ai_model:
                columns = [
                    f"`{col}`"
                    for col in data.columns
                ]

                ai_query_obj = AIQuery(
                    ai_ask,
                    table_name,
                    "elasticsearch",
                    columns
                )

                generated_query = ai_query_obj.nosql_generate(
                    model=ai_model
                )

                print(generated_query)

        except Exception as e:
            print(e)
            return False
        
        return True