<h1 align="center">
  <strong>🚀 Py-Auto-Migrate</strong>
</h1>

<p align="center">
  <em>The Universal Database Migration Tool</em> <br>
  <strong>Seamlessly transfer data between any database.
</p>

<p align="center">
  <a href="https://pypi.org/project/py-auto-migrate/">
    <img src="https://img.shields.io/pypi/v/py-auto-migrate?style=for-the-badge&logo=pypi&logoColor=white&label=PyPI&color=blue" alt="PyPI - Version">
  </a>
  <a href="https://github.com/kasrakhaksar/py-auto-migrate">
    <img src="https://img.shields.io/badge/GitHub-Repo-181717?style=for-the-badge&logo=github" alt="GitHub Repo">
  </a>
  <a href="https://github.com/kasrakhaksar/py-auto-migrate/stargazers">
    <img src="https://img.shields.io/github/stars/kasrakhaksar/py-auto-migrate?style=for-the-badge&logo=apachespark&color=yellow" alt="Stars">
  </a>
    <a href="https://github.com/kasrakhaksar/py-auto-migrate/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/kasrakhaksar/py-auto-migrate?style=for-the-badge&color=brightgreen" alt="License">
  </a>
  <a href="https://github.com/kasrakhaksar/py-auto-migrate/releases">
    <img src="https://img.shields.io/github/v/release/kasrakhaksar/py-auto-migrate?style=for-the-badge&logo=github&label= Releases" alt="Releases">
  </a>
</p>


---

## ⚡ Why Py-Auto-Migrate?

Migrating data between different database systems is often a tedious and error-prone task. **Py-Auto-Migrate** is here to change that. It's a powerful, flexible, and easy-to-use Python tool that automates the entire process.

-   **🔌 Universal Connector**: Supports a vast range of databases, from SQL to NoSQL.
-   **🤖 Zero Configuration**: Point to your source and target, and let the tool handle schema detection, data type mapping, and destination creation.
-   **⚡ Blazing Fast**: Optimized for performance, even with large datasets.
-   **🛡️ Safe & Reliable**: Built-in checks ensure data integrity throughout the migration.


---

## 📦 Installation

Get started in seconds with `pip`.

```bash
pip install py-auto-migrate
```

### 🐚 Prefer a Standalone Shell?

Don't have Python? No problem! Download the dedicated **PAM-Shell** for your OS from the [Releases page](https://github.com/kasrakhaksar/py-auto-migrate/releases). It's a ready-to-run executable with the same powerful features.

---

## 🏁 Quick Start

Using Py-Auto-Migrate is as simple as running one command.

### Basic Command Structure

```bash
py-auto-migrate migrate --source <SOURCE_URI> --target <TARGET_URI> [--table <TABLE_NAME>]
```

| Argument       | Description                                                                                  |
| -------------- | -------------------------------------------------------------------------------------------- |
| `--source`     | **Required.** Connection URI for the source database.                                        |
| `--target`     | **Required.** Connection URI for the target database.                                        |
| `--table`      | **Optional.** Migrate a specific table/collection. If omitted, **all** data is migrated.    |

### Real-World Examples

**1. Migrate an entire database from MongoDB to MySQL:**

```bash
py-auto-migrate migrate \
  --source "mongodb://user:pass@localhost:27017/source_db" \
  --target "mysql://user:pass@localhost:3306/target_db"
```

**2. Migrate a single PostgreSQL table to a new MongoDB collection:**

```bash
py-auto-migrate migrate \
  --source "postgresql://user:pass@localhost:5432/mydb" \
  --target "mongodb://user:pass@localhost:27017/mydb" \ --table users
```

> **✨ The Magic:** If the target database or table doesn't exist, **Py-Auto-Migrate automatically creates it for you!** It intelligently maps source data types to the appropriate target schema.

---

## 🗄️ Supported Databases

We support a wide and growing range of databases.

| Category       | Databases                                                                                                                                                                                                                                                                                                                                                                                          |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Relational** | [![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)](https://www.mysql.com/) [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/) [![Oracle](https://img.shields.io/badge/Oracle-F80000?style=flat-square&logo=oracle&logoColor=white)](https://www.oracle.com/database/) [![SQL Server](https://img.shields.io/badge/SQL%20Server-CC2927?style=flat-square&logo=microsoftsqlserver&logoColor=white)](https://www.microsoft.com/en-us/sql-server) [![MariaDB](https://img.shields.io/badge/MariaDB-003545?style=flat-square&logo=mariadb&logoColor=white)](https://mariadb.org/) [![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/) |
| **NoSQL**      | [![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://www.mongodb.com/) [![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io/) [![DynamoDB](https://img.shields.io/badge/DynamoDB-4053D6?style=flat-square&logo=amazondynamodb&logoColor=white)](https://aws.amazon.com/dynamodb/) [![Elasticsearch](https://img.shields.io/badge/Elasticsearch-005571?style=flat-square&logo=elasticsearch&logoColor=white)](https://www.elastic.co/elasticsearch/) |
| **Other**      | [![ClickHouse](https://img.shields.io/badge/ClickHouse-FFCC00?style=flat-square&logo=clickhouse&logoColor=black)](https://clickhouse.com/)                                                                                     |

---

## 🧭 Future Roadmap

We're constantly working to make Py-Auto-Migrate even better. Here’s what’s on the horizon:

| Feature                                                       | Status      |
| ------------------------------------------------------------- | ----------- |
| ✅ **Click House Support**                                     | Completed   |
| ⏳ **Automatic Index Creation** on target tables/collections   | In Progress |
| ⏳ **Performance Optimizations** for terabyte-scale datasets   | In Progress |
| ⏳ **Incremental Migrations** (sync only changes)              | Planned     |
| ⏳ **Graphical User Interface (GUI)**                          | Planned     |

Have a feature request? [Open an issue](https://github.com/kasrakhaksar/py-auto-migrate/issues) and let us know!