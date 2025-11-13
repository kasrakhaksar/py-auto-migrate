from py_auto_migrate.base_models.base_mysql import BaseMySQL

class InsertMySQL(BaseMySQL):
    def __init__(self, mysql_uri):
        super().__init__(mysql_uri)

    def insert(self, df, table_name):
        conn = self._connect()
        if conn is None:
            print(f"❌ Cannot connect to MySQL database. Insert aborted.")
            return

        cursor = conn.cursor()

        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if cursor.fetchone():
            print(f"⚠ Table '{table_name}' already exists in MySQL. Skipping insert.")
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

        print(f"✅ Inserted {len(df)} rows into MySQL table '{table_name}'")
