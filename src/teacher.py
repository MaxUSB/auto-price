import os
import pandas as pd
from modules import Predictor


def teach():
    print('getting data...', end=' ')
    data = pd.read_csv(f"{os.getenv('project_path')}/data/autoru_learn.csv")

    print('done.\nfit model...')
    predictor = Predictor()
    success, error = predictor.fit(data)
    if not success:
        print(f'error: {error}')
        return 1

    print('done.\nstore model...')
    success, error = predictor.store_model()
    if not success:
        print(f'error: {error}')
        return 1


if __name__ == '__main__':
    raise SystemExit(teach())
