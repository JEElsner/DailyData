import sys
import argparse
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class Configuration:
    data_folder: str


DEFAULT_CONFIG = Configuration(data_folder='./data/activities/')


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_doing = subparsers.add_parser('doing',
                                         help='Record an activity')

    parser_doing.add_argument('event', help='The event you are recording')

    parser_doing.add_argument('-n', '--new',
                              action='store_true',
                              help='Add a new activity to track')

    parser.add_argument('-l', '--list',
                        action='store_true',
                        help='List the activities recorded')

    args = parser.parse_args(argv)

    if not args.list:
        if record_event(args.event, new=args.new):
            print('Recorded doing {activity} at {time}'.format(
                activity=args.event,
                time=datetime.now().strftime('%H:%M')))
        else:
            print(
                'Unknown activity \'{0}\', did not record.\nUse [-n] if you want to add a new activity.'.format(args.event))
    elif args.list:
        print(get_activity_times()
              .to_string(float_format=lambda s: '{:.2f}'.format(s*100)))


def record_event(
    activity,
    time=datetime.now(),
    data_path=DEFAULT_CONFIG.data_folder,
    new=False
) -> bool:
    with open(data_path + 'list.txt', mode='r+') as act_list:
        if not new and (activity + '\n') not in act_list:
            return False
        elif new:
            act_list.write(activity + '\n')

    with open(data_path + time.strftime('%Y-%m') + '.csv', mode='a') as file:
        file.write(','.join([activity, str(time), '\n']))

    return True


def get_activity_times(data_path=DEFAULT_CONFIG.data_folder, max_time=timedelta(hours=1)) -> pd.DataFrame:
    activity_time = {}

    for csv_path in Path(data_path).glob('*.csv'):
        with open(csv_path) as file:
            df = pd.read_csv(file, names=['name', 'time'], usecols=[0, 1])
            df['time'] = pd.to_datetime(df['time'])

            try:
                activity_iter = df.itertuples()
                activity = next(activity_iter)
                next_activity = next(activity_iter)

                while True:
                    time = next_activity.time - activity.time

                    if time > max_time:
                        time = max_time

                    if activity.name not in activity_time:
                        activity_time.update({activity.name: time})
                    else:
                        activity_time[activity.name] += time

                    activity = next_activity
                    next_activity = next(activity_iter)
            except StopIteration:
                pass

    times = pd.DataFrame.from_dict(
        activity_time, orient='index', columns=['time'])

    times['percent'] = times['time'] / times['time'].sum()

    return times


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
    print(get_activity_times())
