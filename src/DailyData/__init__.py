from dataclasses import dataclass
import pkg_resources
from pathlib import Path
import json

from . import analyzer as analyzer_pkg
from . import tracker as tracker_pkg


@dataclass
class Configuration:
    configured: bool
    data_folder: Path
    analyzer: analyzer_pkg.Configuration
    tracker: tracker_pkg.Configuration

    def __post_init__(self):
        self.analyzer = analyzer_pkg.Configuration(**self.analyzer)
        self.tracker = tracker_pkg.Configuration(**self.tracker)


config = Configuration(
    **json.loads(pkg_resources.resource_string(__name__, 'config.json')))
