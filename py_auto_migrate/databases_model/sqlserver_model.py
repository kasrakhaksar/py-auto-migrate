import os
import pandas as pd
import sqlite3
import pyodbc
import psycopg2
from pymongo import MongoClient
from mysqlSaver import Connection, Saver, CheckerAndReceiver, Creator
from .tools import map_dtype_to_postgres


# ========= Base SQL Server =========
class BaseSQLServer:
    def __init__(self, mssql_uri):
        self.mssql_uri = mssql_uri

    def _parse_mssql_uri(self, uri=None):
        if uri is None:
            uri = self.mssql_uri
        uri = uri.replace("mssql://", "")
        if uri.startswith("@") or "@" not in uri:
            if uri.startswith("@"):
                uri = uri[1:]
            host_port, db_name = uri.split("/", 1)
            if ":" in host_port:
                host, port = host_port.split(":")
            else:
                host, port = host_port, "1433"
            return {"auth": "windows", "host": host, "port": port, "database": db_name}
        else:
            user_pass, host_db = uri.split("@", 1)
            user, password = user_pass.split(":", 1)
            host_port, db_name = host_db.split("/", 1)
            if ":" in host_port:
                host, port = host_port.split(":")
            else:
                host, port = host_port, "1433"
            return {
                "auth": "sql",
                "host": host,
                "port": port,
                "database": db_name,
                "user": user,
                "password": password
            }

    def _connect(self):
        cfg = self._parse_mssql_uri()
        if cfg["auth"] == "windows":
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={cfg['host']},{cfg['port']};DATABASE={cfg['database']};Trusted_Connection=yes;"
        else:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={cfg['host']},{cfg['port']};DATABASE={cfg['database']};UID={cfg['user']};PWD={cfg['password']};"
        return pyodbc.connect(conn_str)

    def get_tables(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
        tables = [r[0] for r in cur.fetchall()]
        conn.close()
        return tables

    def read_table(self, table_name):
        conn = self._connect()
        df = pd.read_sql(f"SELECT * FROM [{table_name}]", conn)
        conn.close()
        df = df.fillna(0)
        return df

# ========= SQL Server → MySQL =========
class SQLServerToMySQL(BaseSQLServer):
    def __init__(self, mssql_uri, mysql_uri):
        super().__init__(mssql_uri)
        self.mysql_uri = mysql_uri

    def _parse_mysql_uri(self, uri):
        uri = uri.replace("mysql://", "")
        user_pass, host_db = uri.split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 3306
        return host, port, user, password, db_name

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if df.empty:
            print(f"⚠ Table '{table_name}' is empty in SQL Server.")
            return

        host, port, user, password, db_name = self._parse_mysql_uri(self.mysql_uri)

        temp_conn = Connection.connect(host, port, user, password, None)
        creator = Creator(temp_conn)
        creator.database_creator(db_name)
        temp_conn.close()

        conn = Connection.connect(host, port, user, password, db_name)
        checker = CheckerAndReceiver(conn)

        if checker.table_exist(table_name):
            print(f"⚠ Table '{table_name}' already exists in MySQL. Skipping insert.")
        else:
            saver = Saver(conn)
            saver.sql_saver(df, table_name)
            print(f"✅ Migrated {len(df)} rows from SQL Server → MySQL table '{table_name}'")

        conn.close()

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)


# ========= SQL Server → PostgreSQL =========
class SQLServerToPostgres(BaseSQLServer):
    def __init__(self, mssql_uri, pg_uri):
        super().__init__(mssql_uri)
        self.pg_uri = pg_uri

    def _connect_postgres(self):
        uri = self.pg_uri.replace("postgresql://", "")
        user_pass, host_db = uri.split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host, port = host_port, 5432
        return psycopg2.connect(dbname=db_name, user=user, password=password, host=host, port=port)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if df.empty:
            return
        conn = self._connect_postgres()
        cur = conn.cursor()
        cur.execute("SELECT to_regclass(%s)", (table_name,))
        if cur.fetchone()[0]:
            print(f"⚠ Table '{table_name}' already exists in PostgreSQL. Skipping.")
            conn.close()
            return
        columns = ', '.join([f'"{c}" {map_dtype_to_postgres(df[c].dtype)}' for c in df.columns])
        cur.execute(f'CREATE TABLE "{table_name}" ({columns})')
        for _, row in df.iterrows():
            cur.execute(f'INSERT INTO "{table_name}" VALUES ({", ".join(["%s"] * len(row))})', tuple(row))
        conn.commit()
        conn.close()
        print(f"✅ Migrated {len(df)} rows from SQL Server to PostgreSQL table '{table_name}'")

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)



# ========= SQL Server → SQLite =========
class SQLServerToSQLite(BaseSQLServer):
    def __init__(self, mssql_uri, sqlite_uri):
        super().__init__(mssql_uri)
        self.sqlite_file = self._prepare(sqlite_uri)

    def _prepare(self, uri):
        if uri.startswith("sqlite:///"):
            uri = uri.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(uri), exist_ok=True)
        return uri

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if df.empty:
            return
        conn = sqlite3.connect(self.sqlite_file)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()
        print(f"✅ Migrated {len(df)} rows from SQL Server to SQLite table '{table_name}'")

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)




# ========= SQL Server → MariaDB =========
class SQLServerToMaria(BaseSQLServer):
    def __init__(self, mssql_uri, maria_uri):
        super().__init__(mssql_uri)
        self.maria_uri = maria_uri

    def _parse_maria_uri(self, uri):
        uri = uri.replace("mariadb://", "").replace("mysql://", "")
        user_pass, host_db = uri.split("@")
        user, password = user_pass.split(":")
        host_port, db_name = host_db.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host, port = host_port, 3309
        return host, port, user, password, db_name

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if df.empty:
            print(f"⚠ Table '{table_name}' is empty in SQL Server.")
            return

        host, port, user, password, db_name = self._parse_maria_uri(self.maria_uri)

        temp_conn = Connection.connect(host, port, user, password, None)
        creator = Creator(temp_conn)
        creator.database_creator(db_name)
        temp_conn.close()

        conn = Connection.connect(host, port, user, password, db_name)
        checker = CheckerAndReceiver(conn)

        if checker.table_exist(table_name):
            print(f"⚠ Table '{table_name}' already exists in MariaDB. Skipping insert.")
        else:
            saver = Saver(conn)
            saver.sql_saver(df, table_name)
            print(f"✅ Migrated {len(df)} rows from SQL Server → MariaDB table '{table_name}'")

        conn.close()

    def migrate_all(self):
        for table in self.get_tables():
            print(f"➡ Migrating table: {table}")
            self.migrate_one(table)




# ========= SQL Server → Mongo =========
class SQLServerToMongo(BaseSQLServer):
    def __init__(self, mssql_uri, mongo_uri):
        super().__init__(mssql_uri)
        self.mongo_uri = mongo_uri

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if df.empty:
            return
        db_name = self.mongo_uri.split("/")[-1]
        client = MongoClient(self.mongo_uri)
        db = client[db_name]
        if table_name in db.list_collection_names():
            print(f"⚠ Collection '{table_name}' already exists. Skipping.")
            return
        db[table_name].insert_many(df.to_dict("records"))
        print(f"✅ Migrated {len(df)} rows from SQL Server to MongoDB collection '{table_name}'")

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)