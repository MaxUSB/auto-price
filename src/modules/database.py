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

    def create_table(self, schema):
        cols_list = []
        for col in schema['cols']:
            cols_list.append(f'''{col['name']} {col['type']}''')
        cols = ','.join(cols_list)
        constraints_list = []
        for constraint in schema['constraints']:
            cons_cols = ','.join(constraint['cols'])
            constraints_list.append(f'''
                CONSTRAINT {constraint['constraint_name']} UNIQUE ({cons_cols})
            ''')
        constraints = ','.join(constraints_list)
        if len(constraints_list) > 0:
            constraints = ',' + constraints
        foreign_keys_list = []
        for foreign_key in schema['foreign_keys']:
            foreign_keys_list.append(f'''
                FOREIGN KEY ({foreign_key['col_in_this_table']}) 
                REFERENCES {foreign_key['target_table']} ({foreign_key['col_in_target_table']})
            ''')
        foreign_keys = ','.join(foreign_keys_list)
        if len(foreign_keys_list) > 0:
            foreign_keys = ',' + foreign_keys
        create_query = f'''
            CREATE TABLE IF NOT EXISTS {schema['table_name']} (
                        {cols}
                        {constraints}
                        {foreign_keys}
                    )
        '''
        conn = self.engine.connect()
        try:
            conn.execute(create_query)
        except:
            return

    def insert_table(self, schema, cols_list, data):
        cols = []
        for col in cols_list:
            cols.append(col['name'])
        cols = ','.join(cols)
        conn = self.engine.connect()
        for row in data:
            values = ','.join(row)
            insert_query = f'''
                INSERT INTO {schema['table_name']} ({cols}) values({values})
            '''
            try:
                conn.execute(insert_query)
            except:
                return
