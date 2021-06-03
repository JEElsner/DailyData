from datetime import datetime
import pandas as pd
from DailyData.time_management import timelog
from DailyData.io.db import DatabaseWrapper
import unittest


class TestWithData(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        TestWithData.db_wrapper = DatabaseWrapper('./tests/sample.db')

    def test_parse_timestamps(self):
        timelog.parse_timestamps(
            self.db_wrapper.get_timestamps(datetime.min, datetime.max))


if __name__ == '__main__':
    unittest.main()
