from clickhouse_driver import Client
from py_auto_migrate.insert_models.base import BaseInsert
from py_auto_migrate.ai.ai_query import AIQuery
import json


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

    def _infer_type(self, value):
        if value is None:
            return "String"
        if isinstance(value, int):
            return "Int64"
        elif isinstance(value, float):
            return "Float64"
        elif isinstance(value, bool):
            return "UInt8"
        else:
            return "String"

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        if isinstance(data, str):
            data = json.loads(data)
        
        if not data:
            return

        column_types = {}
        for col in data[0].keys():
            sample_value = data[0][col]
            column_types[col] = self._infer_type(sample_value)

        column_definitions = [f"`{col}` {col_type}" for col, col_type in column_types.items()]

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
            pass


        rows_to_insert = [tuple(row[col] for col in column_types.keys()) for row in data]
        columns_list = ', '.join([f"`{col}`" for col in column_types.keys()])
        placeholders = ', '.join(["%s"] * len(column_types))
        insert_query = f"INSERT INTO `{table_name}` ({columns_list}) VALUES ({placeholders})"

        try:
            self.client.execute(insert_query, rows_to_insert)
        except Exception as e:
            pass

        
        if ai_ask and ai_model:
            ai_query_obj = AIQuery(ai_ask, table_name, 'clickhouse', column_definitions)
            generated_query = ai_query_obj.nosql_generate(model=ai_model)
            
            try:
                self.client.execute(generated_query)
            except Exception as e:
                print(f"Error executing AI query: {e}")
                raise
            return


