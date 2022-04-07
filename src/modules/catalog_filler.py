from .database import DataBase
from .utils import get_config, get_data


class CatalogFiller:
    def __init__(self, file_name, file_path):
        self.cars = get_data(file_name, file_path)
        self.config = get_config('catalog')
        pass

    def fill_catalogs(self):
        try:
            print('Connecting to database...')
            db = DataBase(connect_data=get_config('db')['catalogs'])
            print('Fill catalogs...')
            self.__fill_marks(db)
            self.__fill_cities(db)
            self.__fill_horse_powers(db)
            print('Done.')
        except:
            print('Connection failed')

    def __fill_marks(self, db):
        marks = list(filter(lambda item: item['table_name'] == 'marks', self.config['tables']))[0]
        db.create_table(marks)
        cols_list = list(filter(lambda item: item['name'] != 'id', marks['cols']))
        db.insert_table(marks, cols_list, self.__get_text_col_formatted_data('Mark'))

    def __fill_capacities(self, db):
        capacities = list(filter(lambda item: item['table_name'] == 'capacities', self.config['tables']))[0]
        db.create_table(capacities)
        cols_list = list(filter(lambda item: item['name'] != 'id', capacities['cols']))
        db.insert_table(capacities, cols_list, self.__get_mark_formatted_data(db, ['Mark', 'Capacity']))

    def __fill_cities(self, db):
        cities = list(filter(lambda item: item['table_name'] == 'cities', self.config['tables']))[0]
        db.create_table(cities)
        cols_list = list(filter(lambda item: item['name'] != 'id', cities['cols']))
        db.insert_table(cities, cols_list, self.__get_text_col_formatted_data('City'))

    def __fill_horse_powers(self, db):
        horse_powers = list(filter(lambda item: item['table_name'] == 'horse_powers', self.config['tables']))[0]
        db.create_table(horse_powers)
        cols_list = list(filter(lambda item: item['name'] != 'id', horse_powers['cols']))
        db.insert_table(horse_powers, cols_list, self.__get_mark_formatted_data(db, ['Mark', 'HP']))

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
