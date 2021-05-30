import sqlite3
from pathlib import Path
from importlib import resources
from datetime import datetime, timedelta, tzinfo
from sqlite3.dbapi2 import Row
from typing import List
from dateutil import tz
import numpy as np

import pandas as pd
from pandas.core import series

SCHEMA = 'schema.sql'


def apply_tz(row: pd.Series,
             offset_col_name='timezone_offset',
             tzname_col_name='timezone_name',
             time_col_name='time'
             ) -> datetime:
    if np.isfinite(row[offset_col_name]):
        tz_inst = tz.tzoffset(row[tzname_col_name],
                              timedelta(seconds=row[offset_col_name]))
        non_naive_datetime = tz_inst.fromutc(
            row[time_col_name].replace(tzinfo=tz_inst))
        return non_naive_datetime
    else:
        return row[time_col_name]


def dict_factory(cursor: sqlite3.Cursor, row):
    d = {}

    for i, col in enumerate(cursor.description):
        d[col[0]] = row[i]

    return d


class DatabaseWrapper:
    def __init__(self, folder_path: Path, in_memory=False):
        self.db = sqlite3.connect(folder_path.joinpath(
            'dailydata.db'), detect_types=sqlite3.PARSE_DECLTYPES)
        self.db.row_factory = sqlite3.Row

    def __init__(self):
        self.db = sqlite3.connect(
            ':memory:', detect_types=sqlite3.PARSE_DECLTYPES)
        self.db.row_factory = sqlite3.Row

    def __exit__(self, ex_type, ex_val, ex_tb):
        self.db.close()

        # Re-raise any exceptions
        if ex_val is not None:
            return False

    def new_user(self, user: str):
        self.db.execute('INSERT INTO user VALUES (:usr)', {'usr': user})
        self.db.commit()

    def new_activity(self, activity: str, parent: str = None, is_alias: bool = None):

        if parent is not None:
            if not self.db.execute('SELECT * FROM activity WHERE name=:parent', {'parent': parent}).fetchone():
                raise ValueError(
                    'Parent activity {} does not exist'.format(parent))
            elif not isinstance(parent, str):
                raise TypeError('parent must be a string')

        if is_alias is not None and parent is None:
            raise ValueError(
                'Activity cannot be an alias if there is no parent')
        elif is_alias is not None and not isinstance(is_alias, bool):
            raise TypeError('is_alias must be a boolean')

        self.db.execute('INSERT INTO activity VALUES (:act, :parent, :alias)',
                        {'act': activity,
                         'parent': parent,
                         'alias': is_alias})
        self.db.commit()

    def record_time(self, activity: str, user: str, timestamp: datetime):

        insert_cmd = '''INSERT INTO timelog (time, timezone_name, timezone_offset, activity, user)
        VALUES(:time, :tz_name, :tz_offset, :act, :user);
        '''

        activity_exists = self.db.execute(
            'SELECT * FROM activity WHERE name=:activity',
            {'activity': activity}).fetchone()

        if not activity_exists:
            raise ValueError(
                'Activity {} not found'.format(activity))
        elif activity_exists['parent'] is not None and activity_exists['alias']:
            activity = activity_exists['parent']

        self.db.execute(insert_cmd, {
            # Convert the time to UTC if there is timezone information
            'time': timestamp - (timestamp.tzinfo.utcoffset(timestamp) if timestamp.tzinfo else timedelta(0)),
            'tz_name': timestamp.tzinfo.tzname(timestamp) if timestamp.tzinfo else None,
            'tz_offset': timestamp.tzinfo.utcoffset(timestamp).total_seconds() if timestamp.tzinfo else None,
            'activity': activity,
            'act': activity,
            'user': user
        })

        self.db.commit()

    def get_timestamps(self, earliest: datetime, latest: datetime) -> pd.DataFrame:
        columns = ['time', 'timezone_offset', 'timezone_name', 'activity']

        cmd = '''SELECT :cols FROM timelog WHERE time >= :min AND time <= :max
        '''.replace(':cols', ', '.join(columns))

        old_row_factory = self.db.row_factory
        self.db.row_factory = None

        fetch = self.db.execute(cmd, {
            'min': earliest,
            'max': latest
        }).fetchall()

        self.db.row_factory = old_row_factory

        if len(fetch) == 0:
            return pd.DataFrame(columns=columns)

        frame = pd.DataFrame(fetch, columns=columns)
        frame['time'] = frame.apply(apply_tz, axis=1)
        return frame.drop(columns=['timezone_name', 'timezone_offset'])

    def reset(self) -> None:
        with resources.open_text(package='DailyData.io', resource=SCHEMA, encoding='utf8') as f:
            self.db.executescript(f.read())
