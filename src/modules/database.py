import pandas as pd
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, text, exc


class DataBase:
    def __init__(self, connect_data):
        self.engine = create_engine(URL(**connect_data))

    def create_tables(self, tables):
        for table in tables:
            cols = ','.join(map(lambda col: f'{col[0]} {col[1]}', table['cols'].items()))
            constraint = f',CONSTRAINT {table["name"]}_constraint UNIQUE ({",".join(table["constraint"])})' if table.get('constraint') else ''
            foreign_keys = f''',{','.join(map(lambda f_key: f'FOREIGN KEY ({f_key["col"]}) REFERENCES {f_key["target"]} (id)', table['foreign_keys']))}''' if table.get('foreign_keys') else ''
            query = f'CREATE TABLE IF NOT EXISTS {table["name"]} ({cols}{constraint}{foreign_keys})'
            try:
                with self.engine.connect() as conn:
                    conn.execute(query)
            except exc.SQLAlchemyError as error:
                return False, error
        return True, None

    def truncate_tables(self, table_names):
        try:
            query = f'TRUNCATE {",".join(table_names)}'
            with self.engine.connect() as conn:
                conn.execute(query)
        except exc.SQLAlchemyError as error:
            return False, error
        return True, None

    def select_query(self, sql, params=None):
        try:
            data = pd.read_sql_query(text(sql), self.engine, params=params)
        except exc.SQLAlchemyError as error:
            return False, None, error
        return True, data, None

    def insert_data(self, table_name, data):
        try:
            data.to_sql(table_name, self.engine, if_exists='append', index_label='id')
        except exc.SQLAlchemyError as error:
            return False, error
        return True, None
