from dataclasses import dataclass
from pathlib import Path


@dataclass
class Configuration:
    data_folder: Path = Path('./data')
    activity_folder: Path = Path('./activities')

    def __post_init__(self):
        self.activity_folder = self.data_folder.joinpath(
            self.activity_folder)
