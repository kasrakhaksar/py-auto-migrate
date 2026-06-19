import pandas as pd


def sql_type_mapper(dtype, engine):

    if pd.api.types.is_bool_dtype(dtype):

        return {
            "postgresql": "BOOLEAN",
            "mysql": "BOOLEAN",
            "mariadb": "BOOLEAN",
            "sqlite": "INTEGER",
            "mssql": "BIT",
            "oracle": "NUMBER(1)",
            "clickhouse": "UInt8",
        }.get(engine, "BOOLEAN")


    if pd.api.types.is_integer_dtype(dtype):

        return {
            "postgresql": "BIGINT",
            "mysql": "BIGINT",
            "mariadb": "BIGINT",
            "sqlite": "INTEGER",
            "mssql": "BIGINT",
            "oracle": "NUMBER",
            "clickhouse": "Int64",
        }.get(engine, "BIGINT")


    if pd.api.types.is_float_dtype(dtype):

        return {
            "postgresql": "DOUBLE PRECISION",
            "mysql": "DOUBLE",
            "mariadb": "DOUBLE",
            "sqlite": "REAL",
            "mssql": "FLOAT",
            "oracle": "FLOAT",
            "clickhouse": "Float64",
        }.get(engine, "FLOAT")


    if pd.api.types.is_datetime64_any_dtype(dtype):

        return {
            "postgresql": "TIMESTAMP",
            "mysql": "DATETIME",
            "mariadb": "DATETIME",
            "sqlite": "TEXT",
            "mssql": "DATETIME",
            "oracle": "TIMESTAMP",
            "clickhouse": "DateTime",
        }.get(engine, "TIMESTAMP")


    return {
        "postgresql": "TEXT",
        "mysql": "TEXT",
        "mariadb": "TEXT",
        "sqlite": "TEXT",
        "mssql": "NVARCHAR(MAX)",
        "oracle": "NVARCHAR2(4000)",
        "clickhouse": "String",
    }.get(engine, "TEXT")