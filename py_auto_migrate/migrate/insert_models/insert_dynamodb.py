from botocore.exceptions import ClientError
from py_auto_migrate.migrate.base_models.base_dynamodb import BaseDynamoDB
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery

class InsertDynamoDB(BaseDynamoDB, BaseInsert):
    def __init__(self, dynamo_uri):
        super().__init__(dynamo_uri)

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        conn = self._connect()

        if conn is None:
            return

        if data is None or data.empty:
            return

        try:
            table = conn.Table(table_name)

            try:
                table.load()
                table_exists = True

            except ClientError:
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
                            "AttributeType": "S"
                        }
                    ],
                    BillingMode="PAY_PER_REQUEST"
                )

                table.wait_until_exists()
                table_exists = False

            existing_items = set()

            if table_exists:
                scan = table.scan(
                    Limit=1000
                )

                items = scan.get("Items", [])

                for item in items:
                    existing_items.add(tuple(item.values()))

            records = data.to_dict(
                orient="records"
            )

            new_items = []

            for index, item in enumerate(records):
                if "id" not in item:
                    item["id"] = str(index)

                key = tuple(item.values())

                if key not in existing_items:
                    new_items.append(item)
                    existing_items.add(key)

            with table.batch_writer() as batch:
                for item in new_items:
                    batch.put_item(
                        Item=item
                    )

            if ai_ask and ai_model:
                columns = [
                    f"`{col}`"
                    for col in data.columns
                ]

                ai_query_obj = AIQuery(
                    ai_ask,
                    table_name,
                    "dynamodb",
                    columns
                )

                generated_query = ai_query_obj.nosql_generate(
                    model=ai_model
                )

                print(generated_query)

        except Exception:
            pass

        finally:
            conn.close()