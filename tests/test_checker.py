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
        """Check all homeworks and exercises."""
        self.maxDiff = None

        checker = Checker('tests/example_job.yml')
        results = checker.check_homework()
        self.assertEqual(len(results), 2)
        self.assertEqual(len(results['Homework 1']), 4)
        self.assertEqual(len(results['Homework 1']['Exercise 1']), 2)
        self.assertEqual(len(results['Homework 2']), 1)
        self.assertEqual(results['Homework 1']
                         ['Exercise 1']['Test 1'].stderr, "")
        self.assertTrue(results['Homework 1']
                        ['Exercise 1']['Test 1'].succeeded())
        self.assertTrue(results['Homework 1']
                        ['Exercise 1']['Test 2'].succeeded())

        self.assertEqual(len(results['Homework 1']['Exercise 2']), 1)
        self.assertNotIn("Test 1", results['Homework 1']['Exercise 2'])
        self.assertIn("Build Failed", results['Homework 1']['Exercise 2'])

        self.assertTrue(results['Homework 1']
                        ['Exercise 3']['Test 1'].succeeded())
        self.assertFalse(results['Homework 1']
                         ['Exercise 3']['Test 2'].succeeded())

        self.assertTrue(results['Homework 1']
                        ['Exercise 4']['Test 1'].succeeded())
        self.assertFalse(results['Homework 1']
                         ['Exercise 4']['Test 2'].succeeded())
