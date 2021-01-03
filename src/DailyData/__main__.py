import sys
import argparse
from importlib import resources
import pathlib


def take_args(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()

    parser.add_argument('--config-file', action='store_true',
                        help='Print the location of the configuration file. This can be piped to a text editor to edit it.')

    args = parser.parse_args(argv)

    if args.config_file:
        with resources.path(__package__, 'config.json') as cfg_path:
            print(cfg_path.absolute())
    else:
        parser.print_help()


if __name__ == "__main__":
    take_args(['--config_file'])
