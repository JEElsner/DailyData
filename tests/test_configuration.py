from pathlib import Path
import unittest

import DailyData


class TestConfiguration(unittest.TestCase):
    def test_DailyData_configuration(self):
        self.assertIsNotNone(DailyData.master_config)

        self.assertIsInstance(DailyData.master_config.configured, bool)
        self.assertIsInstance(DailyData.master_config.data_folder, Path)
        # self.assertIsInstance(DailyData.master_config.analyzer,
        #                       DailyData.analyzer.Configuration)
        # self.assertIsInstance(DailyData.master_config.tracker,
        #                       DailyData.tracker.Configuration)


if __name__ == '__main__':
    unittest.main()
