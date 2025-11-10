from ..base_models.base_oracle import BaseOracle


class InsertOracle(BaseOracle):
    def __init__(self, oracle_uri):
        super().__init__(oracle_uri)

    def insert(self, df, table_name):
        conn = self._connect()
        cur = conn.cursor()

        dtype_map = {
            "int64": "NUMBER",
            "float64": "FLOAT",
            "object": "NVARCHAR2(4000)",
            "bool": "NUMBER(1)",
            "datetime64[ns]": "DATE"
        }
        columns = ", ".join(
            [f'"{col}" {dtype_map.get(str(dtype), "NVARCHAR2(4000)")} '
             for col, dtype in df.dtypes.items()]
        )
        cur.execute(f"""
            BEGIN
                EXECUTE IMMEDIATE 'CREATE TABLE "{table_name}" ({columns})';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE != -955 THEN RAISE; END IF;  -- -955 = table exists
            END;
        """)

        placeholders = ", ".join([f":{i+1}" for i in range(len(df.columns))])
        rows = [tuple(x) for x in df.to_numpy()]
        cur.executemany(f'INSERT INTO "{table_name}" VALUES ({placeholders})', rows)

        conn.commit()
        conn.close()
        print(f"✅ Inserted {len(df)} rows into Oracle table '{table_name}'")
