from modules import CatalogFiller
from modules.utils import get_data


def run():
    rc = None
    catalog_filler = CatalogFiller()

    print('AutoRu fill catalogs...')
    cars = get_data('autoru_learn.csv', 'raw')
    rc = catalog_filler.fill_catalogs(cars)

    return rc


if __name__ == '__main__':
    raise SystemExit(run())
