<h1 align="center">
  <strong>Py-Auto-Migrate</strong>
</h1>
<p align="center">
  A powerful database migration tool to transfer data (e.g., between MongoDB and MySQL or MongoDB and MongoDB), with automatic table/database creation, existence checks, and support for full database migrations.
  <br><br>
  <a href="https://github.com/kasrakhaksar/py-auto-migrate" target="_blank">
    <img src="https://img.shields.io/badge/GitHub-Repo-blue?logo=github" alt="GitHub" />
  </a>
</p>



---

## Installation

```bash
pip install py-auto-migrate
```

---


## Usage
<b>Command Line Interface (CLI)</b>
```bash
py-auto-migrate migrate --source <source_uri> --target <target_uri> --table <table_name>
```

<p>

  <b>--source :</b>Source database URI (e.g., mysql://user:pass@host:3306/dbname)

  <b>--target :</b>Target database URI (e.g., mongodb://localhost:27017/mydb)

  <b>--table (optional):</b>Specific table/collection to migrate. If omitted, all tables/collections will be

</p>


---


## Example
```bash
py-auto-migrate migrate --source "mongodb://localhost:27017/mydb" --target "mongodb://localhost:27017/mydb2"
py-auto-migrate migrate --source "mongodb://localhost:27017/mydb" --target "mysql://root:1234@localhost:3306/mydb" --table users
```

<p>You can also use MongoDB → MongoDB or MySQL → MySQL</p>

---



## Future Plans
<ul>

  <li>Add support for creating indexes on tables/collections to improve query performance.</li>
  <li>Support for more databases: Add migrations for PostgreSQL, SQLite.</li>
</ul>