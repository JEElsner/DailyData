from dataclasses import dataclass
from datetime import time
from importlib import resources
from pathlib import Path
import json

from DailyData import time_management

from . import analyzer as analyzer_pkg
from . import tracker as tracker_pkg
from . import time_management as time_management_pkg

from .__main__ import take_args

from sys import argv as __argv


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


if '--use-config' in __argv:
    __i = __argv.index('--use-config')

    with open(__argv[__i+1], mode='r') as cfg_file:
        config = Configuration(**json.load(cfg_file))

    del __argv[__i+1]
    __argv.remove('--use-config')
else:
    # TODO change to importlib instead of pkg_resources
    config = Configuration(
        **json.loads(resources.read_text(__name__, 'config.json')))


if not config.configured and '--config-file' not in __argv:
    raise ValueError(
        'DailyData not configured! Edit the file at \'dailydata --config-file\' to configure this module')
