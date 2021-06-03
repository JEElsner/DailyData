from DailyData.io.timelog_io import TimelogIO
import sqlite3
from pathlib import Path
from importlib import resources
from datetime import datetime, timedelta, tzinfo
from sqlite3.dbapi2 import Row
from typing import Any, Dict, List
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
        return apply_tz_single(row, offset_col_name, tzname_col_name, time_col_name)
    else:
        return row[time_col_name].tz_localize(tz.tzlocal())


def apply_tz_single(row,
                    offset_col_name='timezone_offset',
                    tzname_col_name='timezone_name',
                    time_col_name='time'
                    ):
    tz_inst = tz.tzoffset(row[tzname_col_name],
                          timedelta(seconds=row[offset_col_name]))
    non_naive_datetime = tz_inst.fromutc(
        row[time_col_name].replace(tzinfo=tz_inst))
    return non_naive_datetime


def dict_factory(cursor: sqlite3.Cursor, row):
    d = {}

    for i, col in enumerate(cursor.description):
        d[col[0]] = row[i]

    return d


class DatabaseWrapper(TimelogIO):
    def __init__(self, db_path: Path = None):

        if not db_path:
            db_path = ':memory:'

        self.db = sqlite3.connect(
            db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        self.db.row_factory = sqlite3.Row

        n_tables = self.db.execute(
            'SELECT COUNT(name) FROM sqlite_master WHERE type="table" AND name NOT LIKE "sqlite_%";').fetchone()[0]

        if n_tables == 0:
            self.reset()

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

    def get_activity_or_parent(self, activity):
        activity_exists = self.db.execute(
            'SELECT * FROM activity WHERE name=:activity',
            {'activity': activity}).fetchone()

        if not activity_exists:
            return None

        if activity_exists['parent'] is not None and activity_exists['alias']:
            return activity_exists['parent']
        else:
            return activity

    def record_time(self, activity: str, user: str, timestamp: datetime, backdated=False):
        super().record_time(activity, user, timestamp, backdated)

        insert_cmd = '''INSERT INTO timelog (time, timezone_name, timezone_offset, activity, user, backdated)
        VALUES(:time, :tz_name, :tz_offset, :act, :user, :backdated);
        '''

        # Make sure any values given with pandas datatypes can be recorded
        if isinstance(timestamp, pd.Timestamp):
            timestamp = timestamp.to_pydatetime()

        old_act = activity
        activity = self.get_activity_or_parent(activity)

        if activity is None:
            raise ValueError(
                'Activity {} not found'.format(old_act))

        self.db.execute(insert_cmd, {
            # Convert the time to UTC if there is timezone information
            'time': timestamp - (timestamp.tzinfo.utcoffset(timestamp) if timestamp.tzinfo else timedelta(0)),
            'tz_name': timestamp.tzinfo.tzname(timestamp) if timestamp.tzinfo else None,
            'tz_offset': timestamp.tzinfo.utcoffset(timestamp).total_seconds() if timestamp.tzinfo else None,
            'activity': activity,
            'act': activity,
            'user': user,
            'backdated': backdated
        })

        self.db.commit()

    def get_timestamps(self, earliest: datetime, latest: datetime) -> pd.DataFrame:
        columns = ['time', 'timezone_offset',
                   'timezone_name', 'activity']

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

    def get_last_record(self, as_entered=False) -> Dict[str, Any]:
        if as_entered:
            cmd = '''SELECT *
            FROM
                timelog
            ORDER BY
                id DESC
            LIMIT 1;
            '''
        else:
            cmd = '''SELECT *
            FROM
                timelog
            ORDER BY
                time DESC
            LIMIT 1;
            '''

        record: Row = self.db.execute(cmd).fetchone()

        if record is None:
            return None

        dict_rec = {key: record[key] for key in record.keys()}

        if dict_rec['timezone_offset'] is not None:
            dict_rec['time'] = apply_tz_single(dict_rec)

        del dict_rec['timezone_name'], dict_rec['timezone_offset']

        return dict_rec

    def update_last_record(self, activity: str, search_by_id=False):
        old_act = activity
        activity = self.get_activity_or_parent(activity)

        if activity is None:
            raise ValueError(
                'Activity {} not found'.format(old_act))

        if search_by_id:
            cmd = '''SELECT *
            FROM
                timelog
            ORDER BY
                id DESC
            LIMIT 1;
            '''
        else:
            cmd = '''SELECT *
            FROM
                timelog
            ORDER BY
                time DESC
            LIMIT 1;
            '''

        last_id = self.db.execute(cmd).fetchone()['id']
        self.db.execute('UPDATE timelog SET activity=:act, backdated=True WHERE id=:id', {
            'id': last_id,
            'act': activity
        })
        self.db.commit()

    def reset(self, force=False) -> None:
        try:
            row_count = self.db.execute(
                'SELECT COUNT(*) FROM timelog').fetchone()[0]

            if row_count > 0 and not force:
                raise RuntimeError(
                    'Attempted to reset non-empty database. Set force=True, cross your heart, and hope to die to really make it go away.')
        except sqlite3.OperationalError as err:
            pass

        with resources.open_text(package='DailyData.io', resource=SCHEMA, encoding='utf8') as f:
            self.db.executescript(f.read())


def __main(path: Path):
    from DailyData.io.text import TextIO

    text_io = TextIO(path.joinpath('./activities'))
    db_io = DatabaseWrapper(path.joinpath('dailydata.db'))

    with open(path.joinpath('./activities/list.txt'), mode='r') as list_file:
        for line in list_file:
            db_io.new_activity(line.strip())

    for row in text_io.get_timestamps(pd.Timestamp.min, pd.Timestamp.max).iterrows():
        db_io.record_time(row[1]['activity'], None,
                          row[1]['time'].tz_localize(tz.tzlocal()), backdated=None)

    n_converted = db_io.db.execute(
        'SELECT COUNT(*) FROM timelog').fetchone()[0]
    print('{} timelogs converted'.format(n_converted))

    last_converted = db_io.db.execute(
        'SELECT activity, time FROM timelog ORDER BY time DESC').fetchone()
    print('Last converted log: {} at {}'.format(
        last_converted[0], last_converted[1]))


if __name__ == '__main__':
    __main(Path('.'))
