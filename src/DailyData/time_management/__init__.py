import sys
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Configuration:
    data_folder: str


DEFAULT_CONFIG = Configuration(data_folder='./events/')


def main(argv=sys.argv[1:]):
    if len(argv) == 0:
        # we need to print help
        pass
    else:
        args, kwargs = _parse_args(argv)

        record_event(args[0])
        print('Recorded doing {activity} at {time}'.format(
            activity=args[0],
            time=datetime.now().strftime('%H:%M')))


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
