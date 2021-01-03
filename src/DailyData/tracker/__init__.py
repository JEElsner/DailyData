from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

import DailyData

from .journaller import Journaller


@dataclass
class Configuration:
    data_folder: Path

    name: str
    journal_suffix: str
    columns: List[str]
    activity_questions_count: int
    activity_questions: Dict[str, str]
    greeting: str = 'Heyo'
    open_journal: bool = False
    journal_folder: Path = Path('.\\journals\\')
    stats_folder: Path = Path('.\\journal_stats\\')
    data_suffix: str = '.csv'
    delimiter: str = ','

    def __post_init__(self):
        self.data_folder = Path(self.data_folder)

        self.journal_folder = self.data_folder.joinpath(self.journal_folder)
        self.stats_folder = self.data_folder.joinpath(self.stats_folder)
