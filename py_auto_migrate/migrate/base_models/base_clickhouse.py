import pandas as pd
from clickhouse_driver import Client
from py_auto_migrate.migrate.base_models.base import BaseModel
from py_auto_migrate.migrate.utils.type_mapper import infer_data_types
from clickhouse_driver import Client
import clickhouse_connect



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
        if self.port != 8123:
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
                pass

        try:
            client = clickhouse_connect.get_client(
                host=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                database=self.db_name
            )
            client.query("SELECT 1")
            return client
        except Exception:
            pass

        try:
            client = Client(
                host=self.host,
                port=9000,
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
            query = f"""
            SELECT name
            FROM system.tables
            WHERE database = '{self.db_name}'
            """

            if isinstance(client, Client):
                result = client.execute(query)
                client.disconnect()
                return [row[0] for row in result]

            else: 
                result = client.query(query)
                return [row[0] for row in result.result_rows]

        except Exception as e:
            print(f"❌ Error fetching tables: {e}")
            return []
        

    def read_table(self, table_name):
        client = self._connect()

        if client is None:
            return pd.DataFrame()

        query = f"SELECT * FROM `{table_name}`"

        try:
            if isinstance(client, Client):
                data = client.execute(query)

                columns = [
                    col[0]
                    for col in client.description_of_result_set
                ]

                client.disconnect()

                df = pd.DataFrame(data, columns=columns)

            else:
                result = client.query(query)

                df = pd.DataFrame(
                    result.result_rows,
                    columns=result.column_names
                )


            df = infer_data_types(df)
            return df

        except Exception as e:
            print(f"❌ Error reading table {table_name}: {e}")
            return pd.DataFrame()