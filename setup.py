from setuptools import setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


packages = \
['py-auto-migrate']

package_data = \
{'': ['*']}


setup_kwargs = {
    'name' :'py-auto-migrate',
    'version':'0.0.1',
    'author':'Kasra Khaksar',
    'author_email':'kasrakhaksar17@gmail.com',
    'description':'A Tool For Transferring Data, Tables, And Datasets Between Different Databases.',
    "long_description" : long_description,
    "long_description_content_type" :'text/markdown',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.11',
    'install_requires': [
    'pandas',
    'tqdm',
    'pymysql',
    'pymongo',
    'mysqlSaver'
    ],
}


setup(**setup_kwargs)