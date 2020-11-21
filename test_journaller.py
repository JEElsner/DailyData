import unittest

import journaller as j

# Don't use this, it's old lmao


class JournalTest(unittest.TestCase):
    def test_ask_question(self):
        answer = j.ask_question('Answer 3 ', in_bounds=lambda x: x ==
                                3, cast=int, error='No')

        self.assertEqual(answer, 3)

    def test_load_activites(self):
        activities = j.load_activities('./activities.txt')

        self.assertEqual(activities[0], 'cook a meal')

    def test_load_events(self):
        events = j.load_questions('./events.csv')

        self.assertEqual(events['rain'], 'Did it rain today?')


if __name__ == '__main__':
    unittest.main()
