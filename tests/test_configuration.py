import unittest

import DailyData


class TestConfiguration(unittest.TestCase):
    def test_DailyData_configuration(self):
        self.assertIsNotNone(DailyData.config)

        self.assertIsInstance(DailyData.config.configured, bool)
        self.assertIsInstance(DailyData.config.data_folder, str)
        self.assertIsInstance(DailyData.config.analyzer,
                              DailyData.analyzer.Configuration)
        self.assertIsInstance(DailyData.config.tracker,
                              DailyData.tracker.Configuration)


if __name__ == '__main__':
    unittest.main()
