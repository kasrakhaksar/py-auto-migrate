import json
from py_auto_migrate.base_models.base_mysql import BaseMySQL
from py_auto_migrate.insert_models.base import BaseInsert
from py_auto_migrate.ai.ai_query import AIQuery


class InsertMySQL(BaseMySQL, BaseInsert):
    def __init__(self, mysql_uri):
        super().__init__(mysql_uri)

    def insert(self, data, table_name, ai_ask=None, ai_model=None):
        if isinstance(data, str):
            data = json.loads(data)
        
        if not data:
            return

        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if not cursor.fetchone():
            sample = data[0]
            columns = []
            
            for col, val in sample.items():
                if isinstance(val, int):
                    col_type = "BIGINT"
                elif isinstance(val, float):
                    col_type = "DOUBLE"
                elif isinstance(val, bool):
                    col_type = "TINYINT(1)"
                else:
                    col_type = "TEXT"
                columns.append(f"`{col}` {col_type}")
            
            cursor.execute(f"CREATE TABLE `{table_name}` ({', '.join(columns)})")
            conn.commit()
        


        sample = data[0]
        placeholders = ", ".join(["%s"] * len(sample.keys()))
        values = [tuple(row[col] for col in sample.keys()) for row in data]
        cursor.executemany(f"INSERT INTO `{table_name}` VALUES ({placeholders})", values)
        conn.commit()


        if ai_ask and ai_model:
            ai_query_obj = AIQuery(ai_ask, table_name, 'mysql', columns)
            generated_query = ai_query_obj.sql_generate(model=ai_model)
            
            conn = self._connect()
            cursor = conn.cursor()
            try:
                cursor.execute(generated_query)
                conn.commit()
            except Exception as e:
                print(f"Error executing AI query: {e}")
                raise
            finally:
                conn.close()
            return
        

        conn.close()