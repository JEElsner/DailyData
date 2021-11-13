import os

import pytest
from DailyData.io.db import DatabaseWrapper
from DailyData.time_management.config import TimeManagementConfig

with open(os.path.join(os.path.dirname(__file__), 'real_data.sql'), 'rb') as f:
    _real_data = f.read().decode('utf8')


with open(os.path.join(os.path.dirname(__file__), 'test_data.sql'), 'rb') as f:
    _test_data = f.read().decode('utf8')


@pytest.fixture
def test_config(tmp_path):
    cfg = TimeManagementConfig()
    cfg.activity_folder = tmp_path

    return cfg


@pytest.fixture
def real_data_db():
    '''
    Create a DatabaseWrapper initialized with mock real-world data.

    Note: There are about 3000 rows in the timelog table, this may take
    some time to set-up for each unit test.
    '''

    wrapper = DatabaseWrapper()
    wrapper.db.executescript(_real_data)
    yield wrapper

    wrapper.db.close()


@pytest.fixture
def staged_db():
    '''
    Create a DatabaseWrapper initialized with easy-to-use data for testing.
    '''

    wrapper = DatabaseWrapper()
    wrapper.db.executescript(_test_data)
    yield wrapper

    wrapper.db.close()
