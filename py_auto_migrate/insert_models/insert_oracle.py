from py_auto_migrate.base_models.base_oracle import BaseOracle
from py_auto_migrate.insert_models.base import BaseInsert
from py_auto_migrate.ai.ai_query import AIQuery
import json


class InsertOracle(BaseOracle, BaseInsert):
    def __init__(self, oracle_uri):
        super().__init__(oracle_uri)

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        if isinstance(data, str):
            data = json.loads(data)
        
        if not data:
            return

        conn = self._conn()
        cur = conn.cursor()

        sample = data[0]
        columns = []
        
        for col, val in sample.items():
            if isinstance(val, int):
                col_type = "NUMBER"
            elif isinstance(val, float):
                col_type = "FLOAT"
            elif isinstance(val, bool):
                col_type = "NUMBER(1)"
            else:
                col_type = "NVARCHAR2(4000)"
            columns.append(f'"{col}" {col_type}')
        
        try:
            cur.execute(f'CREATE TABLE "{table_name}" ({", ".join(columns)})')
            conn.commit()
        except Exception:
            pass
        

        placeholders = ", ".join([f":{i+1}" for i in range(len(sample.keys()))])
        values = [tuple(row[col] for col in sample.keys()) for row in data]
        cur.executemany(f'INSERT INTO "{table_name}" VALUES ({placeholders})', values)
        conn.commit()

        if ai_ask and ai_model:
            ai_query_obj = AIQuery(ai_ask, table_name, 'oracle', columns)
            generated_query = ai_query_obj.sql_generate(model=ai_model)
            
            conn = self._conn()
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