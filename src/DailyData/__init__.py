from dataclasses import dataclass
from datetime import time
import pkg_resources
from pathlib import Path
import json

from DailyData import time_management

from . import analyzer as analyzer_pkg
from . import tracker as tracker_pkg
from . import time_management as time_management_pkg

from .__main__ import take_args


@dataclass
class Configuration:
    configured: bool
    data_folder: Path
    analyzer: analyzer_pkg.Configuration
    time_management: time_management_pkg.Configuration
    tracker: tracker_pkg.Configuration

    def __post_init__(self):
        self.data_folder = Path(self.data_folder)

        self.analyzer = analyzer_pkg.Configuration(**self.analyzer)
        self.time_management = time_management_pkg.Configuration(
            data_folder=self.data_folder,
            **self.time_management
        )
        self.tracker = tracker_pkg.Configuration(
            data_folder=self.data_folder,
            **self.tracker)


config = Configuration(
    **json.loads(pkg_resources.resource_string(__name__, 'config.json')))
