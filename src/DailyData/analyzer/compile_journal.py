import json
import re
from pathlib import Path
from typing import Iterable

import pandas as pd

from .parse_docx import get_lines


def load_journal_entries(
    journal_path, parser=get_lines,
    output='./output.xlsx',
    word_count_cutoff=100,
    word_counts='./counts.json',
    pd_output=pd.DataFrame.to_excel
):
    if output.startswith('.') or word_counts.startswith('.'):
        path = Path(journal_path)
        parent_dir = path.parent

        output_path = parent_dir.joinpath(output)
        word_counts_path = parent_dir.joinpath(word_counts)
    else:
        output_path = Path(output)
        word_counts_path = Path(word_counts)

    entries = parser(journal_path)

    data = pd.DataFrame.from_records(entries, columns=['date', 'entry'])
    data['date'] = pd.to_datetime(data['date'])
    data.set_index('date')
    order, counts = count_words(data['entry'])

    save_most_common_words(order[:word_count_cutoff], counts, word_counts_path)
    pd_output(data, output_path)


def count_words(lines: Iterable[str]):
    counts = dict()
    order = []

    if type(lines) == str:
        lines = [lines]

    # Iterate through each word in each line, incrementing a counter for each word
    for line in lines:
        # Split lines on 'not-word' character groups
        for w in re.split('\\W+', line):
            if w not in order:
                counts.update({w: 1})
                order.append(w)
            else:
                counts[w] += 1

                while True:
                    # Keep words ordered by frequency so we don't have to loop through
                    # them again later to sort them.

                    # We need a loop in case a letter becomes more frequent than
                    # two words of the same frequency

                    rank = order.index(w)

                    # If the current word has a greater frequency than the word that has
                    # a higher frequency ranking, switch them
                    if rank == 0:  # If
                        break
                    elif counts[order[rank]] > counts[order[rank-1]]:
                        # Swap positions
                        tmp = order[rank-1]
                        order[rank-1] = order[rank]
                        order[rank] = tmp
                    else:  # When the list is in the right order, break
                        break

    return order, counts


def save_most_common_words(order, counts, file_path):
    path = Path(file_path)
    if not path.exists():
        open(file_path, mode='x').close()

    with open(file_path, mode='w') as file:
        json.dump(
            {word: {'count': counts[word], 'include': False} for word in order}, file)


def load_ignore_words(file_path):
    with open(file_path, mode='r') as file:
        d = json.load(file)

        return (word for word in d if not d[word]['include'])
