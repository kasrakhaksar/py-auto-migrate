from py_auto_migrate.base_models.base_mariadb import BaseMariaDB
from mysqlSaver import Saver, CheckerAndReceiver, Creator, Connection



class InsertMariaDB(BaseMariaDB):
    def __init__(self, maria_uri):
        super().__init__(maria_uri)

    def insert(self, df, table_name):
        host, port, user, password, db_name = self._parse_maria_uri()

        tmp_conn = Connection.connect(host, port, user, password, None)
        Creator(tmp_conn).database_creator(db_name)
        tmp_conn.close()

        conn = self._connect()
        if conn is None:
            print(f"❌ Cannot connect to MariaDB database '{db_name}'. Insert aborted.")
            return

        checker = CheckerAndReceiver(conn)
        if checker.table_exist(table_name):
            print(f"⚠ Table '{table_name}' already exists in MariaDB. Skipping insert.")
        else:
            Saver(conn).sql_saver(df, table_name)
            print(f"✅ Inserted {len(df)} rows into MariaDB table '{table_name}'")

        conn.close()
