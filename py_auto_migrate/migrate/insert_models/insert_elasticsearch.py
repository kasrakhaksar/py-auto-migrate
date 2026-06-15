import json
from elasticsearch import helpers
from py_auto_migrate.migrate.base_models.base_elasticsearch import BaseElasticsearch
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery


class InsertElasticsearch(BaseElasticsearch, BaseInsert):
    def __init__(self, es_uri):
        super().__init__(es_uri)

    def _ensure_index(self, es, index_name):
        if not es.indices.exists(index=index_name):
            es.indices.create(index=index_name, ignore=400)

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        es = self._connect()
        if es is None:
            return

        try:
            if isinstance(data, str):
                data = json.loads(data)

            if not data:
                return

            self._ensure_index(es, table_name)

            existing_set = set()

            try:
                query = {"query": {"match_all": {}}}
                res = es.search(index=table_name, body=query, size=10000)
                existing_set = set(
                    json.dumps(hit["_source"], sort_keys=True)
                    for hit in res["hits"]["hits"]
                )
            except Exception:
                existing_set = set()

            new_docs = []

            if isinstance(data, list):
                for item in data:
                    item_str = json.dumps(item, sort_keys=True)
                    if item_str not in existing_set:
                        new_docs.append(item)
                        existing_set.add(item_str)
            else:
                item_str = json.dumps(data, sort_keys=True)
                if item_str not in existing_set:
                    new_docs.append(data)

            if new_docs:
                actions = [
                    {"_index": table_name, "_source": item}
                    for item in new_docs
                ]
                helpers.bulk(es, actions)

            if ai_ask and ai_model:
                sample_item = new_docs[0] if new_docs else (data[0] if isinstance(data, list) else data)
                columns = [f"`{col}`" for col in sample_item.keys()] if isinstance(sample_item, dict) else []

                ai_query_obj = AIQuery(ai_ask, table_name, "elasticsearch", columns)
                generated_query = ai_query_obj.nosql_generate(model=ai_model)

                print(generated_query)

        except Exception:
            pass