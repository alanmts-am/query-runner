from model.database import Database
from model.result import Result

import psycopg2


class Postgres(Database):
    def __init__(self, host, port, database, username, pwd):
        super().__init__(host, port, database, username, pwd)

    def connect(self):
        return psycopg2.connect(**{
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.username,
            "password": self.pwd
        })

    def run(self, query: str) -> Result:
        try:
            conn = self.connect()
        except Exception as ex:
            return Result(data=[], columns=[], collected=False, error=str(ex))

        cur = conn.cursor()

        try:
            cur.execute(query)
            if cur.description is not None:
                records = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
            else:
                records, columns = [], []
            result = Result(data=records, columns=columns, collected=True)
        except Exception as ex:
            result = Result(data=[], columns=[], collected=False, error=str(ex))

        conn.commit()
        cur.close()
        conn.close()

        return result
