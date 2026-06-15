import json
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

        try:
            if isinstance(data, str):
                data = json.loads(data)

            if not data:
                return

            table = conn.Table(table_name)

            try:
                table.load()
                table_exists = True
            except ClientError:
                table = conn.create_table(
                    TableName=table_name,
                    KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                    AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
                    BillingMode="PAY_PER_REQUEST",
                )
                table.wait_until_exists()
                table_exists = False

            existing_items = set()

            if table_exists:
                scan = table.scan(Limit=1000)
                items = scan.get("Items", [])
                existing_items = set(
                    json.dumps(i, sort_keys=True, default=str) for i in items
                )

            new_items = []

            if isinstance(data, list):
                for idx, item in enumerate(data):
                    if "id" not in item:
                        item["id"] = str(idx)

                    item_str = json.dumps(item, sort_keys=True, default=str)

                    if item_str not in existing_items:
                        new_items.append(item)
                        existing_items.add(item_str)
            else:
                if "id" not in data:
                    data["id"] = "0"

                item_str = json.dumps(data, sort_keys=True, default=str)

                if item_str not in existing_items:
                    new_items.append(data)

            with table.batch_writer() as batch:
                for item in new_items:
                    batch.put_item(Item=json.loads(json.dumps(item, default=str)))

            if ai_ask and ai_model:
                sample_item = new_items[0] if new_items else (data[0] if isinstance(data, list) else data)
                columns = [f"`{col}`" for col in sample_item.keys()] if isinstance(sample_item, dict) else []

                ai_query_obj = AIQuery(ai_ask, table_name, "dynamodb", columns)
                generated_query = ai_query_obj.nosql_generate(model=ai_model)

                print(generated_query)

        except Exception:
            pass
        finally:
            conn.close()