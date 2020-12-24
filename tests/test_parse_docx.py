import unittest

from DailyData.analyzer import parse_docx


class TestParseDocx(unittest.TestCase):
    def test_get_lines(self):
        paras = parse_docx.get_lines('./tests/test.docx')

        self.assertEqual(
            list(paras), ['Hello there', 'General Kenobi\nYou are a bold one'])


if __name__ == '__main__':
    unittest.main()
