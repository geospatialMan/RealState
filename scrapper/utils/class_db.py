import psycopg2


class DbMethods:

    def __init__(self):
        self.conn = None
        self.cur = None

    def create_cursor(self, db_name, user, password, port):
        self.conn = psycopg2.connect(
            dbname=db_name, user=user, password=password, port=port
        )
        self.cur = self.conn.cursor()

    def query_data(self, query):
        self.cur.execute(query)
        rows = self.cur.fetchall()
        return rows

    def execute_query(self, sql, params, commit):
        try:
            self.cur.execute(sql, params)
            if commit:
                self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            raise e

    def close(self):
        self.cur.close()
        self.conn.close()
