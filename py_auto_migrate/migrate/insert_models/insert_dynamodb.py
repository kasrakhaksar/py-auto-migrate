import pandas as pd

from botocore.exceptions import ClientError

from py_auto_migrate.migrate.base_models.base_dynamodb import BaseDynamoDB
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery
from py_auto_migrate.migrate.utils.type_mapper import dynamodb_value_mapper
from py_auto_migrate.core.logging import get_logger

logger = get_logger(__name__)


class InsertDynamoDB(BaseDynamoDB, BaseInsert):

    def __init__(self, dynamo_uri):
        super().__init__(dynamo_uri)


    def _serialize_item(self, item):

        return {
            key: dynamodb_value_mapper(value)
            for key, value in item.items()
        }

    def insert(self, data, table_name, ai_ask=None, ai_model=None):

        conn = self._connect()

        if conn is None:
            return False

        try:

            try:

                table = conn.Table(table_name)
                table.load()


            except ClientError as e:

                if e.response["Error"]["Code"] != "ResourceNotFoundException":
                    raise

                if "id" in data.columns:

                    dtype = data["id"].dtype

                    if pd.api.types.is_integer_dtype(dtype):
                        attr_type = "N"
                    else:
                        attr_type = "S"

                else:

                    attr_type = "S"

                table = conn.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {
                            "AttributeName": "id",
                            "KeyType": "HASH"
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            "AttributeName": "id",
                            "AttributeType": attr_type
                        }
                    ],
                    BillingMode="PAY_PER_REQUEST"
                )

                table.wait_until_exists()

            records = data.to_dict(
                orient="records"
            )

            new_items = []

            for index, item in enumerate(records):

                if "id" not in item:
                    item["id"] = str(index)

                item = self._serialize_item(item)

                new_items.append(item)

            with table.batch_writer() as batch:

                for item in new_items:
                    batch.put_item(Item=item)

            if ai_ask and ai_model:

                columns = [
                    f"`{col}`"
                    for col in data.columns
                ]

                generated_query = AIQuery(
                    ai_ask,
                    table_name,
                    "dynamodb",
                    columns
                ).nosql_generate(
                    model=ai_model
                )

                logger.debug("Generated AI query for DynamoDB table '%s'", table_name)

            return True

        except Exception as e:

            logger.exception("Failed to insert data into DynamoDB table '%s'", table_name)
            return False
