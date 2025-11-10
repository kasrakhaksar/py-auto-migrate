from ..base_models.base_oracle import BaseOracle
from ..insert_models.insert_oracle import InsertOracle


from ..insert_models.insert_mysql import InsertMySQL
from ..insert_models.insert_mariadb import InsertMariaDB
from ..insert_models.insert_postgressql import InsertPostgresSQL
from ..insert_models.insert_sqlite import InsertSQLite
from ..insert_models.insert_mssql import InsertMSSQL
from ..insert_models.insert_mongodb import InsertMongoDB


class OracleToMySQL(BaseOracle):
    def __init__(self, oracle_uri, mysql_uri):
        super().__init__(oracle_uri)
        self.inserter = InsertMySQL(mysql_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


class OracleToMaria(BaseOracle):
    def __init__(self, oracle_uri, maria_uri):
        super().__init__(oracle_uri)
        self.inserter = InsertMariaDB(maria_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


class OracleToPostgres(BaseOracle):
    def __init__(self, oracle_uri, pg_uri):
        super().__init__(oracle_uri)
        self.inserter = InsertPostgresSQL(pg_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


class OracleToSQLite(BaseOracle):
    def __init__(self, oracle_uri, sqlite_uri):
        super().__init__(oracle_uri)
        self.inserter = InsertSQLite(sqlite_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


class OracleToMSSQL(BaseOracle):
    def __init__(self, oracle_uri, mssql_uri):
        super().__init__(oracle_uri)
        self.inserter = InsertMSSQL(mssql_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


class OracleToMongo(BaseOracle):
    def __init__(self, oracle_uri, mongo_uri):
        super().__init__(oracle_uri)
        self.inserter = InsertMongoDB(mongo_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)


class OracleToOracle(BaseOracle):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri)
        self.inserter = InsertOracle(target_uri)

    def migrate_one(self, table_name):
        df = self.read_table(table_name)
        if not df.empty:
            self.inserter.insert(df, table_name)

    def migrate_all(self):
        for t in self.get_tables():
            print(f"➡ Migrating table: {t}")
            self.migrate_one(t)
