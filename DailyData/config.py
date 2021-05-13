import json
import os
from dataclasses import dataclass, asdict
from importlib import resources
from pathlib import Path

from .analyzer.config import AnalyzerConfig
from .time_management.config import TimeManagementConfig
from .tracker.config import TrackerConfig

import ConsoleQuestionPrompts as questions

cfg_file_location = None

cwd_config = Path(os.getcwd()).joinpath('config.json')
usr_config = Path.home().joinpath('.dailydata_config.json')


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
        cfg_file_location = usr_config
        return initial_setup()


def save_config(config: MasterConfig, save_location: Path = None):
    if save_location is None:
        save_location = cfg_file_location

    # if not save_location.parent.exists():
    #     save_location.parent.mkdir()

    json.dump(asdict(config), save_location.open(mode='w'),
              indent='\t', default=__json_encoder)


def __json_encoder(value):
    from datetime import datetime, timedelta

    if isinstance(value, Path):
        return str(value.absolute())
    elif isinstance(value, datetime):
        return str(value)
    elif isinstance(value, timedelta):
        return value.total_seconds()
    else:
        raise TypeError(
            'Object of type {0} is not JSON serializable'.format(type(value)))


def initial_setup(current: MasterConfig = MasterConfig(), first_time=True) -> MasterConfig:
    new_config = MasterConfig()

    if first_time:
        print('Welcome! It looks like this is your first time using DailyData! Answer these setup questions to get started!')
        input('Press [ENTER] to continue')

        global cfg_file_location

        cfg_file_location = questions.option_question('Where would you like this configuration to be saved? (Default: user directory)',
                                                      options=[
                                                          'In the user directory',
                                                          'In the current working directory',
                                                          'Elsewhere (will not load automatically)'
                                                      ],
                                                      return_values=[usr_config, cwd_config, 'elsewhere'])

        if cfg_file_location == 'elsewhere':
            location: Path = None
            while location is None or location.exists():
                location = questions.ask_question('Where would you like to save the configuration file? ',
                                                  in_bounds=lambda file: file.parent.exists() and file.parent.is_dir(),
                                                  cast=lambda s: Path(s),
                                                  error='The parent directory does not exist')

                if location.exists() and not questions.yes_no_question('{0} already exists, overwrite (y/n)? '.format(location.absolute())):
                    location = None

            cfg_file_location = location

    new_config.tracker.name = questions.ask_question('What is your name? ')
    new_config.tracker.greeting = questions.ask_question(
        'How would you like to be greeted? (Current: {0}) '.format(
            current.tracker.greeting)
    )

    new_config.tracker.open_journal = questions.yes_no_question(
        'Would you like to open a text editor after recording data (y/n)? ')

    if new_config.tracker.open_journal:
        new_config.tracker.journal_suffix = questions.ask_question(
            'What file extension should be used for text journals? (e.g. .txt) ')

    good_file = False
    while not good_file:
        new_config.data_folder = questions.ask_question(
            'Where would you like to store your data? ',
            in_bounds=lambda file: file.parent.exists() and file.parent.is_dir(),
            cast=lambda s: Path(s),
            error='The parent directory does not exist.')

        if new_config.data_folder.exists():
            good_file = questions.yes_no_question(
                '{0} already exists, use this path? '.format(new_config.data_folder.absolute()))
        else:
            good_file = True

    new_config.time_management.activity_folder = new_config.data_folder.joinpath(
        './activities')
    new_config.tracker.journal_folder = new_config.data_folder.joinpath(
        './journals')
    new_config.tracker.stats_folder = new_config.data_folder.joinpath(
        '.journal_stats')

    print('Thanks! It\'s time to get started!')

    new_config.configured = True
    return new_config
