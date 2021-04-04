import json
import os
from dataclasses import dataclass, asdict
from importlib import resources
from pathlib import Path

from .analyzer.config import AnalyzerConfig
from .time_management.config import TimeManagementConfig
from .tracker.config import TrackerConfig

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
            self.time_management = TimeManagementConfig(**self.time_management)

        if not isinstance(self.tracker, TrackerConfig):
            self.tracker = TrackerConfig(**self.tracker)

    def __enter__(self):
        pass

    def __exit__(self, exception_type: BaseException, exception: Exception, traceback):
        save_config(self, cfg_file_location)


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
    if save_location is None:
        save_location = cfg_file_location

    # if not save_location.parent.exists():
    #     save_location.parent.mkdir()

    json.dump(asdict(config), save_location.open(mode='w'),
              indent='\t', default=__non_serializable_parser)


def __non_serializable_parser(value):
    if isinstance(value, Path):
        return str(value.absolute())
