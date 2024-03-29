import unittest
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
from DailyData.io.db import DatabaseWrapper
from DailyData.io.timelog_io import DebugTimelogIO
from DailyData.time_management import timelog
from DailyData.time_management.config import TimeManagementConfig
from dateutil import tz
from dateutil import parser as date_parser


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
        self.io_debug = DebugTimelogIO()

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

    @patch('builtins.print')
    @patch('DailyData.time_management.timelog.datetime')
    def test_last_act_print(self, dtm: MagicMock, prnt: MagicMock):
        last = datetime.now(tz=tz.tzlocal())
        next = last + timedelta(minutes=10)

        dtm.now = MagicMock(return_value=next)

        db = DatabaseWrapper()
        db.new_activity('foo')
        db.new_activity('bar')

        db.record_time('foo', 'none', last)

        timelog.take_args(self.config, db, argv=['doing', 'bar'])

        prnt.assert_called_with('Finished doing foo for 0:10:00')

    @patch('builtins.print')
    @patch('DailyData.time_management.timelog.datetime')
    def test_last_act_print_with_tz(self, dtm, prnt: MagicMock):
        last = datetime.now().astimezone(tz.tzlocal())
        next = (last + timedelta(minutes=50)).astimezone(tz.tzlocal())

        dtm.now = MagicMock(return_value=next)

        db = DatabaseWrapper()
        db.new_activity('foo')
        db.new_activity('bar')

        db.record_time('foo', 'none', last)

        timelog.take_args(self.config, db, argv=['doing', 'bar'])

        prnt.assert_called_with('Finished doing foo for 0:50:00')

    @patch('builtins.print')
    @patch('DailyData.time_management.timelog.datetime')
    def test_last_act_multiple(self, dtm, prnt: MagicMock):
        first = datetime.now().astimezone(tz.tzlocal())
        mid = (first + timedelta(minutes=13))
        next = (mid + timedelta(minutes=7))

        dtm.now = MagicMock(return_value=next)

        db = DatabaseWrapper()
        db.new_activity('foo')
        db.new_activity('bar')
        db.new_activity('bash')

        db.record_time('foo', 'none', first)
        db.record_time('bar', 'none', mid)

        timelog.take_args(self.config, db, argv=['doing', 'bash'])

        prnt.assert_called_with('Finished doing bar for 0:07:00')

    @patch('builtins.print')
    def test_record_custom_time(self, print_hook):
        time = '10:59'

        self.io_debug.record_time = MagicMock()

        timelog.take_args(self.config, self.io_debug, argv=[
                          'doing', 'foo', '-t', time])

        # See take_args in timelog (approx. line 119) for why 1 microsecond is
        # necessary
        self.io_debug.record_time.assert_called_once_with('foo', 'default_usr', timestamp=datetime.now(
        ).replace(hour=10, minute=59, second=0, microsecond=1, tzinfo=tz.tzlocal()))


def test_last_act_before_most_recent(staged_db: DatabaseWrapper):
    """
    Make sure that if we record a time before another activity already
    in the timelog, that we don't get a negative duration from that
    activity to this new one, instead make sure that it finds the
    previous activity in time.
    """

    time = datetime(2021, 1, 1, 0, 30, 0, tzinfo=tz.UTC)

    last = staged_db.record_time('foo', 'user1', time)

    assert last is not None
    assert last.name == 'activity1'
    assert last.time == datetime(2021, 1, 1, 0, 0, 0, tzinfo=tz.UTC)
    assert last.duration == timedelta(minutes=30)


def test_show_summary(test_config, staged_db: DatabaseWrapper):
    timelog.take_args(test_config, staged_db, argv=['summary'])


if __name__ == '__main__':
    unittest.main()
