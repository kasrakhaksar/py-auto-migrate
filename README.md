<h1 align="center">
  <strong>𝐏𝐲-𝐀𝐮𝐭𝐨-𝐌𝐢𝐠𝐫𝐚𝐭𝐞</strong>
</h1>

<p align="center">
  A powerful database migration tool to transfer data (e.g., between MongoDB → MySQL or PostgreSQL and Oracle), with automatic table/database creation, existence checks, and support for full database migrations.
</p>

[![PyPI](https://img.shields.io/badge/PyPI-Package-blue?logo=pypi)](https://pypi.org/project/py-auto-migrate/) 
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repo-blue?logo=github)](https://github.com/kasrakhaksar/py-auto-migrate) 
[![Stars](https://img.shields.io/github/stars/kasrakhaksar/py-auto-migrate?style=flat-square)](https://github.com/kasrakhaksar/py-auto-migrate/stargazers) 
[![Forks](https://img.shields.io/github/forks/kasrakhaksar/py-auto-migrate?style=flat-square)](https://github.com/kasrakhaksar/py-auto-migrate/network/members) 
[![Issues](https://img.shields.io/github/issues/kasrakhaksar/py-auto-migrate?style=flat-square)](https://github.com/kasrakhaksar/py-auto-migrate/issues) 
[![Pull Requests](https://img.shields.io/github/issues-pr/kasrakhaksar/py-auto-migrate?style=flat-square)](https://github.com/kasrakhaksar/py-auto-migrate/pulls) 
[![Releases](https://img.shields.io/github/v/release/kasrakhaksar/py-auto-migrate?style=flat-square)](https://github.com/kasrakhaksar/py-auto-migrate/releases)






---

## Installation

```bash
pip install py-auto-migrate
```


## Download Shell 

If you don’t have Python, or you want to use it with the Shell, you can download the dedicated <b>PAM-Shell</b> from the <b>Releases</b> on GitHub epository.

<a href="https://github.com/kasrakhaksar/py-auto-migrate/releases" target="_blank">
  <img src="https://img.shields.io/badge/-Release-blue?logo=github" />
</a>

---


## Help
```bash
py-auto-migrate --help
```

<p>After installation using pip, open your terminal (command line). This command displays a detailed guide on how to use the package, including available commands, arguments, and examples. It’s the best place to start if you want to quickly understand how to work with py-auto-migrate.</p>


<p>‌But in <b>PAM-Shell</b> , you just need to type `help`</p>



```bash
py-auto-migrate> help
```

---


## Usage

```bash
py-auto-migrate migrate --source <source_uri> --target <target_uri> --table <table_name>
```
| Argument   | Description                                                                                          |
| ---------- | ---------------------------------------------------------------------------------------------------- |
| --source | Source database URI (e.g., mysql://user:pass@host:3306/dbname)                                         |
| --target | Target database URI (e.g., oracle://<user>:<password>@<host>:<port>/<service_name>)                    |
| --table  | Optional. Specific table/collection to migrate. If omitted, all tables/collections will be migrated.   |


## Example

Example 1:

```bash
py-auto-migrate migrate --source "mongodb://username:password@<host>:<port>/mydb" --target "mongodb://username:password@<host>:<port>/mydb2"
```

Example 2:

```bash
py-auto-migrate migrate --source "postgresql://<user>:<password>@<host>:<port>/mydb" --target "mysql://<user>:<password>@<host>:<port>/mydb" --table users
```


<b>If the database or table does not exist, it will create them for you based on the column types of the DataFrame.</b>

<p>You can also use MongoDB → MongoDB or PostgreSQL → PostgreSQL</p>




---

## Supported Databases

| Database   |
| ---------- |
| MySQL      |
| PostgreSQL |
| MongoDB    |
| MariaDB    |
| Oracle     |
| Redis      |
| DynamoDB   |
| SQL Server |
| SQLite     |

---

## Future Plans

| Feature                                      | Status  |
| -------------------------------------------- | ------- |
| Support for Redis migrations                 |    ✔️   |
| Support for DynamoDB migrations              |    ✔️   |
| Index creation on tables/collections         | Planned |
| Performance optimizations for large datasets | Planned |

