from elasticsearch import helpers
from py_auto_migrate.migrate.base_models.base_elasticsearch import BaseElasticsearch
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery
from py_auto_migrate.core.logging import get_logger

logger = get_logger(__name__)

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

            records = data.to_dict(
                orient="records"
            )
            if records:
                actions = [
                    {
                        "_index": table_name,
                        "_source": item
                    }
                    for item in records
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

                logger.debug("Generated AI query for Elasticsearch index '%s'", table_name)

        except Exception as e:
            logger.exception("Failed to insert data into Elasticsearch index '%s'", table_name)
            return False
        
        return True
