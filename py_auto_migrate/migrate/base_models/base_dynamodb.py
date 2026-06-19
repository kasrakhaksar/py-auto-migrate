import pandas as pd
import boto3
from botocore.exceptions import ClientError
from urllib.parse import urlparse, parse_qs
from py_auto_migrate.migrate.base_models.base import BaseModel


class BaseDynamoDB(BaseModel):

    def __init__(self, dynamo_uri):
        super().__init__(dynamo_uri)
        self._parse_uri()

    def _parse_uri(self):
        try:
            parsed = urlparse(self.uri)

            self.host = parsed.hostname
            self.port = parsed.port
            self.aws_access_key = parsed.username or None
            self.aws_secret_key = parsed.password or None
            self.table_prefix = parsed.path.lstrip("/") or "default"

            qs = parse_qs(parsed.query)
            self.region_name = qs.get("region", ["us-west-2"])[0]

        except Exception:
            self.aws_access_key = None
            self.aws_secret_key = None
            self.host = "localhost"
            self.port = 9000
            self.table_prefix = "default"
            self.region_name = "us-west-2"

    def _connect(self):
        try:
            endpoint = (
                f"http://{self.host}:{self.port}"
                if self.host and self.port
                else None
            )

            return boto3.resource(
                "dynamodb",
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                endpoint_url=endpoint
            )

        except Exception:
            return None

    def get_tables(self):
        conn = self._connect()

        if conn is None:
            return []

        try:
            return [
                t.name
                for t in conn.tables.all()
                if t.name.startswith(self.table_prefix)
            ]

        except ClientError:
            return []

    def read_table(self, table_name):

        conn = self._connect()

        if conn is None:
            return pd.DataFrame()

        try:
            table = conn.Table(table_name)

            response = table.scan()

            items = response.get("Items", [])

            return pd.DataFrame(items)

        except ClientError:
            return pd.DataFrame()