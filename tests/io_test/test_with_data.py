import sqlite3
from unittest.mock import MagicMock
from DailyData.time_management.config import TimeManagementConfig
from datetime import datetime, timedelta
import pandas as pd
from DailyData.time_management import timelog
from DailyData.io.db import DatabaseWrapper
import unittest

from dateutil import tz


def reset_db(con: sqlite3.Connection):
    # Remove any new rows
    # TODO make this unnecessary by modifying DatabaseWrapper
    con.execute('DELETE FROM timelog WHERE id>3317')
    con.commit()


class TestWithData(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.db_wrapper = DatabaseWrapper(
            './tests/sample_data/sample.db')

        reset_db(cls.db_wrapper.db)

        cls.config = TimeManagementConfig()

    @classmethod
    def tearDownClass(cls) -> None:
        reset_db(cls.db_wrapper.db)

    def tearDown(self) -> None:
        reset_db(self.db_wrapper.db)

    def test_parse_timestamps(self):
        timelog.parse_timestamps(
            self.db_wrapper.get_timestamps(datetime.min, datetime.max))

    def test_custom_backdate(self):
        time = datetime.now(tz=tz.tzlocal()) - timedelta(seconds=1)

        timelog.take_args(self.config, self.db_wrapper,
                          argv=['doing', 'foo', '-t', '{:%H:%M}'.format(time)])

        timelog.take_args(self.config, self.db_wrapper, argv=['doing', 'foo'])
        timelog.parse_timestamps(
            self.db_wrapper.get_timestamps(datetime.min, datetime.max))


if __name__ == '__main__':
    unittest.main()
