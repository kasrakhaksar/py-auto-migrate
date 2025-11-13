import json
from botocore.exceptions import ClientError
from py_auto_migrate.base_models.base_dynamodb import BaseDynamoDB


class InsertDynamoDB(BaseDynamoDB):
    def __init__(self, dynamo_uri):
        super().__init__(dynamo_uri)

    def insert(self, df, table_name):
        conn = self._connect()
        if conn is None:
            print("❌ Cannot connect to DynamoDB. Insert aborted.")
            return

        if df.empty:
            print("⚠ Empty DataFrame, nothing to insert.")
            return

        table = conn.Table(table_name)

        try:
            table.load()
        except ClientError:
            print(f"⚙ Creating new DynamoDB table '{table_name}' ...")
            table = conn.create_table(
                TableName=table_name,
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )
            table.wait_until_exists()

        with table.batch_writer() as batch:
            for idx, row in df.iterrows():
                item = row.to_dict()
                if 'id' not in item:
                    item['id'] = str(idx)
                item = json.loads(json.dumps(item, default=str))
                batch.put_item(Item=item)

        print(f"✅ Inserted {len(df)} items into DynamoDB table '{table_name}'")
