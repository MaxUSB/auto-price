import argparse
from modules import Server


def run():
    server = Server()


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("-p", dest="port", default=6666, type=int)
    args = args_parser.parse_args()
    raise SystemExit(run())
