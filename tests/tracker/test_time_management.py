import unittest

import DailyData.time_management as manager


class TestTimeManagement(unittest.TestCase):
    def test_parse_args(self):
        args, kwargs = manager._parse_args(
            ['foo', 'bar', '-b', 'test', '--oui', 'yeah', 'baz'])

        self.assertListEqual(args, ['foo', 'bar', 'baz'])
        self.assertDictEqual(kwargs, {'b': 'test', 'oui': 'yeah'})


if __name__ == '__main__':
    unittest.main()
