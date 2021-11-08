import sqlite3
from unittest.mock import MagicMock
from datetime import datetime, timedelta
import pandas as pd
from DailyData.time_management import timelog
from DailyData.io.db import DatabaseWrapper

import pytest

from dateutil import tz


def test_parse_timestamps(real_data_db):
    timelog.parse_timestamps(
        real_data_db.get_timestamps(datetime.min, datetime.max))


def test_custom_backdate(test_config, real_data_db):
    time = datetime.now(tz=tz.tzlocal()) - timedelta(seconds=1)

    timelog.take_args(test_config, real_data_db,
                      argv=['doing', 'foo', '-t', '{:%H:%M}'.format(time)])

    timelog.take_args(test_config, real_data_db, argv=['doing', 'foo'])
    timelog.parse_timestamps(
        real_data_db.get_timestamps(datetime.min, datetime.max))


if __name__ == '__main__':
    unittest.main()
