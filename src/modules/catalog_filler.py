import sys
from .utils import get_config
from .database import DataBase


class CatalogFiller:
    def __init__(self):
        self.config = get_config('catalogFiller')
        self.db = DataBase(get_config('db')['catalogs'])

    def __fill_marks(self, db):
        marks = list(filter(lambda item: item['table_name'] == 'marks', self.config['tables']))[0]
        db.create_table(marks)
        cols_list = list(filter(lambda item: item['name'] != 'id', marks['cols']))
        db.insert_data(marks, cols_list, self.__get_text_col_formatted_data('Mark'))

    def __fill_cities(self, db):
        cities = list(filter(lambda item: item['table_name'] == 'cities', self.config['tables']))[0]
        db.create_table(cities)
        cols_list = list(filter(lambda item: item['name'] != 'id', cities['cols']))
        db.insert_data(cities, cols_list, self.__get_text_col_formatted_data('City'))

    def __fill_horse_powers(self, db):
        horse_powers = list(filter(lambda item: item['table_name'] == 'horse_powers', self.config['tables']))[0]
        db.create_table(horse_powers)
        cols_list = list(filter(lambda item: item['name'] != 'id', horse_powers['cols']))
        db.insert_data(horse_powers, cols_list, self.__get_mark_formatted_data(db, ['Mark', 'HP']))

    def __get_text_col_formatted_data(self, col):
        data = []
        for item in self.cars[col].unique():
            data.append([f'\'{item}\''])
        return data

    def __get_mark_formatted_data(self, db, cols):
        data = []
        for i, row in self.cars[cols].drop_duplicates().iterrows():
            values = []
            for value in row:
                if isinstance(value, str):
                    select_query = f'''
                                        SELECT id from marks
                                        WHERE mark = '{value}'
                                    '''
                    try:
                        auto = db.select_query(select_query)[1]['id'].values[0]
                        values.append(auto.__str__())
                    except:
                        continue
                elif isinstance(value, int):
                    values.append(value.__str__())
            data.append(values)
        return data

    def fill_catalogs(self, cars):
        print('create catalogs if not exists...', end=' ')
        success, error = self.db.create_tables(self.config['tables'])
        if not success:
            print(f'error: {error}', file=sys.stderr)
            return 1

        print('done.\ntruncate catalogs...', end=' ')
        success, error = self.db.truncate_tables(list(map(lambda table: table['name'], self.config['tables'])))
        if not success:
            print(f'error: {error}', file=sys.stderr)
            return 1

        print('done.\nfill catalogs...', end=' ')

        return 0
