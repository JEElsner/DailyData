from unittest.mock import MagicMock
from DailyData.time_management.config import TimeManagementConfig
from datetime import datetime, timedelta
import pandas as pd
from DailyData.time_management import timelog
from DailyData.io.db import DatabaseWrapper
import unittest

from dateutil import tz


class TestWithData(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.db_wrapper = DatabaseWrapper(
            './tests/sample_data/sample.db')

        # Remove any new rows
        # TODO make this unnecessary by modifying DatabaseWrapper
        cls.db_wrapper.db.execute('DELETE FROM timelog WHERE id>3317')
        cls.db_wrapper.db.commit()

        cls.config = TimeManagementConfig()

    def tearDown(self) -> None:
        # Remove any new rows
        # TODO make this unnecessary by modifying DatabaseWrapper
        self.db_wrapper.db.execute('DELETE FROM timelog WHERE id>3317')
        self.db_wrapper.db.commit()

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
