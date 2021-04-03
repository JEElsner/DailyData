from dataclasses import dataclass
from pathlib import Path

from .analyzer import AnalyzerConfig
from .time_management import TimeManagementConfig
from .tracker import TrackerConfig

from importlib import resources
import json
import os

cfg_file_location = None


@dataclass
class MasterConfig:
    configured: bool = False
    data_folder: Path = './data'
    analyzer: AnalyzerConfig = AnalyzerConfig()
    time_management: TimeManagementConfig = TimeManagementConfig()
    tracker: TrackerConfig = TrackerConfig()

    def __post_init__(self):
        self.data_folder = Path(self.data_folder)

        if not isinstance(self.analyzer, AnalyzerConfig):
            self.analyzer = AnalyzerConfig(**self.analyzer)

        if not isinstance(self.time_management, TimeManagementConfig):
            self.time_management = TimeManagementConfig(
                data_folder=self.data_folder,
                **self.time_management
            )

        if not isinstance(self.tracker, TrackerConfig):
            self.tracker = TrackerConfig(
                data_folder=self.data_folder,
                **self.tracker)


def load_config(cfg_file: Path = None):
    global cfg_file_location

    if cfg_file is not None:
        cfg_file_location = cfg_file
        return MasterConfig(**json.load(cfg_file.open()))

    cwd_config = Path(os.getcwd()).joinpath('config.json')
    usr_config = Path.home().joinpath('.dailydata_config.json')

    # Try to find a configuration file. First check the directory where the script is, then check the working directory, then the user directory
    # Along with creating the configuration, also set the save location for the config file when the program exits
    if resources.is_resource('DailyData', 'config.json'):
        cfg_file_location = None
        return MasterConfig(**json.loads(resources.read_text(__name__, 'config.json')))

    elif cwd_config.exists():
        cfg_file_location = cwd_config
        return MasterConfig(**json.load(cwd_config.open()))
    elif usr_config.exists():
        cfg_file_location = usr_config
        return MasterConfig(**json.load(usr_config.open()))
    else:
        # Create default configuration if one doesn't exist
        cfg_file_location = cwd_config
        return MasterConfig()


def save_config(config: MasterConfig, save_location: Path = None):
    if save_location is not None:
        json.dump(config, save_location.open())
    else:
        json.dump(config, cfg_file_location.open())
