from clickhouse_driver import Client
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery
from py_auto_migrate.migrate.utils.type_mapper import sql_type_mapper

class InsertClickHouse(BaseInsert):
    def __init__(self, clickhouse_uri):
        self.clickhouse_uri = clickhouse_uri
        self.user, self.password, self.host, self.port, self.db_name = self._parse_clickhouse_uri()
        self._ensure_database()
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

    def _ensure_database(self):
        client = Client(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database="default"
        )

        client.execute(f"CREATE DATABASE IF NOT EXISTS `{self.db_name}`")

    def _connect(self):
        try:
            client = Client(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.db_name
            )

            client.execute("SELECT 1")
            return client

        except Exception:
            return None

    def _infer_type(self, value):
        if value is None:
            return "String"

        if isinstance(value, bool):
            return "UInt8"

        if isinstance(value, int):
            return "Int64"

        if isinstance(value, float):
            return "Float64"

        return "String"

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        if data is None or data.empty:
            return

        try:
            column_types = {}

            for col, dtype in data.dtypes.items():
                column_types[col] = sql_type_mapper(dtype, "clickhouse")

            column_definitions = [
                f"`{col}` {dtype}"
                for col, dtype in column_types.items()
            ]

            create_query = f"""
            CREATE TABLE IF NOT EXISTS `{table_name}`
            (
                {', '.join(column_definitions)}
            )
            ENGINE = MergeTree()
            ORDER BY tuple()
            """

            self.client.execute(create_query)

            rows = list(
                data[list(column_types.keys())]
                .itertuples(index=False, name=None)
            )

            columns = ", ".join(
                f"`{c}`"
                for c in column_types.keys()
            )

            values = ", ".join(["%s"] * len(column_types))

            insert_query = f"""
            INSERT INTO `{table_name}`
            ({columns})
            VALUES ({values})
            """

            self.client.execute(insert_query, rows)

            if ai_ask and ai_model:
                ai_query = AIQuery(
                    ai_ask,
                    table_name,
                    "clickhouse",
                    column_definitions
                )

                generated_query = ai_query.nosql_generate(model=ai_model)

                self.client.execute(generated_query)

        except Exception:
            pass