import sys
import argparse
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Configuration:
    data_folder: str


DEFAULT_CONFIG = Configuration(data_folder='./events/')


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_doing = subparsers.add_parser('doing',
                                         help='Record an activity')

    parser_doing.add_argument('event', help='The event you are recording')

    parser.add_argument('-l', '--list',
                        action='store_true',
                        help='List the activities recorded',)

    args = parser.parse_args(argv)

    if not args.list:
        record_event(args.event)
        print('Recorded doing {activity} at {time}'.format(
            activity=args.event,
            time=datetime.now().strftime('%H:%M')))
    elif args.list:
        pass


def record_event(
    activity,
    time=datetime.now(),
    data_path=DEFAULT_CONFIG.data_folder
):
    with open(data_path + time.strftime('%Y-%m') + '.csv', mode='a') as file:
        file.write(','.join([activity, str(time), '\n']))


def _parse_args(args):
    argdict = {}
    arglist = []

    arg_iter = enumerate(args)

    for i, arg in arg_iter:
        if arg.startswith('--'):
            argdict.update({arg[2:]: args[i+1]})
            next(arg_iter)
        elif arg.startswith('-'):
            argdict.update({arg[1:]: args[i+1]})
            next(arg_iter)
        else:
            arglist.append(arg)

    return arglist, argdict


if __name__ == '__main__':
    main()
