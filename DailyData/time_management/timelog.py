import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List

import pandas as pd
from DailyData import time_management
from DailyData.config import MasterConfig
from DailyData.io.db import DatabaseWrapper
from DailyData.io.timelog_io import DebugTimelogIO, TimelogIO
from dateutil import parser as time_parser
from dateutil import tz

from .config import TimeManagementConfig


def take_args(time_management_cfg: TimeManagementConfig, io: TimelogIO, argv=sys.argv[1:]):
    """
    Parses timelog-related arguments.

    There are two main commands for the timelog: `doing` and `--list`. `doing`
    is used to record when you (or the user) are doing an activity. `--list` is
    used to summarize some statistics for how you spend your time based on the
    activities you record using the `doing` command. The subcommands and
    options for each command are listed below:

    `doing [activity]`: Records the activity you specify after this keyword. By
        default, you must have pre-specified the activity as one that can be
        recorded. This is done to prevent the recording of typos. (See the
        argument `-n`)

        `-n`/`--new`: Specifies that this is a new activity to add to the list
            of possible activities to record, allowing you to record whatever
            activity you specify, and allowing you to record this activity
            again in the future without the use of this flag.

        `-t`/`--time [time]`: Specifies a time other than the current time at
            which to record the activity. It is suggested that you only use
            times between when the last activity was recorded and the current
            time, but it *might* work if you specify another time. In terms of
            formatting this time, `dateutil.parser` is used to parse the time,
            most standard time formats should be accepted, but refer to that
            module's documentation for details.

        `-b`/`--back [duration]`: Specifies a duration of offset from the
            current time. i.e. if it is 10:30, and you specify 20m, the
            activity will be recorded at 10:10. Acceptable units are `h` for
            hours, `m` for minutes, `s` for seconds, and `d` for days. Multiple
            units can be used at once, for example `20m3s`

        `-u`/`--update`: Instead of recording a new time, alter the activity
            that was last recorded with the new activity that was performed.

    `--list`: Prints a summary of how you have spent your time, including the
    total time spent doing each activity, what percentage time you spend doing
    each activity, and how much time per day you spend on average doing each
    activity.

        `-n`/`--num`: The number of activities to display statistics for. By
            default, the 10 activities you spend the most time doing are listed.

    Args:
        `time_management_cfg` (`TimeManagementConfig`): The configuration
            object specifying constant parameters such as the folder for where
            to read and write file output.
        `io` (`TimelogIO`): The IO object that performs pre-defined file
            operations for the timelog
        `argv` (`List[str]`): The list of arguments to parse. By default, this
            is the arguments passed to the module when executed.
    """

    # Create the argparser for the timelog command
    parser = argparse.ArgumentParser(usage=take_args.__doc__)
    subparsers = parser.add_subparsers(dest='subparser')

    parser.set_defaults(time_management_cfg=time_management_cfg,
                        io=io)

    # TODO adapt help message specifically for the 'timelog' command
    # remove the stuff about the function

    # Add all the subcommands for the "timelog doing" command
    parser_doing = subparsers.add_parser('doing',
                                         help='Record an activity')
    parser_doing.set_defaults(func=record)
    parser_doing.add_argument('event', help='The event you are recording')
    parser_doing.add_argument('-n', '--new',
                              action='store_true',
                              help='Add a new activity to track')
    parser_doing.add_argument('-t', '--time', action='store')
    parser_doing.add_argument('-b', '--back', action='store')
    parser_doing.add_argument('-u', '--update', action='store_true')

    parser_summary = subparsers.add_parser(
        'summary', help='Summarizes how you spend your time')
    parser_summary.set_defaults(func=summary)

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

    # Temporary patch to keep --list option working. Don't want to
    # phase this out yet
    if args.list:
        summary(**vars(args))

    # call the function associated with the invoked subparser and pass the
    # given arguments
    args.func(**vars(args))


def record(io, **kwargs: List[str]):
    # When the user is specifying that a new activity will be created
    if kwargs.get('new'):
        # Create the activity in the file system
        io.new_activity(kwargs['event'])

    if kwargs.get('time'):
        # Use the user-specified time if they have given one
        #
        # Yes, the 1 microsecond is necessary so that the time is entered
        # into the database correctly, so that it is then parsed correctly
        # when read back by sqlite3. This is why people hate programming.
        # It took me over an hour to figure this out. （｀Δ´）！
        time = time_parser.parse(kwargs['time']).replace(
            second=0, microsecond=1)
    else:
        # Otherwise use the current time
        time = datetime.now()

        if kwargs.get('back'):
            # If the user has specified that the timestamp will be recorded
            # relative to the current time, subtract the offset
            time -= parse_time_duration(kwargs['back'])

    # Give the time the local timezone
    time = time.astimezone(tz.tzlocal())

    # Create a variable to store the last activity if we can
    last = None

    try:
        # If the user wants to change the last activity recorded, do that
        if kwargs.get('update'):
            # Only if the file system supports it
            # TODO make interface
            if isinstance(io, DatabaseWrapper):
                io.update_last_record(kwargs['event'])
                print('Updated last activity to doing', kwargs['event'])
            else:
                print('Update not supported by data storage system')
        else:
            # Otherwise, record a new activity
            last = io.record_time(kwargs['event'], 'default_usr',
                                  timestamp=time)
            print('Recorded doing {activity} at {time}'.format(
                activity=kwargs['event'],
                time=time.strftime('%H:%M')))
    except ValueError:
        # Print an error message when the activity to record is not one
        # pre-defined by the user
        print(
            'Unknown activity \'{0}\', did not record.\nUse [-n] if you want to add a new activity.'.format(kwargs['event']))

    # TODO move inside the try/catch block so that this isn't printed when
    # it fails to record an activity
    if last and not kwargs.get('update'):
        print('Finished doing {act} for {time}'.format(
            act=last.name,
            time=last.duration
        ))


def summary(time_management_cfg: TimeManagementConfig, io: TimelogIO, **kwargs: List[str]):
    # Define the time range for the search query
    first = time_management_cfg.list_begin_time
    last = datetime.now()

    # Print a message to the user telling them the search time range
    print(
        'Between {:%Y-%m-%d} and {:%Y-%m-%d}, you have spent your time as follows:'.format(first, last))

    # Print a table of activities and how much time is spent for each
    print(parse_timestamps(io.get_timestamps(first, last))[:kwargs['num']])


def parse_timestamps(time_table: pd.DataFrame, max_time=timedelta(hours=12)) -> pd.DataFrame:
    """
    Parses a Pandas DataFrame containing activities and when they started to
    generate statistics about how much time was spent doing each activity
    over the duration of the recorded times.

    The time spent doing a single activity at a single time is calculated by
    subtracting the start time of the activity from the start time of the
    subsequent activity. These durations are then summed to get the total time
    for each activity over the recorded times. The proportion of time spent
    per activity versus all time spent and the amount of time spent per day on
    average for each activity is also calculated.

    Args:
        `time_table`: A pandas DataFrame containing a column of `datetime`s or
            `Timestamps`s with the name `time with an index of strings with
            the activity corresponding to each recorded time, the index's name
            is `activity`.

        `max_time`: Optional; Specifies the maximum duration for an activity,
            activities with durations exceeding `max_time` are ignored for the
            calculations.

    Returns:
        A pandas DataFrame with columns `duration`, `percent`, and
        `per_day`. The index is `activity`, and lists each recorded activity
        once. `duration` has type `timedelta`, and represents the total time
        spent doing each activity. `percent` has type `float`, and represents
        the portion of total time doing each activity. `per_day` has type
        `timedelta` and represents how much time on average is spent on the
        activity per day.
    """

    # Get the UTC time of each timestamp
    time_table['utc_time'] = pd.to_datetime(time_table['time'], utc=True)

    # Sort the values by their time, so that the differences are calculated
    # in the right order
    time_table.sort_values(by=['utc_time'], inplace=True)

    # Calculate the duration of each activity
    #
    # This works by using the pandas difference function to find the difference
    # function between the current record in the next, i.e. current - next,
    # which is a negative duration, but it associates the difference with the
    # current activity. All we have to do is negate this value to get the
    # time spent for each activity starting at the listed time
    time_table['duration'] = -time_table['utc_time'].diff(periods=-1)

    # Ignore activities with duration greater than max_time
    time_table.mask(time_table['duration'] > max_time, inplace=True)

    # Create a table of total durations for each activity
    durations = time_table.groupby(['activity']).sum()

    # Calculate the percentage of time spent on each activity
    durations['percent'] = durations['duration'] / durations['duration'].sum()

    # Calculate the average time spent per day on each activity
    durations['per_day'] = durations['percent'] * timedelta(days=1)

    # Remove the microseconds on the activities, because they add clutter to
    # the screen.
    # TODO I don't think this is working right now
    durations['per_day'] = durations['per_day'].apply(
        lambda td: td - timedelta(microseconds=td.microseconds))

    # Sort so that the activities with the greatest time spent come first
    durations.sort_values(by=['duration'], ascending=False, inplace=True)

    return durations


def parse_time_duration(txt: str) -> timedelta:
    """
    Parses a string representing a length of time and returns the corresponding
    timedelta.

    Args:
        txt: A string containing a set of numbers representing durations, each
            proceeded by a unit of time. For example, a duration could be `20`
            and the unit of time could be `m` for minutes, which combine to
            form the token `20m`. Many tokens can be in one string, for
            example, `3h20m42s`. Valid units of time are:
                `d` for days,
                `h` for hours,
                `m` for minutes,
                `s` for seconds

    Returns:
        A `timedelta` object for the duration represented by the passed string.
        For example, `parse_time_duration('21m5s')` returns
        `timedelta(minutes=21, seconds=5)`
    """

    # The current number being captured
    curr_group = ''

    # dictionary for days, hours, minutes, and seconds
    d = {}

    for c in txt:
        # If the character is a time unit
        if c in ['d', 'h', 'm', 's']:
            # Raise an error if we have no number for the units
            # e.g. the passed string was `m`
            if len(curr_group) == 0:
                raise ValueError('Invalid duration: {}'.format(txt))

            try:
                value = int(curr_group)
            except:
                raise ValueError('Invalid duration: {}'.format(curr_group))

            # Assign the value to a unit of time
            # pattern matching can't come soon enough...
            # TODO what if something like '20m20m' is given
            if c == 'd':
                d['days'] = value
            elif c == 'h':
                d['hours'] = value
            elif c == 'm':
                d['minutes'] = value
            elif c == 's':
                d['seconds'] = value

            # Reset the number being recorded
            curr_group = ''
        elif c.isdigit():
            # If the character isn't a time unit, and it's a digit, concatenate
            # it to the number being built
            # Ignore all other characters
            curr_group += c

    # Build the timedelta from the dictionary and return it
    return timedelta(**d)


def timelog_entry_point():
    """
    The entry point used for the `timelog` command. This method is referenced
    in `setup.py` so that when the package is built, the `timelog` script is
    built and it links to this method.
    """
    from .. import master_config

    # Use the master_config file so that when we are finished, any changes
    # to the configuration are saved.
    #
    # Doing this with a global variable is probably all kinds of bad, but
    # idk, it works for now ¯\_(ツ)_/¯
    with master_config:
        # TODO use a context manager for DatabaseWrapper so the db gets closed
        # properly
        take_args(master_config.time_management,
                  DatabaseWrapper(master_config.data_folder.joinpath('dailydata.db')))


if __name__ == '__main__':
    from .. import master_config

    parse_timestamps(master_config.time_management)
