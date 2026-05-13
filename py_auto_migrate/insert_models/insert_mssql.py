from py_auto_migrate.base_models.base_mssql import BaseMSSQL
from py_auto_migrate.insert_models.base import BaseInsert
from py_auto_migrate.ai.ai_query import AIQuery
import json


class InsertMSSQL(BaseMSSQL, BaseInsert):
    def __init__(self, mssql_uri):
        super().__init__(mssql_uri)

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        if isinstance(data, str):
            data = json.loads(data)
        
        if not data:
            return

        conn = self._connect()
        if conn is None:
            return

        cur = conn.cursor()

        cur.execute(
            f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}'"
        )
        if cur.fetchone()[0] == 0:
            sample = data[0]
            columns = []
            
            for col, val in sample.items():
                if isinstance(val, int):
                    col_type = "BIGINT"
                elif isinstance(val, float):
                    col_type = "FLOAT"
                elif isinstance(val, bool):
                    col_type = "BIT"
                else:
                    col_type = "NVARCHAR(MAX)"
                columns.append(f"[{col}] {col_type}")
            
            cur.execute(f"CREATE TABLE [{table_name}] ({', '.join(columns)})")
            conn.commit()
        

        sample = data[0]
        placeholders = ", ".join(["?"] * len(sample.keys()))
        values = [[row[col] for col in sample.keys()] for row in data]
        cur.fast_executemany = True
        cur.executemany(f"INSERT INTO [{table_name}] VALUES ({placeholders})", values)
        conn.commit()


        if ai_ask and ai_model:
            ai_query_obj = AIQuery(ai_ask, table_name, 'mssql', columns)
            generated_query = ai_query_obj.sql_generate(model=ai_model)
            
            conn = self._connect()
            if conn is None:
                return
            cur = conn.cursor()
            try:
                cur.execute(generated_query)
                conn.commit()
            except Exception as e:
                print(f"Error executing AI query: {e}")
                raise
            finally:
                conn.close()
            return
        

        conn.close()