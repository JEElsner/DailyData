import sqlite3
from pathlib import Path
from importlib import resources
from datetime import datetime
from sqlite3.dbapi2 import Row
from typing import List

SCHEMA = 'schema.sql'


class DatabaseWrapper:
    def __init__(self, folder_path: Path, in_memory=False):
        self.db = sqlite3.connect(folder_path.joinpath('dailydata.db'))
        self.db.row_factory = sqlite3.Row

    def __init__(self):
        self.db = sqlite3.connect(':memory:')
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

    def record_time(self, activity: str, user: str, timestamp: datetime = datetime.now()):

        insert_cmd = '''INSERT INTO timelog (time, utc_offset, activity, user)
        VALUES(:time, :offset, :act, :user);
        '''

        activity_exists = self.db.execute(
            'SELECT * FROM activity WHERE name=:activity',
            {'activity': activity}).fetchone()

        if not activity_exists[0]:
            raise ValueError(
                'Activity {} not found'.format(activity))
        elif activity_exists['parent'] is not None and activity_exists['alias']:
            activity = activity_exists['parent']

        self.db.execute(insert_cmd, {
            'time': timestamp.timestamp(),
            'offset': timestamp.utcoffset().total_seconds() if timestamp.utcoffset() is not None else 0,            'activity': activity,
            'act': activity,
            'user': user
        })

        self.db.commit()

    def get_timestamps(self, earliest: datetime, latest: datetime) -> List[Row]:
        cmd = '''SELECT * FROM activity WHERE time >= :min AND time <= :max
        '''

        return self.db.execute(cmd, {'min': earliest.timestamp(), 'max': latest.time()}).fetchall()

    def reset(self) -> None:
        with resources.open_text(package='DailyData.db', resource=SCHEMA, encoding='utf8') as f:
            self.db.executescript(f.read())
