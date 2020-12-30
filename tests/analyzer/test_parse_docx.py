import unittest

from DailyData.analyzer import parse_docx


class TestParseDocx(unittest.TestCase):
    def test_get_lines(self):
        entries = list(parse_docx.get_lines('./tests/test.docx'))

        self.assertEqual(len(entries), 1)

        heading, entry = entries[0]

        self.assertEqual(heading, 'That scene in the hangar')
        self.assertEqual(
            entry, 'Hello there\nGeneral Kenobi\nYou are a bold one')


if __name__ == '__main__':
    unittest.main()
