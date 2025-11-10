from ..base_models.base_mssql import BaseMSSQL
from ..insert_models.insert_mssql import InsertMSSQL


from ..insert_models.insert_mysql import InsertMySQL
from ..insert_models.insert_mongodb import InsertMongoDB
from ..insert_models.insert_sqlite import InsertSQLite
from ..insert_models.insert_postgressql import InsertPostgresSQL
from ..insert_models.insert_mariadb import InsertMariaDB
from ..insert_models.insert_oracle import InsertOracle



# ========= SQL Server → MySQL =========
class MSSQLToMySQL(BaseMSSQL):
    def __init__(self, mssql_uri, mysql_uri):
        super().__init__(mssql_uri)
        self.inserter = InsertMySQL(mysql_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= SQL Server → PostgreSQL =========
class MSSQLToPostgres(BaseMSSQL):
    def __init__(self, mssql_uri, pg_uri):
        super().__init__(mssql_uri)
        self.inserter = InsertPostgresSQL(pg_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= SQL Server → SQLite =========
class MSSQLToSQLite(BaseMSSQL):
    def __init__(self, mssql_uri, sqlite_uri):
        super().__init__(mssql_uri)
        self.inserter = InsertSQLite(sqlite_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= SQL Server → MariaDB =========
class MSSQLToMaria(BaseMSSQL):
    def __init__(self, mssql_uri, maria_uri):
        super().__init__(mssql_uri)
        self.inserter = InsertMariaDB(maria_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= SQL Server → SQL Server =========
class MSSQLToMSSQL(BaseMSSQL):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri)
        self.inserter = InsertMSSQL(target_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


# ========= SQL Server → Mongo =========
class MSSQLToMongo(BaseMSSQL):
    def __init__(self, mssql_uri, mongo_uri):
        super().__init__(mssql_uri)
        self.inserter = InsertMongoDB(mongo_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)



# ========= SQL Server → Oracle =========
class MSSQLToOracle(BaseMSSQL):
    def __init__(self, mssql_uri, oracle_uri):
        super().__init__(mssql_uri)
        self.inserter = InsertOracle(oracle_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)