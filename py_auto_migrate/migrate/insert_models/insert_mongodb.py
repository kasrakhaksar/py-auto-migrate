from py_auto_migrate.migrate.base_models.base_mongodb import BaseMongoDB
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery
from py_auto_migrate.migrate.utils.type_mapper import mongodb_value_mapper
from py_auto_migrate.core.logging import get_logger

logger = get_logger(__name__)


class InsertMongoDB(BaseMongoDB, BaseInsert):
    def __init__(self, mongo_uri):
        super().__init__(mongo_uri)

    def insert(self, data, table_name, ai_ask=None, ai_model=None):

        db = self._connect()
        if db is None:
            return

        try:
            collection = db[table_name]

            new_docs = []

            for _, row in data.iterrows():
                row_dict = {
                    key: mongodb_value_mapper(value)
                    for key, value in row.to_dict().items()
                }
                new_docs.append(row_dict)

            if new_docs:
                collection.insert_many(new_docs, ordered=False)

            if ai_ask and ai_model:
                columns = [f"`{col}`" for col in data.columns]

                ai_query_obj = AIQuery(
                    ai_ask,
                    table_name,
                    "mongodb",
                    columns
                )

                generated_query = ai_query_obj.nosql_generate(model=ai_model)

                logger.debug("Generated AI query for MongoDB collection '%s'", table_name)

        except Exception as e:
            logger.exception("Failed to insert data into MongoDB collection '%s'", table_name)
            return False


        return True
