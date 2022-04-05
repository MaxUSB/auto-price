from flask import Flask, request
from flask_cors import CORS
from .predictor import Predictor
from flask_restful import Api, Resource, reqparse


class Server:
    def __init__(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        CORS(self.app, resources={r"/*": {"origins": "*"}})

    class CatalogsAPI(Resource):
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
        @staticmethod
        def post():
            data = request.json.get('data')
            predictor = Predictor()
            predictor.restore_model()
            success, predictions = predictor.predict(data)
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
        self.api.add_resource(self.CatalogsAPI, '/catalogs')
        self.api.add_resource(self.PredictorAPI, '/predict')
        self.api.init_app(self.app)
        self.app.run(debug=True, port=port)
