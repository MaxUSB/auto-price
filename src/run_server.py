import argparse
from modules import Server


def run(verbose, port):
    server = Server(verbose)
    server.run(port)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("-v", dest="verbose", action=argparse.BooleanOptionalAction)
    args_parser.add_argument("-p", dest="port", default=3001, type=int)
    args = args_parser.parse_args()
    raise SystemExit(run(args.verbose, args.port))
