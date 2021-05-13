from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import List, Dict


@dataclass
class TrackerConfig:
    name: str = None
    journal_suffix: str = '.md'
    columns: List[str] = field(default_factory=list)
    activity_questions_count: int = 0
    activity_questions: Dict[str, str] = field(default_factory=dict)
    greeting: str = 'Heyo'
    open_journal: bool = False
    journal_folder: Path = Path('./data/journals')
    stats_folder: Path = Path('./data/journal_stats')
    data_suffix: str = '.csv'
    delimiter: str = ','

    def __post_init__(self):
        self.journal_folder = Path(self.journal_folder)
        self.stats_folder = Path(self.stats_folder)
