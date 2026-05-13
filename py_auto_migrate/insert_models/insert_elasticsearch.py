from elasticsearch import helpers
from py_auto_migrate.base_models.base_elasticsearch import BaseElasticsearch
from py_auto_migrate.insert_models.base import BaseInsert
from py_auto_migrate.ai.ai_query import AIQuery
import json


class InsertElasticsearch(BaseElasticsearch, BaseInsert):
    def __init__(self, es_uri):
        super().__init__(es_uri)

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        es = self._connect()
        if es is None:
            return

        if isinstance(data, str):
            data = json.loads(data)
        
        if not data:
            return

        if es.indices.exists(index=table_name):
            return

        es.indices.create(index=table_name, ignore=400)

        try:
            actions = [
                {
                    "_index": table_name,
                    "_source": item
                }
                for item in data
            ]

            helpers.bulk(es, actions)

        except Exception as e:
            pass

        if ai_ask and ai_model:
            sample_item = data[0] if data else {}
            columns = [f"`{col}`" for col in sample_item.keys()]
            ai_query_obj = AIQuery(ai_ask, table_name, 'elasticsearch', columns)
            generated_query = ai_query_obj.nosql_generate(model=ai_model)
            
            try:
                print(f"AI-generated query for Elasticsearch: {generated_query}")
            except Exception as e:
                print(f"Error processing AI query: {e}")
                raise
            return

