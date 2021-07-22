from DailyData.time_management.recorded_activity import RecordedActivity
import abc
from datetime import datetime
from typing import List

from dateutil import tz

from pandas import DataFrame


class TimelogIO(abc.ABC):
    """
    Provides helper methods for complex file operations in timelog.

    This abstract base class is intended to be extended to implement timelog
    for various file systems, for example, a text file or a database. All
    timelog operations should be performable using only the methods in this
    class except for advanced or niche applications. This wrapper may or may
    not expose the underlying file objects to the client.

    Extending classes should handle all normal file activity and some
    non-normal file activity, such that the information stored on disk
    is reasonably guaranteed to be valid. Further, all extending classes are
    strongly encouraged to extend rather than override all methods, and invoke
    each method of this class to perform some input validation before
    performing additional steps.
    """

    def new_activity(self, activity: str, parent: str = None, is_alias: bool = None):
        """
        Saves a new activity so that new timestamps can be recorded with that
        activity.

        Args:
            activity: The name of the new activity as a string
            parent: Optional; the name of the parent activity that is a super
                set of the new activity. For example, the parent activity of
                'doing math homework' might be 'doing homework'
            is_alias: Optional; If a parent activity is specified, `True`
                indicates that this new activity is merely an alias for the
                parent activity, instead of a whole new activity. Activities
                recorded by the user with the alias should be saved internally
                with the parent activity that is not an alias.

        Returns:
            None

        Raises:
            ValueError: The parent activity does not exist
            ValueError: The new activity already exists
        """

        pass

    def record_time(self, activity: str, user: str, timestamp: datetime = datetime.now(tz=tz.tzlocal()), backdated=False) -> RecordedActivity:
        """
        Records the given activity at the given time.

        Args:
            activity: The name of the activity to record that is in the list
                of acceptable activities
            user: The user who is doing the activity
            timestamp: Optional; The datetime at which the new activity is
                recorded, with a valid timezone instance. By default the
                current system time in the current system time zone.
            backdated: Optional; Whether the recorded activity is 'backdated',
                `True` if the activity was recorded after the activity was
                completed, `False` if the activity was recorded at the time
                that it started.

        Returns:
            A RecordedActivity instance of the last activity the user was
            recorded doing chronologically if supported by the data storage
            system.

        Raises:
            ValueError: Activity not found
        """

        if timestamp.tzinfo is None:
            raise ValueError('timestamp must have an associated timezone!')

        return None

    def get_timestamps(self, earliest: datetime, latest: datetime) -> DataFrame:
        """
        Returns from file all of the recorded activities within a given range.

        Args:
            earliest: The time before which activities are not included in the
                results. This is a closed boundary, so a time recorded at
                `earliest` will be included in the results.
            latest: The time after which activities are not included in
                results. This is an open boundary, so a time recorded at the
                `latest` time will not be included.

        Returns:
            A pandas DataFrame with columns 'time' and 'activity'. The 'time'
            column lists the times as `datetimes` or `timestamps` or possibly
            `NumPy.datetime64[ns]` at which activities were recorded. The
            'activity' column lists the activities recorded at each time.
        """

        pass


class DebugTimelogIO(TimelogIO):
    """
    A simple extension of TimelogIO for debug purposes.

    This was originally made before I understood mocking, so it is possible
    to use what is built in to perform tests, however, mocking parts of this
    class would probably be easier. It might be useful to use this instead
    of a 'real' subclass of TimelogIO in order to avoid accidentally creating
    uneccessary files.
    """

    def __init__(self):
        self.clear()

    def clear(self):
        """
        Clear all of the debug information from the class, so that it can
        be called with a blank state.
        """

        self.args = list()
        self.kwargs = dict()
        self.last_called = None

        self.exception_to_raise = None
        self.return_value = None

        self.print_updates = False

    def __update(self, method, args, kwargs):
        """
        Helper method to update information when object methods are called.

        Args:
            method: The name of the method invoked
            args: The arguments invoked with the method
            kwargs: The keyword arguments used with the method

        Returns:
            The value specified in `return_value`

        Raises:
            Whatever error is set in `exception_to_raise`
        """

        self.args = args
        self.kwargs = kwargs
        self.last_called = method

        if self.print_updates:
            print('Call to {m}'.format(m=method))

        if self.exception_to_raise is not None:
            raise self.exception_to_raise

        return self.return_value

    # No docstrings here since we want to instead see the superclass
    # documentation
    def new_activity(self, *args, **kwargs):
        return self.__update('new_activity', args, kwargs)

    def record_time(self, *args, **kwargs):
        return self.__update('record_time', args, kwargs)

    def get_timestamps(self, *args, **kwargs):
        return self.__update('get_timestamps', args, kwargs)
