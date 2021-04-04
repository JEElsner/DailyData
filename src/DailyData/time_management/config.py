from dataclasses import dataclass
from pathlib import Path


@dataclass
class TimeManagementConfig:
    activity_folder: Path = Path('./data/activities')

    def __post_init__(self):
        self.activity_folder = Path(
            self.activity_folder)
