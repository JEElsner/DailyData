from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import List, Dict

import DailyData

from .journaller import Journaller


@dataclass
class TrackerConfig:
    data_folder: Path = './data'

    name: str = None
    journal_suffix: str = '.md'
    columns: List[str] = field(default_factory=list)
    activity_questions_count: int = 0
    activity_questions: Dict[str, str] = field(default_factory=dict)
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
