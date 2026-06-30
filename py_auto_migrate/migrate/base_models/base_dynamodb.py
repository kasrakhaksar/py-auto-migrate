import boto3
import pandas as pd

from botocore.exceptions import ClientError
from urllib.parse import urlparse, parse_qs
from py_auto_migrate.migrate.base_models.base import BaseModel
from py_auto_migrate.migrate.utils.type_mapper import infer_data_types


class BaseDynamoDB(BaseModel):

    def __init__(self, dynamo_uri: str):
        super().__init__(dynamo_uri)
        self._parse_uri()


    def _parse_uri(self):
        parsed = urlparse(self.uri)
        self.host = parsed.hostname
        self.port = parsed.port
        self.aws_access_key = parsed.username
        self.aws_secret_key = parsed.password
        path = parsed.path.strip("/")
        self.table_prefix = path if path else None
        qs = parse_qs(parsed.query)
        self.region_name = qs.get("region", ["us-east-1"])[0]

    def _connect(self):

        endpoint = None

        if self.host:
            scheme = "https" if self.port == 443 else "http"
            endpoint = f"{scheme}://{self.host}"

            if self.port:
                endpoint += f":{self.port}"

        kwargs = {
            "service_name": "dynamodb",
            "region_name": self.region_name,
        }

        if endpoint:
            kwargs["endpoint_url"] = endpoint

        if self.aws_access_key:
            kwargs["aws_access_key_id"] = self.aws_access_key

        if self.aws_secret_key:
            kwargs["aws_secret_access_key"] = self.aws_secret_key

        return boto3.resource(**kwargs)

    def get_tables(self):
        conn = self._connect()

        try:
            tables = [
                table.name
                for table in conn.tables.all()
            ]

            if self.table_prefix:
                tables = [
                    table
                    for table in tables
                    if table.startswith(self.table_prefix)
                ]

            return tables

        except ClientError:
            return []

    def read_table(self, table_name):
        conn = self._connect()

        try:

            table = conn.Table(table_name)
            response = table.scan()
            items = response.get("Items", [])

            while "LastEvaluatedKey" in response:

                response = table.scan(
                    ExclusiveStartKey=response["LastEvaluatedKey"]
                )

                items.extend(
                    response.get("Items", [])
                )

            df = pd.DataFrame(items)
            df = infer_data_types(df)
            return df

        except ClientError:
            return pd.DataFrame()
    