from typing import List
import yaml
import pandas as pd

from model.database import Database
from model.postgres import Postgres
from model.result import Result


def generate_xlsx(databases_result: List[Result]) -> None:
    if (databases_result[0].collected):
        result_list: List[pd.DataFrame] = []

        for result in databases_result:
            df = pd.DataFrame(data=result.data, columns=result.columns)
            result_list.append(df)

        result_df: pd.DataFrame = pd.concat(result_list, ignore_index=True)
        result_df.to_excel("data" + '.xlsx', index=False)


CONFIG_PATH = "config.yml"
QUERY_PATH = "query.sql"

with open(CONFIG_PATH, "r", encoding='utf8') as file:
    config = yaml.full_load(file)

with open(QUERY_PATH, "r", encoding='utf8') as file:
    query = file.read()

HOST = config["connection"]["host"]
PORT = config["connection"]["port"]
DATABASE = config["connection"]["database"]
USER = config["connection"]["username"]
PASSWORD = config["connection"]["password"]

SOURCE_DATABASE = config["sql"]["database"]

IS_SELECT = config["options"]["select"]

database_main: Database = Postgres(
    host=HOST, port=PORT, database=DATABASE, username=USER, pwd=PASSWORD)

targets_result: Result = database_main.run(
    query=SOURCE_DATABASE)

databases: List[Database] = []
databases_result: List[Result] = []


for database in targets_result.data:
    databases.append(
        Postgres(host=database[0], port=database[1], database=database[2], username=database[3], pwd=database[4]))

for database in databases:
    database_result = database.run(query=query)
    databases_result.append(database_result)

generate_xlsx(databases_result=databases_result)
