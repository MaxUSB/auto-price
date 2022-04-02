from flask import Flask, request
from .predictor import Predictor
from flask_restful import Api, Resource, reqparse


class Server:
    def __init__(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)

    class CatalogsAPI(Resource):
        @staticmethod
        def get():
            catalogs = {}  # TODO get catalogs from DB
            return catalogs, 200

    class PredictorAPI(Resource):
        @staticmethod
        def post():
            data = None  # TODO from POST fields
            predictor = Predictor()
            predictor.restore_model()
            predictions = predictor.predict(data)
            if predictions is not None:
                return predictions, 200
            return {}, 500

    def run(self, port):
        self.api.add_resource(self.CatalogsAPI, '/catalogs', '/catalogs/')
        self.api.add_resource(self.PredictorAPI, '/predict', '/predict/')
        self.app.run(debug=True, port=port)
