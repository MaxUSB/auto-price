import sys
import pandas as pd
from .utils import get_config
from .database import DataBase


class CatalogFiller:
    def __init__(self):
        self.config = get_config('catalogFiller')
        self.db = DataBase(get_config('db')['catalogs'])

    def __save_data_df(self, data, field, table_name):
        to_save = pd.DataFrame(data[field].unique(), columns=[field.lower()])
        success, error = self.db.insert_data(table_name, to_save)
        return success, to_save, error

    def __save_dependent_data_df(self, base, data, field, table_name):
        base_field = [col for col in base.columns if 'id' not in col][0].capitalize()
        rename_dict = {base_field: f'{base_field.lower()}_id', field: field.lower()}
        to_save = data.drop_duplicates([base_field, field], ignore_index=True)[[base_field, field]]
        to_save[base_field] = to_save[base_field].apply(lambda x: base.index[base[base_field.lower()] == x].tolist()[0])
        to_save = to_save.rename(columns=rename_dict)
        success, error = self.db.insert_data(table_name, to_save)
        return success, to_save, error

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

        print('done.\nfill base catalogs...', end=' ')
        success, cities, error = self.__save_data_df(cars, 'City', 'cities')
        if not success:
            print(f'error: {error}', file=sys.stderr)
            return 1
        success, marks, error = self.__save_data_df(cars, 'Mark', 'marks')
        if not success:
            print(f'error: {error}', file=sys.stderr)
            return 1

        print('done.\nfill dependent catalogs...', end=' ')
        success, models, error = self.__save_dependent_data_df(marks, cars, 'Model', 'models')
        if not success:
            print(f'error: {error}', file=sys.stderr)
            return 1
        success, horsepower, error = self.__save_dependent_data_df(models, cars, 'Horsepower', 'horsepower')
        if not success:
            print(f'error: {error}', file=sys.stderr)
            return 1
        print('done.')

        return 0
