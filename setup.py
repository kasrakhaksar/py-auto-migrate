from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='py_auto_migrate',
    version='0.2.3',
    author='Kasra Khaksar',
    author_email='kasrakhaksar17@gmail.com',
    description='A Tool For Transferring Data, Tables, And Datasets Between Different Databases.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(include=["py_auto_migrate", "py_auto_migrate.*"]),
    python_requires='>=3.11',
    install_requires=[
        'pandas',
        'mysqlSaver',
        'pymongo',
        'click',
        'pyodbc',
        'psycopg2',
        'oracledb',
        'redis',
        'boto3'
    ],
    entry_points={
        'console_scripts': [
            'py-auto-migrate=py_auto_migrate.cli:main',
        ],
    },
)