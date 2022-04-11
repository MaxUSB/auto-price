import argparse
from modules import Parser


def run(start_price, end_price, increment):
    rc = None
    parser = Parser()

    print('AutoRu parsing...')
    rc = parser.get_autoru_cars(start_price, end_price, increment)

    return rc


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("-s", dest="start_price", default=0, type=int)
    args_parser.add_argument("-e", dest="end_price", default=20_000_000, type=int)
    args_parser.add_argument("-i", dest="increment", default=500_000, type=int)
    args = args_parser.parse_args()
    raise SystemExit(run(args.start_price, args.end_price, args.increment))
