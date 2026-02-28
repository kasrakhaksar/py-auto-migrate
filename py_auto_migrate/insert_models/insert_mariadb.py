from py_auto_migrate.base_models.base_mariadb import BaseMariaDB
from py_auto_migrate.insert_models.base import BaseInsert
from mysqlSaver import Saver, CheckerAndReceiver, Creator, Connection


class InsertMariaDB(BaseMariaDB, BaseInsert):
    def __init__(self, maria_uri):
        super().__init__(maria_uri)

    def insert(self, df, table_name):
        host, port, user, password, db_name = self._parse_maria_uri()

        tmp_conn = Connection.connect(host, port, user, password, None)
        Creator(tmp_conn).database_creator(db_name)
        tmp_conn.close()

        conn = self._connect()
        if conn is None:
            return

        checker = CheckerAndReceiver(conn)
        if checker.table_exist(table_name):
            pass
        else:
            Saver(conn).sql_saver(df, table_name)

        conn.close()