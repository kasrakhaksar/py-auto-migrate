from py_auto_migrate.base_models.base_mysql import BaseMySQL
from py_auto_migrate.insert_models.base import BaseInsert


class InsertMySQL(BaseMySQL, BaseInsert):
    def __init__(self, mysql_uri):
        super().__init__(mysql_uri)

    def insert(self, df, table_name):
        conn = self._connect()
        if conn is None:
            return

        cursor = conn.cursor()

        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if cursor.fetchone():
            conn.close()
            return

        dtype_map = {
            "int64": "BIGINT",
            "float64": "DOUBLE",
            "object": "TEXT",
            "bool": "TINYINT(1)",
            "datetime64[ns]": "DATETIME"
        }

        columns = ", ".join(
            [f"`{col}` {dtype_map.get(str(dtype), 'TEXT')}" for col, dtype in df.dtypes.items()]
        )
        cursor.execute(f"CREATE TABLE `{table_name}` ({columns})")
        conn.commit()

        placeholders = ", ".join(["%s"] * len(df.columns))
        values = [tuple(x) for x in df.to_numpy()]
        cursor.executemany(f"INSERT INTO `{table_name}` VALUES ({placeholders})", values)
        conn.commit()
        conn.close()