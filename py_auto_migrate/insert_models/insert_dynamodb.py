import json
from botocore.exceptions import ClientError
from py_auto_migrate.base_models.base_dynamodb import BaseDynamoDB
from py_auto_migrate.insert_models.base import BaseInsert
from py_auto_migrate.ai.ai_query import AIQuery


class InsertDynamoDB(BaseDynamoDB, BaseInsert):
    def __init__(self, dynamo_uri):
        super().__init__(dynamo_uri)

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        conn = self._connect()
        if conn is None:
            return

        if isinstance(data, str):
            data = json.loads(data)
        
        if not data:
            return

        table = conn.Table(table_name)

        try:
            table.load()
        except ClientError:
            table = conn.create_table(
                TableName=table_name,
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )
            table.wait_until_exists()



        with table.batch_writer() as batch:
            for idx, item in enumerate(data):
                if 'id' not in item:
                    item['id'] = str(idx)
                item = json.loads(json.dumps(item, default=str))
                batch.put_item(Item=item)


    
        if ai_ask and ai_model:
            sample_item = data[0] if data else {}
            columns = [f"`{col}`" for col in sample_item.keys()]
            ai_query_obj = AIQuery(ai_ask, table_name, 'dynamodb', columns)
            
            try:
                generated_query = ai_query_obj.nosql_generate(model=ai_model)
            except Exception as e:
                print(f"Error processing AI query: {e}")
                raise
            return

