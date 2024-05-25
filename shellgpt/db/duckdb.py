import duckdb

class DuckDB:
    def __init__(self, db_file=None):
        if db_file is None:
            self.conn = duckdb.connect(":memory:")
        else:
            self.conn = duckdb.connect(db_file)


    def exec(self, query):
        return self.conn.execute(query)

    def show(self, query):
        print(self.sql(query).fetchdf())
