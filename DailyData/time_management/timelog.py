from DailyData.io.db import DatabaseWrapper
from DailyData.io.timelog_io import DebugTimelogIO, TimelogIO
import sys
import argparse
from datetime import datetime, timedelta

import pandas as pd

from DailyData import time_management
from DailyData.config import MasterConfig

from .config import TimeManagementConfig

from pathlib import Path

from dateutil import tz


def take_args(time_manangement_cfg: TimeManagementConfig, io: TimelogIO, argv=sys.argv[1:]):
    # Create the argparser for the timelog command
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
    parser.add_argument('-n',
                        type=int, default=10)

    # get and parse the args passed to the method
    args = parser.parse_args(argv)

    # If the user wants to record a time
    if not args.list:
        if args.new:
            io.new_activity(args.event)

        try:
            io.record_time(args.event, 'default_usr',
                           timestamp=datetime.utcnow().astimezone(tz.UTC))
            print('Recorded doing {activity} at {time}'.format(
                activity=args.event,
                time=datetime.now().strftime('%H:%M')))
        except ValueError:
            print(
                'Unknown activity \'{0}\', did not record.\nUse [-n] if you want to add a new activity.'.format(args.event))
    elif args.list:
        # If the user wants to get a summary of how they spent their time
        print(parse_timestamps(io.get_timestamps(
            datetime.min, datetime.max))[:args.n])


def parse_timestamps(time_table: pd.DataFrame, max_time=timedelta(hours=12)) -> pd.DataFrame:
    time_table['duration'] = -time_table['time'].diff(periods=-1)

    time_table.mask(time_table['duration'] > max_time, inplace=True)
    durations = time_table.groupby(['activity']).sum()

    durations['percent'] = durations['duration'] / durations['duration'].sum()

    durations['per_day'] = durations['percent'] * timedelta(days=1)
    durations['per_day'] = durations['per_day'].apply(
        lambda td: td - timedelta(microseconds=td.microseconds))
    durations.sort_values(by=['duration'], ascending=False, inplace=True)

    return durations


def timelog_entry_point():
    from .. import master_config

    with master_config:
        take_args(master_config.time_management,
                  DatabaseWrapper(master_config.data_folder.joinpath('dailydata.db')))


if __name__ == '__main__':
    from .. import master_config

    parse_timestamps(master_config.time_management)
