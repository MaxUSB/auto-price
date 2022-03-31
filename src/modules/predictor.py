import os
import pandas as pd
from .utils import get_config, get_data, save_data


class Predictor:
    def __init__(self):
        self.config = get_config('predictor')

    def fit(self, data):
        pass

    def store_model(self):
        pass

    def restore_model(self):
        pass

    def predict(self, data):
        pass
