from abc import ABC, abstractclassmethod


class Database(ABC):
    def __init__(self, host: str, port: int, database: str, username: str, pwd: str):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.pwd = pwd
        pass

    @classmethod
    @abstractclassmethod
    def connect(query: str):
        pass

    @classmethod
    @abstractclassmethod
    def run(query: str, ):
        pass
