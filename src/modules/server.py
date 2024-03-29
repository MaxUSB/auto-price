import sys
import pandas as pd
from flask_cors import CORS
from .utils import get_config
from .database import DataBase
from .predictor import Predictor
from flask import Flask, request
from flask_restful import Api, Resource


class Server:
    def __init__(self, verbose=False):
        self.v = verbose
        self.app = Flask(__name__)
        self.api = Api(self.app)
        CORS(self.app, resources={r"/*": {"origins": "http://localhost:3000"}})

        self.initedCatalogsAPI = self.CatalogsAPI.init()
        self.initedPredictorAPI = self.PredictorAPI.init(self.v)

    class CatalogsAPI(Resource):
        @classmethod
        def init(cls):
            db_config = get_config('db')
            cls.db = DataBase(db_config['catalogs'])
            cls.catalog_queries = {
                'cities': 'SELECT city FROM cities',
                'marks': 'SELECT mark FROM marks',
                'models': 'SELECT model FROM marks ma JOIN models mo on mo.mark_id = ma.id WHERE mark = :mark',
                'model_params': '''
                    SELECT horsepower FROM models m
                    JOIN horsepower hp ON hp.model_id = m.id
                    WHERE model = :model
                ''',
            }
            cls.catalog_params = {
                'cities': ['city'],
                'marks': ['mark'],
                'models': ['model'],
                'model_params': ['horsepower'],
            }
            return cls

        def get(self):
            try:
                catalog = request.args.get('catalog')
                mark = request.args.get('mark')
                model = request.args.get('model')
                if catalog is None:
                    return {
                               'success': False,
                               'data': {},
                               'error': 'Отсутствует параметр "catalog"',
                           }, 400
                success, result, error = self.db.select_query(self.catalog_queries[catalog], {'mark': mark, 'model': model})
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
        def init(cls, verbose):
            predictor = Predictor(verbose)
            predictor.restore_model()
            cls.predictor = predictor
            return cls

        def get(self):
            success = self.predictor.restore_model()
            if not success:
                return {
                           'success': False,
                           'data': {},
                           'error': None,
                       }, 500
            else:
                return {
                           'success': True,
                           'data': {},
                           'error': None,
                       }, 200

        def post(self):
            try:
                data = request.json.get('data')
                data = pd.DataFrame(data, index=[0])
                data.columns = list(col[0].capitalize() + (col[1:] if len(col) > 2 else col[1:].capitalize()) for col in data.columns)
                success, predictions = self.predictor.predict(data)
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
        self.api.add_resource(self.initedPredictorAPI, '/predict', '/reload_models')
        self.app.debug = self.v
        self.app.run(port=port)
