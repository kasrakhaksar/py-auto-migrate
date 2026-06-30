import pandas as pd
import numpy as np
import datetime
from decimal import Decimal
from uuid import UUID

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
            "mssql": "DATETIME2",
            "oracle": "TIMESTAMP",
            "clickhouse": "DateTime",
        }.get(engine, "TIMESTAMP")


    return {
        "postgresql": "TEXT",
        "mysql": "TEXT",
        "mariadb": "TEXT",
        "sqlite": "TEXT",
        "mssql": "NVARCHAR(MAX)",
        "oracle": "NVARCHAR2(2000)",
        "clickhouse": "String",
    }.get(engine, "TEXT")





def sqlite_value_mapper(value):

    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.isoformat(" ")
    
    if isinstance(value, datetime.datetime):
        return value.isoformat(" ")

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        return float(value)

    if isinstance(value, np.bool_):
        return bool(value)

    if isinstance(value, np.ndarray):
        return value.tolist()

    return value



def dynamodb_value_mapper(value):

    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if isinstance(value, datetime.datetime):
        return value.isoformat()

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        return Decimal(str(value))

    if isinstance(value, float):
        return Decimal(str(value))

    if isinstance(value, np.bool_):
        return bool(value)

    if isinstance(value, UUID):
        return str(value)

    if isinstance(value, Decimal):
        return value

    return value



def infer_data_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in df.columns:
        if df[col].dtype != "object":
            continue

        df[col] = df[col].astype(str).str.strip()

        lower = df[col].str.lower()
        if lower.isin(["true", "false", "1", "0"]).all():
            df[col] = lower.map({
                "true": True,
                "false": False,
                "1": True,
                "0": False
            })
            continue

        numeric = pd.to_numeric(df[col], errors="coerce")

        if numeric.notna().all():
            if (numeric % 1 == 0).all():
                df[col] = numeric.astype(int)
            else:
                df[col] = numeric.astype(float)
            continue

        dt = pd.to_datetime(df[col], errors="coerce")

        if dt.notna().all():
            df[col] = dt
            continue

    return df





def normalize_datetime(df):
    df = df.copy()

    df = df.fillna(0)
    
    for col in df.columns:
        s = df[col]

        if pd.api.types.is_datetime64tz_dtype(s):
            df[col] = s.dt.tz_localize(None)
            continue

        if pd.api.types.is_datetime64_any_dtype(s):
            continue

        if pd.api.types.is_object_dtype(s) or pd.api.types.is_string_dtype(s):
            try:
                converted = pd.to_datetime(s, errors="raise")

                if pd.api.types.is_datetime64_any_dtype(converted):
                    df[col] = converted

            except Exception:
                pass

    return df