import boto3
import pandas as pd
from botocore.exceptions import ClientError
from urllib.parse import urlparse, parse_qs


class BaseDynamoDB:
    def __init__(self, dynamo_uri):

        self.dynamo_uri = dynamo_uri
        self._client = None
        self._parse_uri()

    def _parse_uri(self):
        try:
            parsed = urlparse(self.dynamo_uri)
            self.host = parsed.hostname
            self.port = parsed.port 
            self.aws_access_key = parsed.username or None
            self.aws_secret_key = parsed.password or None
            self.table_prefix = parsed.path.lstrip('/') or 'default'

            qs = parse_qs(parsed.query)
            self.region_name = qs.get('region', [ 'us-west-2' ])[0]

        except Exception as e:
            print(f"❌ Invalid DynamoDB URI format: {e}")
            self.aws_access_key = None
            self.aws_secret_key = None
            self.host = 'localhost'
            self.port = 9000
            self.table_prefix = 'default'
            self.region_name = 'us-west-2'

    def _connect(self):
        if self._client:
            return self._client
        try:
            endpoint = f"http://{self.host}:{self.port}" if self.host and self.port else None
            self._client = boto3.resource(
                'dynamodb',
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                endpoint_url=endpoint
            )
            return self._client
        except Exception as e:
            print(f"❌ DynamoDB connection failed: {e}")
            return None

    def get_tables(self):
        conn = self._connect()
        if not conn:
            return []
        try:
            tables = [t.name for t in conn.tables.all() if t.name.startswith(self.table_prefix)]
            return tables
        except ClientError as e:
            print(f"❌ Error listing tables: {e}")
            return []

    def read_table(self, table_name):
        conn = self._connect()
        if not conn:
            return pd.DataFrame()
        try:
            table = conn.Table(table_name)
            response = table.scan()
            data = response.get("Items", [])
            return pd.DataFrame(data)
        except ClientError as e:
            print(f"❌ Error reading table {table_name}: {e}")
            return pd.DataFrame()
