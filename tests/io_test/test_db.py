import sqlite3
import unittest
from datetime import datetime, timedelta, tzinfo
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import dateutil
import numpy as np
import pandas as pd
from DailyData.io import DatabaseWrapper, timelog_io
from dateutil import tz


class DBTests(unittest.TestCase):

    def setUp(self) -> None:
        self.db_wrapper = DatabaseWrapper()

        self.db_wrapper.new_activity('foo')
        self.db_wrapper.new_activity('bar')
        self.db_wrapper.new_activity('bash')

    def test_add_user(self):
        self.db_wrapper.new_user('gary')

    def test_add_duplicate_user(self):
        self.db_wrapper.new_user('howard')

        with self.assertRaises(sqlite3.IntegrityError):
            self.db_wrapper.new_user('howard')

    def test_add_activity(self):
        self.db_wrapper.new_activity('detonate_high_yield_nuclear_weapon')

    def test_add_child_activity(self):
        self.db_wrapper.new_activity('social studies')

        self.db_wrapper.new_activity('history', parent='social studies')

    def test_add_alias(self):
        self.db_wrapper.new_activity('history')

        self.db_wrapper.new_activity('hist', parent='history', is_alias=True)

    def test_add_child_with_no_parent(self):
        with self.assertRaises(ValueError):
            self.db_wrapper.new_activity('go_to_orphanage', parent='test')

    def test_add_duplicate_activity(self):
        self.db_wrapper.new_activity('hug_red_panda')

        with self.assertRaises(sqlite3.IntegrityError):
            # TODO make this a ValueError in line with the spec for
            # TimelogIO
            self.db_wrapper.new_activity('hug_red_panda')

    def test_add_timestamp(self):
        act = 'set_phasors_to_stun'
        user = 'spock'

        self.db_wrapper.new_user(user)
        self.db_wrapper.new_activity(act)

        time = datetime.utcnow().astimezone(tz.UTC)

        self.db_wrapper.record_time(act, user, time)

        record = self.db_wrapper.db.execute('SELECT * FROM timelog').fetchone()

        self.assertEqual(1, self.db_wrapper.db.execute(
            'SELECT COUNT(*) FROM timelog').fetchone()[0])
        self.assertEqual(act, record['activity'])
        self.assertEqual(time.replace(tzinfo=None), record['time'])
        self.assertEqual(time.tzinfo.utcoffset(
            time).total_seconds(), record['timezone_offset'])
        self.assertEqual(False, record['backdated'])

    def test_add_aliased_timestamp(self):
        self.db_wrapper.new_activity('f', parent='foo', is_alias=True)

        self.db_wrapper.new_user('bar')

        self.db_wrapper.record_time('f', 'bar', datetime.now(tz=tz.tzlocal()))

        self.assertEqual('foo', self.db_wrapper.db.execute(
            'SELECT activity FROM timelog').fetchone()[0])

    def test_preserve_timezone(self):

        self.db_wrapper.new_user('bar')

        test_date = datetime.now(tz=tz.tzlocal())
        self.db_wrapper.record_time('foo', 'bar', test_date)

        row = self.db_wrapper.db.execute('SELECT * FROM timelog').fetchone()

        tz_inst = tz.tzoffset(row['timezone_name'], row['timezone_offset'])
        fetched_date = row['time'].astimezone(tz_inst)

        self.assertEqual(test_date.replace(tzinfo=None),
                         tz_inst.fromutc(fetched_date).replace(tzinfo=None))
        self.assertEqual(test_date.tzinfo.utcoffset(
            test_date), tz_inst.utcoffset(fetched_date))
        self.assertEqual(test_date.tzinfo.tzname(
            test_date), tz_inst.tzname(fetched_date))

        # Make sure I got the UTC conversion right
        self.assertEqual(datetime.now().hour,
                         tz_inst.fromutc(fetched_date).hour)

    def test_fail_on_no_timezone(self):
        with self.assertRaisesRegex(ValueError, 'timestamp must have an associated timezone!'):
            self.db_wrapper.record_time('foo', None, datetime.now())

    def test_update_activity(self):
        # Test updating the activity last recorded
        self.db_wrapper.record_time(
            'foo', 'default', datetime.now(tz=tz.tzlocal()))
        self.db_wrapper.update_last_record('bar')

        last_act_name = self.db_wrapper.db.execute(
            'SELECT * FROM timelog').fetchone()['activity']
        row_count = self.db_wrapper.db.execute(
            'SELECT COUNT(*) FROM timelog').fetchone()[0]

        self.assertEqual('bar', last_act_name)
        self.assertEqual(1, row_count)

    def test_backdate(self):
        time = datetime.now(tz=tz.tzlocal())

        self.db_wrapper.record_time('foo', None, time, backdated=True)

        self.assertEqual(True, self.db_wrapper.db.execute(
            'SELECT backdated FROM timelog').fetchone()[0])

    def test_try_reset_non_empty_db(self):
        self.db_wrapper.record_time('foo', None, datetime.now(tz=tz.tzlocal()))

        with self.assertRaises(RuntimeError):
            self.db_wrapper.reset()

    def tearDown(self) -> None:
        self.db_wrapper.db.close()


if __name__ == '__main__':
    unittest.main(exit=False)
