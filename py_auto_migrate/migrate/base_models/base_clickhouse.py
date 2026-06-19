import pandas as pd
from clickhouse_driver import Client
from py_auto_migrate.migrate.base_models.base import BaseModel


class BaseClickHouse(BaseModel):
    def __init__(self, clickhouse_uri):
        super().__init__(clickhouse_uri)
        self.user, self.password, self.host, self.port, self.db_name = self._parse_clickhouse_uri()

    def _parse_clickhouse_uri(self):
        if self.uri.startswith("clickhouse://"):
            uri = self.uri.replace("clickhouse://", "")
        else:
            uri = self.uri

        if "@" in uri:
            auth_part, host_db_part = uri.split("@")
            if ":" in auth_part:
                user, password = auth_part.split(":")
            else:
                user, password = auth_part, ""
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
            client.execute("SELECT 1")
            return client
        except Exception as e:
            print(f"❌ Error connecting to ClickHouse: {e}")
            return None

    def get_tables(self):
        client = self._connect()

        if client is None:
            return []

        try:
            query = "SELECT name FROM system.tables WHERE database = %s"
            result = client.execute(query, [self.db_name])

            client.disconnect()

            return [row[0] for row in result]

        except Exception as e:
            print(f"❌ Error fetching tables: {e}")
            return []

    def read_table(self, table_name):
        client = self._connect()

        if client is None:
            return pd.DataFrame()

        try:
            query = f'SELECT * FROM `{table_name}`'

            data = client.execute(query)

            columns = [
                desc[0]
                for desc in client.description_of_result_set
            ]

            client.disconnect()

            return pd.DataFrame(
                data,
                columns=columns
            )

        except Exception as e:
            print(f"❌ Error reading table {table_name}: {e}")
            return pd.DataFrame()