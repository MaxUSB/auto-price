import argparse
from modules import Scheduler


def run(verbose):
    scheduler = Scheduler(verbose)
    scheduler.run()


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("-v", dest="verbose", action=argparse.BooleanOptionalAction)
    args = args_parser.parse_args()
    raise SystemExit(run(args.verbose))
