from ..base_models.base_mssql import BaseMSSQL



class InsertMSSQL(BaseMSSQL):
    def __init__(self, mssql_uri):
        super().__init__(mssql_uri)

    def insert(self, df, table_name):

        conn = self._connect()
        if conn is None:
            print(f"❌ Cannot connect to SQL Server database. Insert aborted.")
            return

        cur = conn.cursor()

        dtype_map = {
            "int64": "BIGINT",
            "float64": "FLOAT",
            "object": "NVARCHAR(MAX)",
            "bool": "BIT",
            "datetime64[ns]": "DATETIME"
        }

        cur.execute(
            f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}'"
        )
        if cur.fetchone()[0] > 0:
            print(f"⚠ Table '{table_name}' already exists in SQL Server. Skipping insert.")
            conn.close()
            return

        columns = ", ".join(
            [f"[{col}] {dtype_map.get(str(dtype), 'NVARCHAR(MAX)')}" for col, dtype in df.dtypes.items()]
        )
        cur.execute(f"CREATE TABLE [{table_name}] ({columns})")
        conn.commit()

        placeholders = ", ".join(["?"] * len(df.columns))
        cur.fast_executemany = True
        cur.executemany(f"INSERT INTO [{table_name}] VALUES ({placeholders})", df.values.tolist())
        conn.commit()
        conn.close()

        print(f"✅ Inserted {len(df)} rows into SQL Server table '{table_name}'")