from typing import Iterable

import re


def count_words(lines: Iterable[str]):
    counts = dict()
    order = []

    # Iterate through each word in each line, incrementing a counter for each word
    for line in lines:
        # Split lines on 'not-word' character groups
        for w in re.split('\\W+', line):
            if w not in order:
                counts.update({w: 1})
                order.append(w)
            else:
                counts[w] += 1

                # Keep words ordered by frequency so we don't have to loop through
                # them again later to sort them.
                rank = order.index(w)
                # If the current word has a greater frequency than the word that has
                # a higher frequency ranking, switch them
                if counts[order[rank]] > counts[order[rank-1]]:
                    # Swap positions
                    tmp = order[rank-1]
                    order[rank-1] = order[rank]
                    order[rank] = tmp

    return order, counts
