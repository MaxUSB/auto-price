import sys
import pandas as pd
from sklearn.linear_model import Ridge
from .utils import get_config, get_data, save_data


class Predictor:
    def __init__(self):
        self.config = get_config('predictor')
        self.target = self.config['target']
        self.features = self.config['features']
        self.filters = self.config['filters']

        self.model = None
        self.error_model = None
        self.custom_encode_dicts = {}

    def __filter_data(self, data):
        for field in self.filters.keys():
            filter_params = self.filters[field]
            if filter_params['filter_type'] == 'binary_union':
                data[field] = data[field].apply(
                    lambda x: filter_params['true_value'] if x in filter_params['condition_values'] else filter_params['false_value']
                )
            elif filter_params['filter_type'] == 'simple_filter':
                data = data[data[field].isin(filter_params['values'])]
            else:
                print(f"error: invalid filter type {filter_params['filter_type']}", file=sys.stderr)
        return data

    def __set_custom_field_encode_dicts(self, data):
        for field in [k for k, v in self.features.items() if v == 'custom']:
            if field == 'Mark':
                self.custom_encode_dicts[field] = data.groupby('Mark')['Price'].mean()
            elif field == 'City':
                cities = data[['City']].drop_duplicates()
                cities['CityID'] = cities['City'].astype('category')
                cities['CityID'] = cities['CityID'].cat.codes
                self.custom_encode_dicts[field] = cities.set_index('City')['CityID']
            else:
                print(f'error: not found set encode dict handle for {field} field', file=sys.stderr)

    def __encode_fields(self, data):
        for field in self.features.keys():
            encoding_type = self.features[field]
            if encoding_type == 'custom':
                custom_encode_dict = self.custom_encode_dicts[field]
                data[field] = data[field].apply(
                    lambda x: custom_encode_dict.loc[x] if x in custom_encode_dict.index else custom_encode_dict.mean()
                )
            elif encoding_type == 'one-hot':
                data = pd.get_dummies(data, columns=[field], prefix=[field])
            elif encoding_type == 'none':
                continue
            else:
                print(f'error: not found {encoding_type} encoding type handle', file=sys.stderr)
        return data

    def fit(self, data):
        try:
            data = data[self.features.keys()]
            print('filtering data...', end=' ')
            data = self.__filter_data(data.copy())
            print('done.\nsetting custom field encode dicts...', end=' ')
            self.__set_custom_field_encode_dicts(data)
            print('done.\nencoding fields...', end=' ')
            data = self.__encode_fields(data.copy())
            print('done.\ncreating training pool...', end=' ')
            x = data.drop(columns=self.target)
            y = data[self.target]
            print('done.\ncreating model...', end=' ')
            self.model = Ridge()
            print('done.\ntraining model...', end=' ')
            self.model.fit(x, y)
            print('done.\ncreating error model...', end=' ')
            error_df = pd.DataFrame({
                'real': y,
                'predicted': self.model.predict(x)
            })
            error_df['error'] = error_df.apply(lambda row: abs(row['real'] - row['predicted']) / row['real'], axis=1)
            self.error_model = Ridge()
            print('done.\ntraining error model...', end=' ')
            self.error_model.fit(x, error_df['error'])
            print('done.')
            return True, None
        except Exception as e:
            return False, e

    def predict(self, data):
        try:
            result = {}
            data[self.target] = 0
            data = data[self.features.keys()]
            print('filtering data...', end=' ')
            data = self.__filter_data(data.copy())
            print('done.\nencoding fields...', end=' ')
            data = self.__encode_fields(data.copy())
            data.drop(columns=self.target, inplace=True)
            false_binary_columns = [col for col in self.model.feature_names_in_ if col not in data.columns]
            if false_binary_columns:
                data[false_binary_columns] = 0
            print('done.\npredicting price...', end=' ')
            result[self.target] = int(self.model.predict(data)[0])
            print('done.\npredicting error...', end=' ')
            result['PredictedError'] = round(self.error_model.predict(data)[0], 2)
            print('done.')
            return True, result
        except Exception as e:
            print(f'error: {e}', file=sys.stderr, flush=True)
            return False, None

    def store_model(self):
        model_data = {
            'model': self.model,
            'error_model': self.error_model,
            'custom_encode_dicts': self.custom_encode_dicts,
        }
        return save_data(model_data, 'predictor_model.pickle', 'models')

    def restore_model(self):
        model_data = get_data('predictor_model.pickle', 'models')
        if model_data is None:
            return False
        self.model = model_data['model']
        self.error_model = model_data['error_model']
        self.custom_encode_dicts = model_data['custom_encode_dicts']
        return True
