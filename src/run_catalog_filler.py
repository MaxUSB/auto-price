import argparse
from modules import CatalogFiller
from modules.utils import get_data


def run(verbose):
    rc = None
    catalog_filler = CatalogFiller(verbose)

    print('AutoRu fill catalogs...')
    cars = get_data('autoru_learn.csv', 'raw')
    rc = catalog_filler.fill_catalogs(cars)

    return rc


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("-v", dest="verbose", action=argparse.BooleanOptionalAction)
    args = args_parser.parse_args()
    raise SystemExit(run(args.verbose))
