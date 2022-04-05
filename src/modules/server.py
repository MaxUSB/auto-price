from flask_cors import CORS
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

        self.initedCatalogsAPI = self.CatalogsAPI.init()
        self.initedPredictorAPI = self.PredictorAPI.init(predictor)

    class CatalogsAPI(Resource):
        @classmethod
        def init(cls):
            return cls

        @staticmethod
        def get():
            mark = request.args.get('mark')
            if mark is None:
                return {
                           'success': True,
                           'data': {'mark': ['Honda', 'Dodge']},
                           'error': None,
                       }, 200
            else:
                return {
                           'success': True,
                           'data': {'capacity': ['2000', '2400'] if mark == 'Honda' else ['4000', '5800']},
                           'error': None,
                       }, 200

    class PredictorAPI(Resource):
        @classmethod
        def init(cls, predictor):
            cls.predictor = predictor
            return cls

        def post(self):
            data = request.json.get('data')
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

    def run(self, port):
        self.api.add_resource(self.initedCatalogsAPI, '/catalogs')
        self.api.add_resource(self.initedPredictorAPI, '/predict')
        self.app.run(debug=True, port=port)
