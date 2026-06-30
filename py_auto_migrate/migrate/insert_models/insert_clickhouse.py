import clickhouse_connect
from clickhouse_driver import Client as NativeClient

from py_auto_migrate.migrate.base_models.base_clickhouse import BaseClickHouse
from py_auto_migrate.migrate.insert_models.base import BaseInsert
from py_auto_migrate.migrate.ai.ai_query import AIQuery
from py_auto_migrate.migrate.utils.type_mapper import sql_type_mapper


class InsertClickHouse(BaseClickHouse, BaseInsert):
    def __init__(self, clickhouse_uri):
        super().__init__(clickhouse_uri)
        self._ensure_database()



    def _ensure_database(self):
        if self.port == 8123:
            client = clickhouse_connect.get_client(
                host=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                database="default"
            )

            client.command(
                f"CREATE DATABASE IF NOT EXISTS `{self.db_name}`"
            )

            client.disconnect()

        else:
            client = NativeClient(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database="default"
            )

            client.execute(
                f"CREATE DATABASE IF NOT EXISTS `{self.db_name}`"
            )

            client.disconnect()

    def insert(self, data, table_name, ai_ask=None, ai_model=None):

        client = self._connect()

        if client is None:
            return False

        try:
            column_types = {}

            for col, dtype in data.dtypes.items():
                column_types[col] = sql_type_mapper(dtype, "clickhouse")

            column_defs = [
                f"`{col}` {dtype}"
                for col, dtype in column_types.items()
            ]

            create_query = f"""
            CREATE TABLE IF NOT EXISTS `{table_name}`
            (
                {", ".join(column_defs)}
            )
            ENGINE = MergeTree()
            ORDER BY tuple()
            """

            columns = list(column_types.keys())

            values = list(
                data[columns].itertuples(
                    index=False,
                    name=None
                )
            )

            if isinstance(client, NativeClient):

                client.execute(create_query)

                if values:
                    insert_query = f"""
                    INSERT INTO `{table_name}`
                    ({",".join(f"`{c}`" for c in columns)})
                    VALUES
                    """

                    client.execute(insert_query, values)

                if ai_ask and ai_model:
                    ai_query = AIQuery(
                        ai_ask,
                        table_name,
                        "clickhouse",
                        column_defs
                    )

                    generated_query = ai_query.nosql_generate(
                        model=ai_model
                    )

                    client.execute(generated_query)

            else:

                client.command(create_query)

                if values:
                    client.insert(
                        table=table_name,
                        data=values,
                        column_names=columns
                    )

                if ai_ask and ai_model:
                    ai_query = AIQuery(
                        ai_ask,
                        table_name,
                        "clickhouse",
                        column_defs
                    )

                    generated_query = ai_query.nosql_generate(
                        model=ai_model
                    )

                    client.command(generated_query)

            return True


        except Exception as e:
            print(e)
            return False

        finally:
            client.disconnect()