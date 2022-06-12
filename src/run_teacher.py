import sys
import argparse
from modules import Predictor
from modules.utils import get_data


def run(verbose):
    if verbose:
        print('getting data...', end=' ')
    data = get_data('autoru_learn.csv', 'raw')
    if data is None:
        print('error (teacher): data is None', file=sys.stderr)

    if verbose:
        print('done.\nfit model...', end=' ')
    predictor = Predictor()
    success, error = predictor.fit(data)
    if not success:
        print(f'error (teacher): {error}', file=sys.stderr)
        return 1

    if verbose:
        print('done.\nstore model...', end=' ')
    success = predictor.store_model()
    if not success:
        return 1
    if verbose:
        print('done.')

    return 0


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("-v", dest="verbose", action=argparse.BooleanOptionalAction)
    args = args_parser.parse_args()
    raise SystemExit(run(args.verbose))
