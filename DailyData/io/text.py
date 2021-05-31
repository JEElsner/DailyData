from datetime import datetime, timedelta
from os import PathLike
from pathlib import Path
from typing import List
from .timelog_io import TimelogIO

import pandas as pd


class TextIO(TimelogIO):
    def __init__(self, act_folder: Path):
        self.activity_folder = act_folder
        self.act_list_path = self.activity_folder.joinpath('list.txt')

    def record_time(self, activity: str, user: str, timestamp: datetime):
        if not self.activity_folder.exists():
            self.activity_folder.mkdir()

        if not self.act_list_path.exists():
            open(self.act_list_path, mode='w').close()

        with open(self.act_list_path, mode='r+') as act_list:
            if (activity + '\n') not in act_list:
                raise ValueError('Unknown activity {}'.format(activity))

        with open(self.activity_folder.joinpath(timestamp.strftime('%Y-%m') + '.csv'), mode='a') as file:
            file.write(','.join([activity, str(timestamp), '\n']))

    def get_timestamps(self, earliest: datetime, latest: datetime) -> List:
        all = pd.DataFrame(columns=['activity', 'time'])

        for csv_path in self.activity_folder.glob('*.csv'):
            file_date = datetime.strptime(csv_path.stem, '%Y-%m')

            if earliest <= file_date <= latest:
                with open(csv_path) as file:
                    df = pd.read_csv(
                        file, names=['activity', 'time'], usecols=[0, 1])
                    df['time'] = pd.to_datetime(df['time'])

                    df.drop(df[df['time'] > latest].index, inplace=True)
                    df.drop(df[df['time'] < earliest].index, inplace=True)

                    all = all.append(df, ignore_index=True)

        return all

    def new_activity(self, activity: str, parent: str, is_alias: bool):
        raise NotImplementedError()
