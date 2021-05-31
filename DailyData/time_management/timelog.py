import argparse
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
from DailyData import time_management
from DailyData.config import MasterConfig
from DailyData.io.db import DatabaseWrapper
from DailyData.io.timelog_io import DebugTimelogIO, TimelogIO
from dateutil import parser as time_parser
from dateutil import tz

from .config import TimeManagementConfig


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
    parser_doing.add_argument('-t', '--time', action='store')
    parser_doing.add_argument('-r', '--relative', action='store')

    parser.add_argument('-l', '--list',
                        action='store_true',
                        help='List the activities recorded')
    parser.add_argument('-n', '--num',
                        type=int, default=10)

    # get and parse the args passed to the method
    args = parser.parse_args(argv)

    # If the user wants to record a time
    if not args.list:
        if args.new:
            io.new_activity(args.event)

        if args.time:
            time = time_parser.parse(args.time)
        else:
            time = datetime.now()

            if args.relative:
                time -= parse_time_duration(args.relative)

        time = time.astimezone(tz.tzlocal())

        try:
            io.record_time(args.event, 'default_usr',
                           timestamp=time)
            print('Recorded doing {activity} at {time}'.format(
                activity=args.event,
                time=time.strftime('%H:%M')))
        except ValueError:
            print(
                'Unknown activity \'{0}\', did not record.\nUse [-n] if you want to add a new activity.'.format(args.event))
    elif args.list:
        # If the user wants to get a summary of how they spent their time
        print(parse_timestamps(io.get_timestamps(
            datetime.min, datetime.max))[:args.num])


def parse_timestamps(time_table: pd.DataFrame, max_time=timedelta(hours=12)) -> pd.DataFrame:
    time_table.sort_values(by=['time'], inplace=True)
    time_table['duration'] = -time_table['time'].diff(periods=-1)

    time_table.mask(time_table['duration'] > max_time, inplace=True)
    durations = time_table.groupby(['activity']).sum()

    durations['percent'] = durations['duration'] / durations['duration'].sum()

    durations['per_day'] = durations['percent'] * timedelta(days=1)
    durations['per_day'] = durations['per_day'].apply(
        lambda td: td - timedelta(microseconds=td.microseconds))
    durations.sort_values(by=['duration'], ascending=False, inplace=True)

    return durations


def parse_time_duration(txt: str) -> timedelta:
    curr_group = ''

    d = {}

    for c in txt:
        if c in ['d', 'h', 'm', 's']:
            if len(curr_group) == 0:
                raise ValueError('Invalid duration: {}'.format(txt))

            try:
                value = int(curr_group)
            except:
                raise ValueError('Invalid duration: {}'.format(curr_group))

            # pattern matching can't come soon enough...
            if c == 'd':
                d['days'] = value
            elif c == 'h':
                d['hours'] = value
            elif c == 'm':
                d['minutes'] = value
            elif c == 's':
                d['seconds'] = value

            curr_group = ''
        elif c.isdigit():
            curr_group += c

    return timedelta(**d)


def timelog_entry_point():
    from .. import master_config

    with master_config:
        take_args(master_config.time_management,
                  DatabaseWrapper(master_config.data_folder.joinpath('dailydata.db')))


if __name__ == '__main__':
    from .. import master_config

    parse_timestamps(master_config.time_management)
