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

    def __init__(self):
        self.db = sqlite3.connect(':memory:')

    def __exit__(self, ex_type, ex_val, ex_tb):
        self.db.close()

        # Re-raise any exceptions
        if ex_val is not None:
            return False

    def new_user(self, user: str):
        self.db.execute('INSERT INTO user VALUES (:usr)', {'usr': user})
        self.db.commit()

    def new_activity(self, activity: str):
        self.db.execute('INSERT INTO activity VALUES (:act)',
                        {'act': activity})
        self.db.commit()

    def record_time(self, activity: str, user: str, timestamp: datetime = datetime.now()):

        insert_cmd = '''INSERT INTO timelog (time, utc_offset, activity, user)
        VALUES(:time, :offset, :act, :user);
        '''

        activity_exists = self.db.execute(
            'SELECT COUNT(*) FROM activity WHERE name = :activity',
            {'activity': activity}).fetchone()

        if activity_exists[0] < 1:
            raise ValueError(
                'Activity {} not found'.format(activity))

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
