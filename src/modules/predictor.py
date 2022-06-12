import sys
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from .utils import get_config, get_data, save_data


class Predictor:
    def __init__(self, verbose=False):
        self.v = verbose
        self.config = get_config('predictor')
        self.target = self.config['target']
        self.features = self.config['features']

        self.model_e = None
        self.model_m_and_p = None
        self.error_model_e = None
        self.error_model_m_and_p = None
        self.custom_encode_dicts = {}
        self.segments = pd.DataFrame()
        self.cars = pd.DataFrame()

    def __set_custom_field_encode_dicts(self, data):
        for field in [k for k, v in self.features.items() if v == 'custom']:
            if field == 'Mark':
                self.custom_encode_dicts[field] = data.groupby('Mark')['Price'].median()
            elif field == 'Model':
                self.custom_encode_dicts[field] = data.groupby('Model')['Price'].median()
            elif field == 'City':
                cities = data[['City']].drop_duplicates()
                cities['CityID'] = cities['City'].astype('category')
                cities['CityID'] = cities['CityID'].cat.codes
                self.custom_encode_dicts[field] = cities.set_index('City')['CityID']
            else:
                print(f'error (predictor): not found set encode dict handle for {field} field', file=sys.stderr)

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
                print(f'error (predictor): not found {encoding_type} encoding type handle', file=sys.stderr)
        return data

    def __segment_split(self, data):
        data_e = data[data['PriceSegment'] == 'ECONOMY'].drop(columns=['PriceSegment'])
        data_m_and_p = data[data['PriceSegment'].isin('MEDIUM', 'PREMIUM')].drop(columns=['PriceSegment'])
        models_e = data_e['Model'].unique().tolist()
        models_m_and_p = data_m_and_p['Model'].unique().tolist()
        self.segments = pd.concat([self.segments, pd.DataFrame({'Model': models_e, 'Segment': ['ECONOMY'] * len(models_e)})], ignore_index=True)
        self.segments = pd.concat([self.segments, pd.DataFrame({'Model': models_m_and_p, 'Segment': ['MEDIUM+PREMIUM'] * len(models_m_and_p)})], ignore_index=True)
        return data_e, data_m_and_p

    def __get_segment_model(self, model):
        segment = self.segments[self.segments['Model'] == model]['Segment']
        if segment.empty:
            return self.model_m_and_p, self.error_model_m_and_p
        else:
            segment = segment.iloc[0]
        if segment == 'ECONOMY':
            return self.model_e, self.error_model_e
        elif segment == 'MEDIUM+PREMIUM':
            return self.model_m_and_p, self.error_model_m_and_p

    def fit(self, data):
        try:
            data = data[self.features.keys()]
            if self.v:
                print('setting custom field encode dicts...', end=' ')
            self.__set_custom_field_encode_dicts(data)
            if self.v:
                print('done.\nsplitting data by segment...', end=' ')
            data_e, data_m_and_p = self.__segment_split(data)
            if self.v:
                print('done.\nencoding fields...', end=' ')
            data_e = self.__encode_fields(data_e.copy())
            data_m_and_p = self.__encode_fields(data_m_and_p.copy())
            if self.v:
                print('done.\ncreating training pools...', end=' ')
            x_e = data_e.drop(columns=self.target)
            x_m_and_p = data_m_and_p.drop(columns=self.target)
            y_e = data_e[self.target]
            y_m_and_p = data_m_and_p[self.target]
            if self.v:
                print('done.\ncreating models...', end=' ')
            self.model_e = RandomForestRegressor(random_state=369)
            self.model_m_and_p = RandomForestRegressor(random_state=369)
            if self.v:
                print('done.\ntraining models...', end=' ')
            self.model_e.fit(x_e, y_e)
            self.model_m_and_p.fit(x_m_and_p, y_m_and_p)
            if self.v:
                print('done.\ncreating error models...', end=' ')
            error_df_e = pd.DataFrame({'real': y_e, 'predicted': self.model_e.predict(x_e)})
            error_df_m_and_p = pd.DataFrame({'real': y_m_and_p, 'predicted': self.model_m_and_p.predict(x_m_and_p)})
            error_df_e['error'] = error_df_e.apply(lambda row: abs(row['real'] - row['predicted']) / row['real'], axis=1)
            error_df_m_and_p['error'] = error_df_m_and_p.apply(lambda row: abs(row['real'] - row['predicted']) / row['real'], axis=1)
            self.error_model_e = RandomForestRegressor(random_state=369)
            self.error_model_m_and_p = RandomForestRegressor(random_state=369)
            if self.v:
                print('done.\ntraining error models...', end=' ')
            self.error_model_e.fit(x_e, error_df_e['error'])
            self.error_model_m_and_p.fit(x_m_and_p, error_df_m_and_p['error'])
            if self.v:
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
            if self.v:
                print('getting segment model...', end=' ')
            model, error_model = self.__get_segment_model(data['Model'].iloc[0])
            if self.v:
                print('done.\nencoding fields...', end=' ')
            data = self.__encode_fields(data.copy())
            data.drop(columns=self.target, inplace=True)
            false_binary_columns = [col for col in model.feature_names_in_ if col not in data.columns]
            if false_binary_columns:
                data[false_binary_columns] = 0
            data = data[model.feature_names_in_]
            if self.v:
                print('done.\npredicting price...', end=' ')
            result[self.target] = int(model.predict(data)[0])
            if self.v:
                print('done.\npredicting error...', end=' ')
            result['PredictedError'] = int(result[self.target] * abs(round(error_model.predict(data)[0], 2)))
            if self.v:
                print('done.')
            return True, result
        except Exception as e:
            print(f'error (predictor): {e}', file=sys.stderr, flush=True)
            return False, None

    def store_model(self):
        model_data = {
            'model_e': self.model_e,
            'model_m_and_p': self.model_m_and_p,
            'error_model_e': self.error_model_e,
            'error_model_m_and_p': self.error_model_m_and_p,
            'custom_encode_dicts': self.custom_encode_dicts,
            'segments': self.segments,
        }
        return save_data(model_data, 'predictor_model.pickle', 'models')

    def restore_model(self):
        model_data = get_data('predictor_model.pickle', 'models')
        if model_data is None:
            return False
        self.model_e = model_data['model_e']
        self.model_m_and_p = model_data['model_m_and_p']
        self.error_model_e = model_data['error_model_e']
        self.error_model_m_and_p = model_data['error_model_m_and_p']
        self.custom_encode_dicts = model_data['custom_encode_dicts']
        self.segments = model_data['segments']
        self.cars = get_data('autoru_learn.csv', 'raw')
        return True
