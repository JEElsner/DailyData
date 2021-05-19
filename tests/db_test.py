import datetime
import sqlite3
from DailyData.db import DatabaseWrapper
import unittest
from unittest.mock import MagicMock, Mock, patch
from pathlib import Path


class DBTests(unittest.TestCase):

    def setUp(self) -> None:
        self.db_wrapper = DatabaseWrapper()
        self.db_wrapper.reset()

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
            self.db_wrapper.new_activity('hug_red_panda')

    def test_add_timestamp(self):
        act = 'set_phasors_to_stun'
        user = 'spock'

        self.db_wrapper.new_user(user)
        self.db_wrapper.new_activity(act)

        self.db_wrapper.record_time(act, user)

        # print(self.db_wrapper.db.execute('SELECT * FROM timelog').fetchall())

    def test_add_aliased_timestamp(self):
        self.db_wrapper.new_activity('foo')
        self.db_wrapper.new_activity('f', parent='foo', is_alias=True)

        self.db_wrapper.new_user('bar')

        self.db_wrapper.record_time('f', 'bar')

        self.assertEqual('foo', self.db_wrapper.db.execute(
            'SELECT activity FROM timelog').fetchone()[0])

    def tearDown(self) -> None:
        self.db_wrapper.db.close()


if __name__ == '__main__':
    unittest.main()
