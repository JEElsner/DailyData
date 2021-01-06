import sys
import argparse
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class Configuration:
    data_folder: Path = Path('./data')
    activity_folder: Path = Path('./activities')

    def __post_init__(self):
        self.activity_folder = self.data_folder.joinpath(
            self.activity_folder)


class Timelog:
    def __init__(self, time_management_cfg: Configuration):
        self.cfg = time_management_cfg

        if not self.cfg.activity_folder.exists():
            self.cfg.activity_folder.mkdir()

    def take_args(self, argv=sys.argv[1:]):
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
            if self.record_event(args.event, new=args.new):
                print('Recorded doing {activity} at {time}'.format(
                    activity=args.event,
                    time=datetime.now().strftime('%H:%M')))
            else:
                print(
                    'Unknown activity \'{0}\', did not record.\nUse [-n] if you want to add a new activity.'.format(args.event))
        elif args.list:
            print(self.get_activity_times()
                  .to_string(float_format=lambda s: '{:.2f}'.format(s*100)))

    def record_event(
        self,
        activity,
        time=datetime.now(),
        new=False
    ) -> bool:
        act_list_path = self.cfg.activity_folder.joinpath('list.txt')

        if not act_list_path.exists():
            open(act_list_path, mode='w').close()

        with open(act_list_path, mode='r+') as act_list:
            if not new and (activity + '\n') not in act_list:
                return False
            elif new:
                act_list.seek(0, 2)
                act_list.write(activity + '\n')

        with open(self.cfg.activity_folder.joinpath(time.strftime('%Y-%m') + '.csv'), mode='a') as file:
            file.write(','.join([activity, str(time), '\n']))

        return True

    def get_activity_times(self, max_time=timedelta(hours=12)) -> pd.DataFrame:
        activity_time = {}

        for csv_path in self.cfg.activity_folder.glob('*.csv'):
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
                            time = timedelta(0)

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
        times.sort_values(by=['time'], ascending=False, inplace=True)

        return times


def timelog_entry_point():
    from .. import config

    Timelog(config.time_management).take_args()


if __name__ == '__main__':
    print(Timelog(Configuration()).get_activity_times())
