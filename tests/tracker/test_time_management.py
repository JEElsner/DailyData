from datetime import date, datetime, timedelta
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from DailyData.io.timelog_io import DebugTimelogIO
from DailyData.time_management import timelog
from DailyData.time_management.config import TimeManagementConfig


class TestTimeManagement(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.io_debug = DebugTimelogIO()

        cls.config = TimeManagementConfig()

    def setUp(self) -> None:
        self.io_debug.clear()

    @patch('builtins.print')
    @patch('DailyData.time_management.timelog.datetime')
    def test_record_time(self, dtm, prnt):
        now_value = datetime.now()
        dtm.now = MagicMock(return_value=now_value)

        timelog.take_args(self.config, self.io_debug, argv=['doing', 'foo'])

        dtm.now.assert_called()
        prnt.assert_called_with('Recorded doing foo at {}'.format(
                                now_value.strftime('%H:%M')))

        self.assertEqual('record_time', self.io_debug.last_called)
        self.assertEqual('foo', self.io_debug.args[0])

    @patch('builtins.print')
    def test_record_new_activity(self, prnt):
        self.io_debug.new_activity = MagicMock()

        timelog.take_args(self.config, self.io_debug,
                          argv=['doing', 'bar', '--new'])

        self.io_debug.new_activity.assert_called_with('bar')

    def test_parse_timestamps(self):
        from DailyData.io.text import TextIO

        txt_reader = TextIO(Path('./tests/data/activities/'))
        data = txt_reader.get_timestamps(pd.Timestamp.min, pd.Timestamp.max)

        timelog.parse_timestamps(data)

    def test_parse_str_durations(self):
        tests = {'10h3m': timedelta(hours=10, minutes=3),
                 '1m3s': timedelta(minutes=1, seconds=3),
                 '0d0h0s': timedelta(0),
                 '6d3m2s': timedelta(days=6, minutes=3, seconds=2),
                 '5s999d': timedelta(days=999, seconds=5)}

        for key, value in tests.items():
            with self.subTest(key):
                self.assertEqual(value, timelog.parse_time_duration(key))


if __name__ == '__main__':
    unittest.main()
