import sys
import argparse
from importlib import resources

from . import tracker
from . import time_management


def take_args(argv=sys.argv[1:]):
    from . import config

    parser = argparse.ArgumentParser()

    parser.add_argument('--config-file', action='store_true',
                        help='Print the location of the configuration file. This can be piped to a text editor to edit it.')

    parser.add_argument('-j', '--journal', action='store_true',
                        help='Create a new journal entry')

    args = parser.parse_args(argv)

    if args.config_file:
        with resources.path(__package__, 'config.json') as cfg_path:
            print(cfg_path.absolute())
    elif args.journal:
        tracker.Journaller(config.tracker).record_and_write_to_file()
    else:
        parser.print_help()


if __name__ == "__main__":
    take_args()
