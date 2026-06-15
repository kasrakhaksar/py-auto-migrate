from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='py_auto_migrate',
    version='0.5.8',
    author='Kasra Khaksar',
    author_email='kasrakhaksar17@gmail.com',
    description='A Powerful Database Migration Tool To Transfer Data.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(include=["py_auto_migrate", "py_auto_migrate.*"]),
    python_requires='>=3.11',
    install_requires=[
        'openai',
        'requests',
        'pymysql',
        'pymongo',
        'click',
        'pyodbc',
        'psycopg2',
        'oracledb',
        'redis',
        'boto3',
        'elasticsearch',
        'clickhouse_driver',
        'uvicorn',
        'fastapi',
        'python-multipart',
        'jinja2'
    ],
    package_data={
        'py_auto_migrate': [
            'dashboard/templates/*.html',
            'dashboard/static/css/*.css',
            'dashboard/static/js/*.js',
        ],
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'py-auto-migrate=py_auto_migrate.cli:main',
        ],
    },
)