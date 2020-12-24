from DailyData.analyzer import compile_journal

import unittest

import json


class TestCompileJournal(unittest.TestCase):
    def test_word_count(self):
        lines = ['c c b b a a a a', 'b']

        expected_order = ['a', 'b', 'c']
        expected_counts = {'c': 2, 'b': 3, 'a': 4}

        actual_order, actual_counts = compile_journal.count_words(lines)

        self.assertSequenceEqual(actual_order, expected_order)
        self.assertDictEqual(actual_counts, expected_counts)

    def test_single_line_word_count(self):
        line = 'a b c c d e'

        order, counts = compile_journal.count_words(line)

        self.assertEqual(order[0], 'c')
        self.assertSetEqual(set(order), {'a', 'b', 'c', 'd', 'e'})

    def test_save_common_words(self):
        file_path = './tests/test_words.json'

        order = ['a', 'b', 'c']
        counts = {'a': 3, 'b': 2, 'c': 1}

        compile_journal.save_most_common_words(
            order, counts, file_path)

        with open(file_path, mode='r') as file:
            output = json.load(file)

            self.assertDictEqual(
                output, {w: {'count': counts[w], 'include': False} for w in order})


if __name__ == '__main__':
    unittest.main()
