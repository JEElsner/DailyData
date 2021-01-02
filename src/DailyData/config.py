from dataclasses import dataclass
import pkg_resources
from pathlib import Path
import json

from .analyzer import Configuration as AnalyzerConfig
from .tracker import Configuration as TrackerConfig


@dataclass
class Configuration:
    configured: bool
    data_folder: Path
    analyzer: AnalyzerConfig
    tracker: TrackerConfig

    def __post_init__(self):
        self.analyzer = AnalyzerConfig(**self.analyzer)
        self.tracker = TrackerConfig(**self.tracker)


config = Configuration(
    **json.loads(pkg_resources.resource_string(__name__, 'config.json')))
