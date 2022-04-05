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
            self.__fill_auto_marks(db)
            self.__fill_auto_capacity(db)
            print('Done.')
        except:
            print('Connection failed')

    def __fill_auto_marks(self, db):
        auto_marks = list(filter(lambda item: item['table_name'] == 'marks', self.config['tables']))[0]
        db.create_table(auto_marks)

        data = []
        for item in self.cars['Mark'].unique():
            data.append([f'\'{item}\''])

        cols_list = list(filter(lambda item: item['name'] != 'id', auto_marks['cols']))
        db.insert_table(auto_marks, cols_list, data)

    def __fill_auto_capacity(self, db):
        auto_capacity = list(filter(lambda item: item['table_name'] == 'capacities', self.config['tables']))[0]
        db.create_table(auto_capacity)

        data = []
        for i, row in self.cars[['Mark', 'Capacity']].drop_duplicates().iterrows():
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

        cols_list = list(filter(lambda item: item['name'] != 'id', auto_capacity['cols']))
        db.insert_table(auto_capacity, cols_list, data)
