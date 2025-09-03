from pymongo import MongoClient
from mysqlSaver import Connection, Saver, CheckerAndReceiver, Creator
import pandas as pd
import psycopg2
import sqlite3
from .tools import map_dtype_to_postgres



class PostgresConnection:
    @staticmethod
    def connect(host, port, user, password, db_name=None):
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=db_name if db_name else "postgres"
            )
            return conn

        except psycopg2.OperationalError as e:
            if db_name:  
                try:
                    temp_conn = psycopg2.connect(
                        host=host,
                        port=port,
                        user=user,
                        password=password,
                        dbname="postgres"
                    )
                    temp_conn.autocommit = True
                    cur = temp_conn.cursor()

                    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
                    exists = cur.fetchone()
                    if not exists:
                        cur.execute(f'CREATE DATABASE "{db_name}"')
                        print(f"✅ Database '{db_name}' created in PostgreSQL")
                    else:
                        print(f"⚠ Database '{db_name}' already exists")

                    cur.close()
                    temp_conn.close()

                    conn = psycopg2.connect(
                        host=host,
                        port=port,
                        user=user,
                        password=password,
                        dbname=db_name
                    )
                    return conn

                except Exception as e2:
                    print(f"❌ Failed to create PostgreSQL database '{db_name}': {e2}")
                    return None
            else:
                print(f"❌ PostgreSQL Connection Error (no db_name given): {e}")
                return None

        except Exception as e:
            print(f"❌ PostgreSQL Connection Error: {e}")
            return None



# ========== PostgreSQL → MySQL ==========
class PostgresToMySQL:
    def __init__(self, pg_uri, mysql_uri):
        self.pg_uri = pg_uri
        self.mysql_uri = mysql_uri

    def migrate_one(self, table_name):
        pg_conn = self._get_postgres_conn(self.pg_uri)
        df = pd.read_sql(f'SELECT * FROM "{table_name}"', pg_conn)
        pg_conn.close()

        host, port, user, password, db_name = self._parse_mysql_uri(self.mysql_uri)

        temp_conn = Connection.connect(host, port, user, password, None)
        creator = Creator(temp_conn)
        creator.database_creator(db_name)
        temp_conn.close()

        conn = Connection.connect(host, port, user, password, db_name)

        checker = CheckerAndReceiver(conn)
        if checker.table_exist(table_name):
            print(f"⚠ Table '{table_name}' already exists in MySQL. Skipping.")
            conn.close()
            return

        saver = Saver(conn)
        saver.sql_saver(df, table_name)
        conn.close()
        print(f"✅ Migrated {len(df)} rows from PostgreSQL to MySQL table '{table_name}'")

    def migrate_all(self):
        
        pg_conn = self._get_postgres_conn(self.pg_uri)
        cursor = pg_conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        pg_conn.close()

        for table in tables:
            print(f"➡ Migrating PostgreSQL table: {table}")
            self.migrate_one(table)

    def _get_postgres_conn(self, pg_uri):
        user_pass, host_db = pg_uri.replace("postgresql://", "").split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 5432
        return PostgresConnection.connect(host, port, user, password, db_name)

    def _parse_mysql_uri(self, mysql_uri):
        mysql_uri = mysql_uri.replace("mysql://", "")
        user_pass, host_db = mysql_uri.split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 3306
        return host, port, user, password, db_name


# ========== PostgreSQL → Mongo ==========
class PostgresToMongo:
    def __init__(self, pg_uri, mongo_uri):
        self.pg_uri = pg_uri
        self.mongo_uri = mongo_uri

    def migrate_one(self, table_name):
        pg_conn = self._get_postgres_conn(self.pg_uri)
        df = pd.read_sql(f'SELECT * FROM "{table_name}"', pg_conn)
        pg_conn.close()

        client = MongoClient(self.mongo_uri)
        db_name = self.mongo_uri.split("/")[-1]
        db = client[db_name]

        if table_name in db.list_collection_names():
            print(f"⚠ Collection '{table_name}' already exists in MongoDB. Skipping.")
            return

        db[table_name].insert_many(df.to_dict("records"))
        print(f"✅ Migrated {len(df)} rows from PostgreSQL to MongoDB collection '{table_name}'")

    def migrate_all(self):
        pg_conn = self._get_postgres_conn(self.pg_uri)
        cursor = pg_conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        pg_conn.close()

        for table in tables:
            print(f"➡ Migrating PostgreSQL table: {table}")
            self.migrate_one(table)

    def _get_postgres_conn(self, pg_uri):
        user_pass, host_db = pg_uri.replace("postgresql://", "").split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 5432
        return PostgresConnection.connect(host, port, user, password, db_name)


# ========== PostgreSQL → PostgreSQL ==========
class PostgresToPostgres:
    def __init__(self, source_uri, target_uri):
        self.source_uri = source_uri
        self.target_uri = target_uri

    def migrate_one(self, table_name):
        source_conn = self._get_postgres_conn(self.source_uri)
        df = pd.read_sql(f'SELECT * FROM "{table_name}"', source_conn)
        source_conn.close()

        target_conn = self._get_postgres_conn(self.target_uri)
        cursor = target_conn.cursor()

        cursor.execute(f"SELECT to_regclass('{table_name}')")
        if cursor.fetchone()[0]:
            print(f"⚠ Table '{table_name}' already exists in target PostgreSQL. Skipping.")
            target_conn.close()
            return

        columns = ', '.join([f'"{col}" {map_dtype_to_postgres(df[col].dtype)}' for col in df.columns])
        cursor.execute(f'CREATE TABLE "{table_name}" ({columns})')

        for _, row in df.iterrows():
            values = tuple(row.astype(str))
            placeholders = ', '.join(['%s'] * len(values))
            cursor.execute(f'INSERT INTO "{table_name}" VALUES ({placeholders})', values)

        target_conn.commit()
        target_conn.close()
        print(f"✅ Migrated {len(df)} rows from PostgreSQL to PostgreSQL table '{table_name}'")

    def migrate_all(self):
        source_conn = self._get_postgres_conn(self.source_uri)
        cursor = source_conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        source_conn.close()

        for table in tables:
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)

    def _get_postgres_conn(self, pg_uri):
        user_pass, host_db = pg_uri.replace("postgresql://", "").split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 5432
        return PostgresConnection.connect(host, port, user, password, db_name)
    

# ========== PostgreSQL → SQLite ==========
class PostgresToSQLite:
    def __init__(self, pg_uri, sqlite_file):
        self.pg_uri = pg_uri
        self.sqlite_file = sqlite_file

    def migrate_one(self, table_name):
        pg_conn = self._get_postgres_conn(self.pg_uri)
        df = pd.read_sql(f'SELECT * FROM "{table_name}"', pg_conn)
        pg_conn.close()

        conn_sqlite = sqlite3.connect(self.sqlite_file)
        cursor = conn_sqlite.cursor()

        columns = []
        dtype_map = {
            'int32': 'INTEGER',
            'int64': 'INTEGER',
            'float64': 'REAL',
            'object': 'TEXT',
            'bool': 'BOOLEAN',
            'datetime64[ns]': 'TEXT'
        }
        for col, dtype in df.dtypes.items():
            col_type = dtype_map.get(str(dtype), 'TEXT')
            columns.append(f'"{col}" {col_type}')
        columns_str = ", ".join(columns)
        cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_str})')
        conn_sqlite.commit()

        placeholders = ", ".join(["?"] * len(df.columns))
        cursor.executemany(f'INSERT INTO "{table_name}" VALUES ({placeholders})', df.values.tolist())
        conn_sqlite.commit()
        conn_sqlite.close()
        print(f"✅ Migrated {len(df)} rows from PostgreSQL to SQLite table '{table_name}'")

    def migrate_all(self):
        pg_conn = self._get_postgres_conn(self.pg_uri)
        cursor = pg_conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        pg_conn.close()

        for table in tables:
            print(f"➡ Migrating PostgreSQL table: {table}")
            self.migrate_one(table)

    def _get_postgres_conn(self, pg_uri):
        user_pass, host_db = pg_uri.replace("postgresql://", "").split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 5432
        return PostgresConnection.connect(host, port, user, password, db_name)