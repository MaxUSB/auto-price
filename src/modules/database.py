import pandas as pd
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, text, exc


class DataBase:
    def __init__(self, connect_data):
        self.engine = create_engine(URL(**connect_data))

    def select_query(self, sql, params=None):
        try:
            data = pd.read_sql_query(text(sql), self.engine, params=params)
            return True, data, None
        except exc.SQLAlchemyError as error:
            return False, None, error
