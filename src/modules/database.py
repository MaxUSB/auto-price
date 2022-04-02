import psycopg2
import pandas as pd


class DataBase:
    def __init__(self, connect_data):
        self.connection = psycopg2.connect(**connect_data)

    def select_query(self, sql):
        return pd.read_sql_query(sql, self.connection)

    def __del__(self):
        self.connection.close()
