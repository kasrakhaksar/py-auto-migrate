<h1 align="center">
  <strong>𝐏𝐲-𝐀𝐮𝐭𝐨-𝐌𝐢𝐠𝐫𝐚𝐭𝐞</strong>
</h1>

<p align="center">
  A powerful database migration tool to transfer data (e.g., between MongoDB and MySQL or PostgreSQL and MySQL), with automatic table/database creation, existence checks, and support for full database migrations.
</p>



<table align="center">
  <tr>
    <td>
      <a href="https://pypi.org/project/py-auto-migrate/">
        <img src="https://img.shields.io/badge/PyPI-Package-blue?logo=pypi" alt="PyPI">
      </a>
    </td>
    <td>
      <a href="https://github.com/kasrakhaksar/py-auto-migrate">
        <img src="https://img.shields.io/badge/GitHub-Repo-blue?logo=github" alt="GitHub">
      </a>
    </td>
    <td>
      <a href="https://github.com/kasrakhaksar/py-auto-migrate/stargazers">
        <img src="https://img.shields.io/github/stars/kasrakhaksar/py-auto-migrate?style=flat-square" alt="Stars">
      </a>
    </td>
    <td>
      <a href="https://github.com/kasrakhaksar/py-auto-migrate/network/members">
        <img src="https://img.shields.io/github/forks/kasrakhaksar/py-auto-migrate?style=flat-square" alt="Forks">
      </a>
    </td>
    <td>
      <a href="https://github.com/kasrakhaksar/py-auto-migrate/issues">
        <img src="https://img.shields.io/github/issues/kasrakhaksar/py-auto-migrate?style=flat-square" alt="Issues">
      </a>
    </td>
    <td>
      <a href="https://github.com/kasrakhaksar/py-auto-migrate/pulls">
        <img src="https://img.shields.io/github/issues-pr/kasrakhaksar/py-auto-migrate?style=flat-square" alt="Pull Requests">
      </a>
    </td>
    <td>
      <a href="https://github.com/kasrakhaksar/py-auto-migrate/releases">
        <img src="https://img.shields.io/github/v/release/kasrakhaksar/py-auto-migrate?style=flat-square" alt="Releases">
      </a>
    </td>
  </tr>
</table>






---

## Installation

```bash
pip install py-auto-migrate
```


## Download CLI 

If you don’t have Python, or you want to use it with the CLI (Shell), you can download the dedicated <b>PAM-CLI</b> from the <b>Releases</b> on GitHub epository.

<a href="https://github.com/kasrakhaksar/py-auto-migrate/releases" target="_blank">
  <img src="https://img.shields.io/badge/-Release-blue?logo=github" />
</a>

---


## Help

```bash
py-auto-migrate --help
```

<p>This command displays a detailed guide on how to use the package, including available commands, arguments, and examples. It’s the best place to start if you want to quickly understand how to work with py-auto-migrate.</p>



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
```
```bash
py-auto-migrate migrate --source "mongodb://localhost:27017/mydb" --target "mysql://root:1234@localhost:3306/mydb" --table users
```

<p>You can also use MongoDB → MongoDB or PostgreSQL → PostgreSQL</p>

---


## Database Support
<ul>
  <li>MySQL</li>
  <li>MongoDB</li>
  <li>PostgreSQL</li>
  <li>MariaDB</li>
  <li>SQLite</li>
</ul>


---


## Future Plans
<ul>
  <li>Add support for creating indexes on tables/collections to improve query performance.</li>
  <li>Support for more databases: Add migrations for Oracle.</li>
</ul>
