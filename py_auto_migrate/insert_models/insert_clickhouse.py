import pandas as pd
from clickhouse_driver import Client
from py_auto_migrate.insert_models.base import BaseInsert


class InsertClickHouse(BaseInsert):
    def __init__(self, clickhouse_uri):
        self.clickhouse_uri = clickhouse_uri
        self.user, self.password, self.host, self.port, self.db_name = self._parse_clickhouse_uri()
        self.client = self._connect()

    def _parse_clickhouse_uri(self):
        if self.clickhouse_uri.startswith("clickhouse://"):
            uri = self.clickhouse_uri.replace("clickhouse://", "")
        else:
            uri = self.clickhouse_uri

        if "@" in uri:
            auth_part, host_db_part = uri.split("@")
            user, password = (auth_part.split(":") + ["default", ""])[:2]
        else:
            user, password = "default", ""
            host_db_part = uri

        if "/" in host_db_part:
            host_port, db_name = host_db_part.split("/", 1)
        else:
            host_port, db_name = host_db_part, ""

        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host, port = host_port, 9000

        return user, password, host, port, db_name

    def _connect(self):
        try:
            client = Client(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.db_name
            )
            client.execute('SELECT 1')
            return client
        except Exception as e:
            raise

    def _map_pandas_to_clickhouse_type(self, pd_type):
        pd_type_str = str(pd_type)
        if 'int' in pd_type_str:
            return "Int64"
        elif 'float' in pd_type_str:
            return "Float64"
        elif 'datetime64' in pd_type_str:
            return "DateTime"
        elif 'bool' in pd_type_str:
            return "UInt8"
        else:
            return "String"

    def insert(self, df: pd.DataFrame, table_name: str):
        column_definitions = []
        for col, dtype in df.dtypes.items():
            ch_type = self._map_pandas_to_clickhouse_type(dtype)
            column_definitions.append(f"`{col}` {ch_type}")

        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS `{table_name}`
        (
            {', '.join(column_definitions)}
        )
        ENGINE = MergeTree()
        ORDER BY tuple();
        """

        try:
            self.client.execute(create_table_query)
        except Exception as e:
            return

        rows_to_insert = [tuple(x) for x in df.where(
            pd.notnull(df), None).to_numpy()]

        columns_list = ', '.join([f"`{col}`" for col in df.columns])
        placeholders = ', '.join(["%s"] * len(df.columns))
        insert_query = f"INSERT INTO `{table_name}` ({columns_list}) VALUES ({placeholders})"

        try:
            self.client.execute(insert_query, rows_to_insert)
        except Exception as e:
            pass