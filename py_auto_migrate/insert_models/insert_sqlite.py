import os
import json
from py_auto_migrate.base_models.base_sqlite import BaseSQLite
from py_auto_migrate.insert_models.base import BaseInsert
from py_auto_migrate.ai.ai_query import AIQuery


class InsertSQLite(BaseSQLite, BaseInsert):
    def __init__(self, sqlite_uri):
        if sqlite_uri.startswith("sqlite:///"):
            sqlite_uri = sqlite_uri.replace("sqlite:///", "", 1)
        os.makedirs(os.path.dirname(sqlite_uri), exist_ok=True)
        super().__init__(sqlite_uri)

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        if isinstance(data, str):
            data = json.loads(data)
        
        if not data:
            return

        conn = self._connect()
        if conn is None:
            return

        columns = list(data[0].keys())
        column_defs = []
        for col in columns:
            sample_value = data[0][col]
            if isinstance(sample_value, int):
                col_type = "INTEGER"
            elif isinstance(sample_value, float):
                col_type = "REAL"
            else:
                col_type = "TEXT"
            column_defs.append(f'"{col}" {col_type}')
        
        cursor = conn.cursor()
        cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(column_defs)})')
        

        placeholders = ", ".join(["?"] * len(columns))
        values = [tuple(row[col] for col in columns) for row in data]
        cursor.executemany(f'INSERT INTO "{table_name}" VALUES ({placeholders})', values)
        conn.commit()


        if ai_ask and ai_model:
            ai_query_obj = AIQuery(ai_ask, table_name, 'sqlite', column_defs)
            generated_query = ai_query_obj.sql_generate(model=ai_model)
            
            conn = self._connect()
            if conn is None:
                return
            cursor = conn.cursor()
            try:
                cursor.execute(generated_query)
                conn.commit()
                print(f"AI-generated INSERT query executed successfully: {generated_query}")
            except Exception as e:
                print(f"Error executing AI query: {e}")
                raise
            finally:
                conn.close()
            return


        conn.close()