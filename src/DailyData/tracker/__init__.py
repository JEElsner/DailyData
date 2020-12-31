from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

import DailyData


@dataclass
class Configuration:
    name: str
    journal_suffix: str
    columns: List[str]
    activity_questions_count: int
    activity_questions: Dict[str, str]
    greeting: str = 'Heyo'
    open_journal: bool = False
    journal_folder: Path = Path('.\\journals\\')
    data_folder: Path = Path('.\\data\\')
    data_suffix: str = '.csv'
    delimiter: str = ','
