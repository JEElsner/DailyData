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
    '''
    Parses timelog-related arguments.

    TODO Detailed description of commandline arguments.

    Args:
        `time_management_cfg` (`TimeManagementConfig`): The configuration object
            specifying constant parameters such as the folder for where to read
            and write file output.
        `io` (`TimelogIO`): The IO object that performs pre-defined file operations
            for the timelog
        `argv` (`List[str]`): The list of arguments to parse. By default, this
            is the arguments passed to the module when executed.
    '''

    # Create the argparser for the timelog command
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Add all the subcommands for the "timelog doing" command
    parser_doing = subparsers.add_parser('doing',
                                         help='Record an activity')
    parser_doing.add_argument('event', help='The event you are recording')
    parser_doing.add_argument('-n', '--new',
                              action='store_true',
                              help='Add a new activity to track')
    parser_doing.add_argument('-t', '--time', action='store')
    parser_doing.add_argument('-b', '--back', action='store')
    parser_doing.add_argument('-u', '--update', action='store_true')

    # Add all the subcommands for the "timelog --list" command
    # TODO: This needs to be better fleshed out. ideally, "list" would be it's
    # own subcommand, but also that may reach beyond the capabilities of argparse,
    # the module we're using
    parser.add_argument('-l', '--list',
                        action='store_true',
                        help='List the activities recorded')
    parser.add_argument('-n', '--num',
                        type=int, default=10)

    # get and parse the args passed to the method
    args = parser.parse_args(argv)

    # If the user wants to record a time
    if not args.list:
        # When the user is specifying that a new activity will be created
        if args.new:
            # Create the activity in the file system
            io.new_activity(args.event)

        if args.time:
            # Use the user-specified time if they have given one
            time = time_parser.parse(args.time)
        else:
            # Otherwise use the current time
            time = datetime.now()

            if args.back:
                # If the user has specified that the timestamp will be recorded
                # relative to the current time, subtract the offset
                time -= parse_time_duration(args.back)

        # Give the time the local timezone
        time = time.astimezone(tz.tzlocal())

        # Get and print the last activity if our data storage does that
        # TODO make this an interface, instead of just allowing DatabaseWrapper
        if isinstance(io, DatabaseWrapper):
            last = io.get_last_record()  # Get the last activity

            # Re-combine the timezone with the time
            if last is not None and last['time'].tzinfo == None:
                last['time'] = last['time'].replace(tzinfo=tz.tzlocal())
        else:
            last = None

        try:
            # If the user wants to change the last activity recorded, do that
            if args.update:
                # Only if the file system supports it
                # TODO make interface
                if isinstance(io, DatabaseWrapper):
                    io.update_last_record(args.event)
                    print('Updated last activity to doing', args.event)
                else:
                    print('Update not supported by data storage system')
            else:
                # Otherwise, record a new activity
                io.record_time(args.event, 'default_usr',
                               timestamp=time)
                print('Recorded doing {activity} at {time}'.format(
                    activity=args.event,
                    time=time.strftime('%H:%M')))
        except ValueError:
            # Print an error message when the activity to record is not one
            # pre-defined by the user
            print(
                'Unknown activity \'{0}\', did not record.\nUse [-n] if you want to add a new activity.'.format(args.event))

        # TODO move inside the try/catch block so that this isn't printed when
        # it fails to record an activity
        if last and not args.update:
            print('Finished doing {act} for {time}'.format(
                act=last['activity'],
                time=time - last['time']
            ))
    elif args.list:
        # If the user wants to get a summary of how they spent their time

        # Define the time range for the search query
        first = time_manangement_cfg.list_begin_time
        last = datetime.now()

        # Print a message to the user telling them the search time range
        print(
            'Between {:%Y-%m-%d} and {:%Y-%m-%d}, you have spent your time as follows:'.format(first, last))

        # Print a table of activities and how much time is spent for each
        print(parse_timestamps(io.get_timestamps(first, last))[:args.num])


def parse_timestamps(time_table: pd.DataFrame, max_time=timedelta(hours=12)) -> pd.DataFrame:
    time_table['utc_time'] = pd.to_datetime(time_table['time'], utc=True)

    time_table.sort_values(by=['utc_time'], inplace=True)
    time_table['duration'] = -time_table['utc_time'].diff(periods=-1)

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
