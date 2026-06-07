from py_auto_migrate.base_models.base_postgressql import BasePostgresSQL
from py_auto_migrate.insert_models.base import BaseInsert
from py_auto_migrate.ai.ai_query import AIQuery
import json


class InsertPostgresSQL(BasePostgresSQL, BaseInsert):
    def __init__(self, pg_uri):
        super().__init__(pg_uri)

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        conn = self._connect()
        if conn is None:
            return

        if isinstance(data, str):
            data = json.loads(data)

        if not data:
            return

        cur = conn.cursor()

        cur.execute("SELECT to_regclass(%s)", (table_name,))
        if not cur.fetchone()[0]:
            columns = list(data[0].keys())
            column_defs = []
            for col in columns:
                sample_value = data[0][col]
                if isinstance(sample_value, int):
                    dtype = 'INTEGER'
                elif isinstance(sample_value, float):
                    dtype = 'FLOAT'
                elif isinstance(sample_value, bool):
                    dtype = 'BOOLEAN'
                else:
                    dtype = 'TEXT'
                column_defs.append(f'"{col}" {dtype}')
            
            cur.execute(f'CREATE TABLE "{table_name}" ({", ".join(column_defs)})')
            conn.commit()


        placeholders = ', '.join(['%s'] * len(columns))
        values = [tuple(row[col] for col in columns) for row in data]
        cur.executemany(f'INSERT INTO "{table_name}" VALUES ({placeholders})', values)
        conn.commit()

        
        if ai_ask and ai_model:
            ai_query_obj = AIQuery(ai_ask, table_name, 'postgresql', column_defs)
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