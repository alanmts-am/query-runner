from model.database import Database
from model.result import Result

import psycopg2


class Postgres(Database):
    def __init__(self, host, port, database, username, pwd):
        super().__init__(host, port, database, username, pwd)
    pass

    def connect(self):
        return psycopg2.connect(**{
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.username,
            "password": self.pwd
        })

    def run(self, query: str):
        result: Result

        conn = self.connect()
        cur = conn.cursor()

        cur.execute(query)

        try:
            records = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

            result = Result(data=records, columns=columns, collected=True)
        except Exception as ex:
            result = Result(data=[], columns=[], collected=False)
        conn.commit()

        cur.close()
        conn.close()

        return result
