


def build_connection(db_type: str, data: dict) -> str:
    db_type = db_type.lower()

    if db_type in ["postgresql", "mysql", "mariadb", "mssql", "clickhouse"]:
        return f"{db_type}://{data.get('username')}:{data.get('password')}@{data.get('host')}:{data.get('port')}/{data.get('db_name')}"

    elif db_type == "mongodb":
        if data.get("username") and data.get("password"):
            return f"mongodb://{data['username']}:{data['password']}@{data['host']}:{data['port']}/{data['db_name']}"
        return f"mongodb://{data['host']}:{data['port']}/{data['db_name']}"

    elif db_type == "redis":
        if data.get("password"):
            return f"redis://:{data['password']}@{data['host']}:{data['port']}/{data.get('db_name','0')}"
        return f"redis://{data['host']}:{data['port']}/{data.get('db_name','0')}"

    elif db_type == "oracle":
        return f"oracle://{data['username']}:{data['password']}@{data['host']}:{data['port']}/{data['service_name']}"

    elif db_type == "sqlite":
        return f"sqlite:///{data['file_path']}"

    elif db_type == "dynamodb":
        return (
            f"dynamodb://{data['aws_access_key']}:{data['aws_secret_key']}"
            f"@{data['host']}:{data['port']}/{data.get('db_name','')}"
            f"?region={data['region']}"
        )

    elif db_type == "elasticsearch":
        return f"elasticsearch://{data['username']}:{data['password']}@{data['host']}:{data['port']}"

    else:
        raise ValueError(f"Unsupported DB type: {db_type}")
