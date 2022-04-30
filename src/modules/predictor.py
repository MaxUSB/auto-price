import sys
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from .utils import get_config, get_data, save_data


class Predictor:
    def __init__(self):
        self.config = get_config('predictor')
        self.target = self.config['target']
        self.features = self.config['features']

        self.model_e = None
        self.model_m = None
        self.model_p = None
        self.error_model_e = None
        self.error_model_m = None
        self.error_model_p = None
        self.custom_encode_dicts = {}
        self.segments = pd.DataFrame()
        self.cars = pd.DataFrame()

    def __set_custom_field_encode_dicts(self, data):
        for field in [k for k, v in self.features.items() if v == 'custom']:
            if field == 'Mark':
                self.custom_encode_dicts[field] = data.groupby('Mark')['Price'].mean()
            elif field == 'Model':
                self.custom_encode_dicts[field] = data.groupby('Model')['Price'].mean()
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

    def __segment_split(self, data):
        data_e = data[data['PriceSegment'] == 'ECONOMY'].drop(columns=['PriceSegment'])
        data_m = data[data['PriceSegment'] == 'MEDIUM'].drop(columns=['PriceSegment'])
        data_p = data[data['PriceSegment'] == 'PREMIUM'].drop(columns=['PriceSegment'])
        models_e = data_e['Model'].unique().tolist()
        models_m = data_m['Model'].unique().tolist()
        models_p = data_p['Model'].unique().tolist()
        self.segments = pd.concat([self.segments, pd.DataFrame({'Model': models_e, 'Segment': ['ECONOMY'] * len(models_e)})], ignore_index=True)
        self.segments = pd.concat([self.segments, pd.DataFrame({'Model': models_m, 'Segment': ['MEDIUM'] * len(models_m)})], ignore_index=True)
        self.segments = pd.concat([self.segments, pd.DataFrame({'Model': models_p, 'Segment': ['PREMIUM'] * len(models_p)})], ignore_index=True)
        return data_e, data_m, data_p

    def __get_segment_model(self, model):
        segment = self.segments[self.segments['Model'] == model]['Segment']
        if segment.empty:
            return self.model_m, self.error_model_m
        else:
            segment = segment.iloc[0]
        if segment == 'ECONOMY':
            return self.model_e, self.error_model_e
        elif segment == 'MEDIUM':
            return self.model_m, self.error_model_m
        elif segment == 'PREMIUM':
            return self.model_p, self.error_model_p

    def fit(self, data):
        try:
            data = data[self.features.keys()]
            print('setting custom field encode dicts...', end=' ')
            self.__set_custom_field_encode_dicts(data)
            print('done.\nsplitting data by segment...', end=' ')
            data_e, data_m, data_p = self.__segment_split(data)
            print('done.\nencoding fields...', end=' ')
            data_e = self.__encode_fields(data_e.copy())
            data_m = self.__encode_fields(data_m.copy())
            data_p = self.__encode_fields(data_p.copy())
            print('done.\ncreating training pools...', end=' ')
            x_e = data_e.drop(columns=self.target)
            x_m = data_m.drop(columns=self.target)
            x_p = data_p.drop(columns=self.target)
            y_e = data_e[self.target]
            y_m = data_m[self.target]
            y_p = data_p[self.target]
            print('done.\ncreating models...', end=' ')
            self.model_e = RandomForestRegressor(random_state=369)
            self.model_m = RandomForestRegressor(random_state=369)
            self.model_p = RandomForestRegressor(random_state=369)
            print('done.\ntraining models...', end=' ')
            self.model_e.fit(x_e, y_e)
            self.model_m.fit(x_m, y_m)
            self.model_p.fit(x_p, y_p)
            print('done.\ncreating error models...', end=' ')
            error_df_e = pd.DataFrame({'real': y_e, 'predicted': self.model_e.predict(x_e)})
            error_df_m = pd.DataFrame({'real': y_m, 'predicted': self.model_m.predict(x_m)})
            error_df_p = pd.DataFrame({'real': y_p, 'predicted': self.model_p.predict(x_p)})
            error_df_e['error'] = error_df_e.apply(lambda row: abs(row['real'] - row['predicted']) / row['real'], axis=1)
            error_df_m['error'] = error_df_m.apply(lambda row: abs(row['real'] - row['predicted']) / row['real'], axis=1)
            error_df_p['error'] = error_df_p.apply(lambda row: abs(row['real'] - row['predicted']) / row['real'], axis=1)
            self.error_model_e = RandomForestRegressor(random_state=369)
            self.error_model_m = RandomForestRegressor(random_state=369)
            self.error_model_p = RandomForestRegressor(random_state=369)
            print('done.\ntraining error models...', end=' ')
            self.error_model_e.fit(x_e, error_df_e['error'])
            self.error_model_m.fit(x_m, error_df_m['error'])
            self.error_model_p.fit(x_p, error_df_p['error'])
            print('done.')
            return True, None
        except Exception as e:
            return False, e

    def predict(self, data):
        try:
            result = {
                'Similar': self.cars[
                    (self.cars['Mark'] == data['Mark'].iloc[0]) & (self.cars['Model'] == data['Model'].iloc[0])
                    ][self.features.keys()].to_dict('records')[:10]
            }
            data[self.target] = 0
            data['PriceSegment'] = 'UNKNOWN'
            data = data[self.features.keys()]
            print('getting segment model...', end=' ')
            model, error_model = self.__get_segment_model(data['Model'].iloc[0])
            print('done.\nencoding fields...', end=' ')
            data = self.__encode_fields(data.copy())
            data.drop(columns=self.target, inplace=True)
            false_binary_columns = [col for col in model.feature_names_in_ if col not in data.columns]
            if false_binary_columns:
                data[false_binary_columns] = 0
            data = data[model.feature_names_in_]
            print('done.\npredicting price...', end=' ')
            result[self.target] = int(model.predict(data)[0])
            print('done.\npredicting error...', end=' ')
            print(int(result[self.target] * abs(round(error_model.predict(data)[0], 2))))
            result['PredictedError'] = int(result[self.target] * abs(round(error_model.predict(data)[0], 2)))
            print('done.')
            return True, result
        except Exception as e:
            print(f'error: {e}', file=sys.stderr, flush=True)
            return False, None

    def store_model(self):
        model_data = {
            'model_e': self.model_e,
            'model_m': self.model_m,
            'model_p': self.model_p,
            'error_model_e': self.error_model_e,
            'error_model_m': self.error_model_m,
            'error_model_p': self.error_model_p,
            'custom_encode_dicts': self.custom_encode_dicts,
            'segments': self.segments,
        }
        return save_data(model_data, 'predictor_model.pickle', 'models')

    def restore_model(self):
        model_data = get_data('predictor_model.pickle', 'models')
        if model_data is None:
            return False
        self.model_e = model_data['model_e']
        self.model_m = model_data['model_m']
        self.model_p = model_data['model_p']
        self.error_model_e = model_data['error_model_e']
        self.error_model_m = model_data['error_model_m']
        self.error_model_p = model_data['error_model_p']
        self.custom_encode_dicts = model_data['custom_encode_dicts']
        self.segments = model_data['segments']
        self.cars = get_data('autoru_learn.csv', 'raw')
        return True
