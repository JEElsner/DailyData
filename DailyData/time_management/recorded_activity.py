from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass(frozen=True)
class RecordedActivity:
    """
    An immutable instance of an activity that was performed by the user.

    Attributes: name: The string name of the activity that was performed.

        time: The datetime timestamp of when the activity was started.

        duration: The timedelta duration of time during which the activity
            occurred.

        user: The string name of the user that performed the activity.

        backdated: True if the listed start of the activity was not recorded
            until later, False otherwise.

        id (optional): The integer identification number of the activity
            record. This is present in some data storage systems for activities
            (e.g. SQLite database), so it is provided here optionally.
    """

    name: str
    time: datetime
    duration: timedelta
    user: str
    backdated: bool
    id: int = field(default=-1, compare=False)
