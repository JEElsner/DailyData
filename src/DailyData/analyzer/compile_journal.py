from typing import Iterable

import json

import re

from pathlib import Path


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
