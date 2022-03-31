import argparse
from modules import Parser


def run(start_price, end_price):
    rc = None
    parser = Parser(start_price, end_price)

    print('AutoRu parsing:')
    rc = parser.get_autoru_cars()

    return rc


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("-s", dest="start_price", default=100_000, type=int)
    args_parser.add_argument("-e", dest="end_price", default=2_000_000, type=int)
    args = args_parser.parse_args()
    raise SystemExit(run(args.start_price, args.end_price))
