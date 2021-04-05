from dataclasses import dataclass, field
from pathlib import Path

from datetime import datetime, timedelta


@dataclass
class TimeManagementConfig:
    activity_folder: Path = Path('./data/activities')
    list_begin_time: datetime = datetime.min
    list_duration: timedelta = timedelta(days=36500)

    def __post_init__(self):
        self.activity_folder = Path(
            self.activity_folder)

        if isinstance(self.list_begin_time, str):
            self.list_begin_time = datetime.fromisoformat(self.list_begin_time)

        if isinstance(self.list_duration, float):
            self.list_duration = timedelta(seconds=self.list_duration)
