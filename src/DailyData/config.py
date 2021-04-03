from dataclasses import dataclass
from pathlib import Path

from . import analyzer as analyzer_pkg
from . import time_management as time_management_pkg
from . import tracker as tracker_pkg


@dataclass
class Configuration:
    configured: bool = False
    data_folder: Path = './data'
    analyzer: analyzer_pkg.Configuration = analyzer_pkg.Configuration()
    time_management: time_management_pkg.Configuration = time_management_pkg.Configuration()
    tracker: tracker_pkg.Configuration = tracker_pkg.Configuration()

    def __post_init__(self):
        self.data_folder = Path(self.data_folder)

        if not isinstance(self.analyzer, analyzer_pkg.Configuration):
            self.analyzer = analyzer_pkg.Configuration(**self.analyzer)

        if not isinstance(self.time_management, time_management_pkg.Configuration):
            self.time_management = time_management_pkg.Configuration(
                data_folder=self.data_folder,
                **self.time_management
            )

        if not isinstance(self.tracker, tracker_pkg.Configuration):
            self.tracker = tracker_pkg.Configuration(
                data_folder=self.data_folder,
                **self.tracker)
