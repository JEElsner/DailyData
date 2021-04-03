from dataclasses import dataclass
from pathlib import Path

from . import analyzer as analyzer_pkg
from . import time_management as time_management_pkg
from . import tracker as tracker_pkg

from importlib import resources
import json
import os

cfg_file_location = None


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


def load_config(cfg_file: Path = None):
    if cfg_file is not None:
        cfg_file_location = cfg_file
        return Configuration(**json.load(cfg_file))

    cwd_config = Path(os.getcwd()).joinpath('config.json')
    usr_config = Path.home().joinpath('.dailydata_config.json')

    # Try to find a configuration file. First check the directory where the script is, then check the working directory, then the user directory
    # Along with creating the configuration, also set the save location for the config file when the program exits
    if resources.is_resource('DailyData', 'config.json'):
        cfg_file_location = None
        return Configuration(**json.loads(resources.read_text(__name__, 'config.json')))

    elif cwd_config.exists():
        cfg_file_location = cwd_config
        return Configuration(**json.load(cwd_config.open()))
    elif usr_config.exists():
        cfg_file_location = usr_config
        return Configuration(**json.load(usr_config.open()))
    else:
        # Create default configuration if one doesn't exist
        cfg_file_location = cwd_config
        return Configuration()


def save_config(config: Configuration, save_location: Path = None):
    if save_location is not None:
        json.dump(config, save_location.open())
    else:
        json.dump(config, cfg_file_location.open())
