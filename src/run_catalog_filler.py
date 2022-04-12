from modules import CatalogFiller


def run():
    rc = None
    catalog_filler = CatalogFiller(file_name='autoru_learn.csv', file_path='raw')

    print('AutoRu parsing...')
    rc = catalog_filler.fill_catalogs()

    return rc


if __name__ == '__main__':
    raise SystemExit(run())
