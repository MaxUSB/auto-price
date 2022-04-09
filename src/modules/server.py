import sys
import pandas as pd
from flask_cors import CORS
from .utils import get_config
from .database import DataBase
from .predictor import Predictor
from flask import Flask, request
from flask_restful import Api, Resource


class Server:
    def __init__(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        CORS(self.app, resources={r"/*": {"origins": "http://localhost:3000"}})

        predictor = Predictor()
        predictor.restore_model()
        db_config = get_config('db')

        self.initedCatalogsAPI = self.CatalogsAPI.init(db_config)
        self.initedPredictorAPI = self.PredictorAPI.init(predictor)

    class CatalogsAPI(Resource):
        @classmethod
        def init(cls, db_config):
            cls.db = DataBase(db_config['catalogs'])
            cls.catalog_queries = {
                'marks': 'SELECT mark FROM marks',
                'cities': 'SELECT city FROM cities',
                'mark_params': 'SELECT horse_power FROM marks m JOIN horse_powers hp ON m.id = hp.mark_id WHERE mark = :mark',
            }
            cls.catalog_params = {
                'marks': ['mark'],
                'cities': ['city'],
                'mark_params': ['hp'],
            }
            return cls

        def get(self):
            try:
                catalog = request.args.get('catalog')
                mark = request.args.get('mark')
                if catalog is None:
                    return {
                               'success': False,
                               'data': {},
                               'error': 'Отсутствует параметр "catalog"',
                           }, 400
                success, result, error = self.db.select_query(self.catalog_queries[catalog], {'mark': mark})
                if success:
                    result = result.astype(str)
                    return {
                               'success': True,
                               'data': {param: result[result.columns[i]].tolist() for i, param in enumerate(self.catalog_params[catalog])},
                               'error': None,
                           }, 200
                else:
                    print(f'error: {error}', file=sys.stderr, flush=True)
                    return {
                               'success': False,
                               'data': {},
                               'error': f'Не удалось получить каталог "{catalog}"',
                           }, 500
            except Exception as error:
                print(f'error: {error}', file=sys.stderr, flush=True)
                return {
                           'success': False,
                           'data': {},
                           'error': 'Что-то пошло не так...',
                       }, 500

    class PredictorAPI(Resource):
        @classmethod
        def init(cls, predictor):
            cls.predictor = predictor
            return cls

        def post(self):
            try:
                data = request.json.get('data')
                data = pd.DataFrame(data, index=[0])
                data.columns = list(col[0].capitalize() + (col[1:] if len(col) > 2 else col[1:].capitalize()) for col in data.columns)
                # success, predictions = self.predictor.predict(data)
                success, predictions = True, {'Price': 1100000, 'PredictedError': 0.09}
                if not success:
                    return {
                               'success': False,
                               'data': {},
                               'error': 'Не удалось предсказать стоимость',
                           }, 500
                else:
                    return {
                               'success': True,
                               'data': predictions,
                               'error': None,
                           }, 200
            except Exception as error:
                print(f'error: {error}', file=sys.stderr, flush=True)
                return {
                           'success': False,
                           'data': {},
                           'error': 'Что-то пошло не так...',
                       }, 500

    def run(self, port):
        self.api.add_resource(self.initedCatalogsAPI, '/catalogs')
        self.api.add_resource(self.initedPredictorAPI, '/predict')
        self.app.run(debug=True, port=port)
