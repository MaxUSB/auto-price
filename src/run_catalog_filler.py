from modules import CatalogFiller


def run():
    catalog_filler = CatalogFiller(file_name='autoru_learn.csv', file_path='raw')
    catalog_filler.fill_catalogs()


if __name__ == '__main__':
    raise SystemExit(run())
