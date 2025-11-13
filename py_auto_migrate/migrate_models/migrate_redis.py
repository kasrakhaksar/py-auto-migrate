from py_auto_migrate.base_models.base_redis import BaseRedis
from py_auto_migrate.insert_models.insert_redis import InsertRedis


from py_auto_migrate.insert_models.insert_mssql import InsertMSSQL
from py_auto_migrate.insert_models.insert_mongodb import InsertMongoDB
from py_auto_migrate.insert_models.insert_sqlite import InsertSQLite
from py_auto_migrate.insert_models.insert_mysql import InsertMySQL
from py_auto_migrate.insert_models.insert_mariadb import InsertMariaDB
from py_auto_migrate.insert_models.insert_oracle import InsertOracle
from py_auto_migrate.insert_models.insert_postgressql import InsertPostgresSQL
from py_auto_migrate.insert_models.insert_dynamodb import InsertDynamoDB


# ========= Redis → PostgreSQL =========
class RedisToPostgres(BaseRedis):
    def __init__(self, redis_uri, pg_uri):
        super().__init__(redis_uri)
        self.inserter = InsertPostgresSQL(pg_uri)

    def migrate_one(self, key):
        df = self.read_key(key)
        if not df.empty:
            self.inserter.insert(df, key)

    def migrate_all(self, pattern='*'):
        for key in self.get_keys(pattern):
            print(
                f"➡ Migrating table: {key.decode() if isinstance(key, bytes) else key}")
            self.migrate_one(key.decode() if isinstance(key, bytes) else key)


# ========= Redis → Redis =========
class RedisToRedis(BaseRedis):
    def __init__(self, source_uri, target_uri):
        super().__init__(source_uri)
        self.inserter = InsertRedis(target_uri)

    def migrate_one(self, key):
        df = self.read_key(key)
        if not df.empty:
            self.inserter.insert(df, key)

    def migrate_all(self, pattern='*'):
        for key in self.get_keys(pattern):
            print(
                f"➡ Migrating table: {key.decode() if isinstance(key, bytes) else key}")
            self.migrate_one(key.decode() if isinstance(key, bytes) else key)


# ========= Redis → MySQL =========
class RedisToMySQL(BaseRedis):
    def __init__(self, redis_uri, mysql_uri):
        super().__init__(redis_uri)
        self.inserter = InsertMySQL(mysql_uri)

    def migrate_one(self, key):
        df = self.read_key(key)
        if not df.empty:
            self.inserter.insert(df, key)

    def migrate_all(self, pattern='*'):
        for key in self.get_keys(pattern):
            print(
                f"➡ Migrating table: {key.decode() if isinstance(key, bytes) else key}")
            self.migrate_one(key.decode() if isinstance(key, bytes) else key)


# ========= Redis → MariaDB =========
class RedisToMaria(BaseRedis):
    def __init__(self, redis_uri, maria_uri):
        super().__init__(redis_uri)
        self.inserter = InsertMariaDB(maria_uri)

    def migrate_one(self, key):
        df = self.read_key(key)
        if not df.empty:
            self.inserter.insert(df, key)

    def migrate_all(self, pattern='*'):
        for key in self.get_keys(pattern):
            print(
                f"➡ Migrating table: {key.decode() if isinstance(key, bytes) else key}")
            self.migrate_one(key.decode() if isinstance(key, bytes) else key)


# ========= Redis → SQLite =========
class RedisToSQLite(BaseRedis):
    def __init__(self, redis_uri, sqlite_file):
        super().__init__(redis_uri)
        self.inserter = InsertSQLite(sqlite_file)

    def migrate_one(self, key):
        df = self.read_key(key)
        if not df.empty:
            self.inserter.insert(df, key)

    def migrate_all(self, pattern='*'):
        for key in self.get_keys(pattern):
            print(
                f"➡ Migrating table: {key.decode() if isinstance(key, bytes) else key}")
            self.migrate_one(key.decode() if isinstance(key, bytes) else key)


# ========= Redis → MongoDB =========
class RedisToMongo(BaseRedis):
    def __init__(self, redis_uri, mongo_uri):
        super().__init__(redis_uri)
        self.inserter = InsertMongoDB(mongo_uri)

    def migrate_one(self, key):
        df = self.read_key(key)
        if not df.empty:
            self.inserter.insert(df, key)

    def migrate_all(self, pattern='*'):
        for key in self.get_keys(pattern):
            print(
                f"➡ Migrating table: {key.decode() if isinstance(key, bytes) else key}")
            self.migrate_one(key.decode() if isinstance(key, bytes) else key)


# ========= Redis → MSSQL =========
class RedisToMSSQL(BaseRedis):
    def __init__(self, redis_uri, mssql_uri):
        super().__init__(redis_uri)
        self.inserter = InsertMSSQL(mssql_uri)

    def migrate_one(self, key):
        df = self.read_key(key)
        if not df.empty:
            self.inserter.insert(df, key)

    def migrate_all(self, pattern='*'):
        for key in self.get_keys(pattern):
            print(
                f"➡ Migrating table: {key.decode() if isinstance(key, bytes) else key}")
            self.migrate_one(key.decode() if isinstance(key, bytes) else key)


# ========= Redis → Oracle =========
class RedisToOracle(BaseRedis):
    def __init__(self, redis_uri, oracle_uri):
        super().__init__(redis_uri)
        self.inserter = InsertOracle(oracle_uri)

    def migrate_one(self, key):
        df = self.read_key(key)
        if not df.empty:
            self.inserter.insert(df, key)

    def migrate_all(self, pattern='*'):
        for key in self.get_keys(pattern):
            print(
                f"➡ Migrating table: {key.decode() if isinstance(key, bytes) else key}")
            self.migrate_one(key.decode() if isinstance(key, bytes) else key)



# ========= Redis → Dynamo =========
class RedisToDynamoDB(BaseRedis):
    def __init__(self, redis_uri, dynamo_uri):
        super().__init__(redis_uri)
        self.inserter = InsertDynamoDB(dynamo_uri)

    def migrate_one(self, key):
        df = self.read_key(key)
        if not df.empty:
            self.inserter.insert(df, key)

    def migrate_all(self, pattern='*'):
        for key in self.get_keys(pattern):
            print(
                f"➡ Migrating table: {key.decode() if isinstance(key, bytes) else key}")
            self.migrate_one(key.decode() if isinstance(key, bytes) else key)
