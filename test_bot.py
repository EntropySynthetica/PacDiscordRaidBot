'''
Unit Test for bot.py
'''

import unittest
import bot

class test_get_trial_id(unittest.TestCase):

    def test_get_trial_id(self):
        result = bot.get_trial_id()
        self.assertRegex(result, r'\d{6}')
