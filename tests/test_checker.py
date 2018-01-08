#!/usr/bin/python3
"""Test the checker."""

import unittest
from os import sys

sys.path.append('src')
sys.path.append('../src')

from checker import Checker


class TestChecker(unittest.TestCase):
    """Test the checker."""

    def test_exercise_success(self):
        """Dummy test."""
        checker = Checker('tests/example_job.yml')
        results = checker.check_homework()
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results['Exercise 1']), 2)
        self.assertTrue(results['Exercise 1']['Test 1'].succeeded())
        self.assertTrue(results['Exercise 1']['Test 2'].succeeded())
