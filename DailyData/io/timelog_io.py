import abc
from datetime import datetime
from typing import List


class TimelogIO(abc.ABC):
    def new_activity(self, activity: str, parent: str = None, is_alias: bool = None):
        pass

    def record_time(self, activity: str, user: str, timestamp: datetime = datetime.now(), backdated=False):
        pass

    def get_timestamps(self, earliest: datetime, latest: datetime) -> List:
        pass


class DebugTimelogIO(TimelogIO):
    def __init__(self):
        self.clear()

    def clear(self):
        self.args = list()
        self.kwargs = dict()
        self.last_called = None

        self.exception_to_raise = None
        self.return_value = None

        self.print_updates = False

    def __update(self, method, args, kwargs):
        self.args = args
        self.kwargs = kwargs
        self.last_called = method

        if self.print_updates:
            print('Call to {m}'.format(m=method))

        if self.exception_to_raise is not None:
            raise self.exception_to_raise

        return self.return_value

    def new_activity(self, *args, **kwargs):
        return self.__update('new_activity', args, kwargs)

    def record_time(self, *args, **kwargs):
        return self.__update('record_time', args, kwargs)

    def get_timestamps(self, *args, **kwargs):
        return self.__update('get_timestamps', args, kwargs)
