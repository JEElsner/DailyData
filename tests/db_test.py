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

        print(self.db_wrapper.db.execute('SELECT * FROM timelog').fetchall())

    def tearDown(self) -> None:
        self.db_wrapper.db.close()


if __name__ == '__main__':
    unittest.main()
