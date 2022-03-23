from modules import Parser


def run():
    rc = None
    parser = Parser(100000, 1000000)

    print('AutoRu parsing:')
    rc = parser.get_autoru_cars()

    return rc


if __name__ == '__main__':
    raise SystemExit(run())
