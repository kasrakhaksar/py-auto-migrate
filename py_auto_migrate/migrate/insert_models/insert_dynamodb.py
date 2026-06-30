import json
import pandas as pd

from botocore.exceptions import ClientError

from py_auto_migrate.migrate.base_models.base_dynamodb import BaseDynamoDB
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery
from py_auto_migrate.migrate.utils.type_mapper import dynamodb_value_mapper


class InsertDynamoDB(BaseDynamoDB, BaseInsert):

    def __init__(self, dynamo_uri):
        super().__init__(dynamo_uri)


    def _serialize_item(self, item):

        return {
            key: dynamodb_value_mapper(value)
            for key, value in item.items()
        }

    def _existing_items(self, table):

        existing = set()

        response = table.scan()

        while True:

            for item in response.get("Items", []):

                existing.add(
                    json.dumps(
                        item,
                        sort_keys=True,
                        default=str
                    )
                )

            if "LastEvaluatedKey" not in response:
                break

            response = table.scan(
                ExclusiveStartKey=response["LastEvaluatedKey"]
            )

        return existing

    def insert(self, data, table_name, ai_ask=None, ai_model=None):

        conn = self._connect()

        if conn is None:
            return False

        try:

            try:

                table = conn.Table(table_name)
                table.load()

                existing_items = self._existing_items(table)

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

                existing_items = set()

            records = data.to_dict(
                orient="records"
            )

            new_items = []

            for index, item in enumerate(records):

                if "id" not in item:
                    item["id"] = str(index)

                item = self._serialize_item(item)

                unique_key = json.dumps(
                    item,
                    sort_keys=True,
                    default=str
                )

                if unique_key not in existing_items:
                    new_items.append(item)
                    existing_items.add(unique_key)

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

                print(generated_query)

            return True

        except Exception as e:

            print(e)
            return False