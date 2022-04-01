import sys
from modules import Predictor
from modules.utils import get_data


def run():
    print('getting data...', end=' ')
    data = get_data('autoru_learn.csv', 'raw')
    if data is None:
        print('error: data is None', file=sys.stderr)

    print('done.\nfit model =>')
    predictor = Predictor()
    success, error = predictor.fit(data)
    if not success:
        print(f'error: {error}', file=sys.stderr)
        return 1

    print('<=\nstore model...', end=' ')
    success = predictor.store_model()
    if not success:
        return 1
    print('done.')

    return 0


if __name__ == '__main__':
    raise SystemExit(run())
