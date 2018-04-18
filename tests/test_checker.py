#!/usr/bin/python3
"""Test the checker."""

import unittest
from os import sys

sys.path.append('src')
sys.path.append('../src')

from checker import Checker
import tools


class TestChecker(unittest.TestCase):
    """Test the checker."""

    def test_everything(self):
        """Check all homeworks and Tasks."""
        self.maxDiff = None

        checker = Checker('tests/data/homework/example_job.yml')
        results = checker.check_homework()
        self.assertEqual(len(results), 3)
        self.assertEqual(len(results['Homework 1']), 4)
        self.assertEqual(len(results['Homework 1']['Task 1']), 3)
        self.assertEqual(len(results['Homework 2']), 2)
        self.assertEqual(results['Homework 1']
                         ['Task 1']['Test 1'].stderr, "")
        self.assertTrue(results['Homework 1']
                        ['Task 1']['Test 1'].succeeded())
        self.assertTrue(results['Homework 1']
                        ['Task 1']['Test 2'].succeeded())

        self.assertEqual(len(results['Homework 1']['Task 2']), 1)
        self.assertNotIn("Test 1", results['Homework 1']['Task 2'])
        self.assertIn("Build Succeeded", results['Homework 1']['Task 2'])

        self.assertTrue(results['Homework 1']
                        ['Task 3']['Test 1'].succeeded())
        self.assertFalse(results['Homework 1']
                         ['Task 3']['Test 2'].succeeded())

        self.assertIn('Style Errors', results['Homework 1']['Task 4'])
        self.assertTrue(results['Homework 1']
                        ['Task 4']['Test 1'].succeeded())
        self.assertFalse(results['Homework 1']
                         ['Task 4']['Test 2'].succeeded())

        self.assertFalse(results['Homework 2']
                         ['Task 1']['Test 1'].succeeded())
        self.assertIsNotNone(results['Homework 2']
                             ['Task 2']['Test 1'])
        self.assertEqual(results['Homework 2']
                         ['Task 2']['Test 1'].stderr, '')
        self.assertTrue(results['Homework 2']
                        ['Task 2']['Test 1'].succeeded())

        self.assertIsNotNone(results['Homework 3']
                             ['Google Tests']['Just build'])
        self.assertTrue(results['Homework 3']
                        ['Google Tests']['Just build'].succeeded())
        self.assertIsNotNone(results['Homework 3']
                             ['Google Tests']['Inject pass'])
        self.assertEqual(results['Homework 3']
                         ['Google Tests']['Inject pass'].stderr, '')
        self.assertTrue(results['Homework 3']
                        ['Google Tests']['Inject pass'].succeeded())
        self.assertIsNotNone(results['Homework 3']
                             ['Google Tests']['Inject fail'])
        self.assertEqual(results['Homework 3']
                         ['Google Tests']['Inject fail'].stderr,
                         'Errors while running CTest\n')
        self.assertFalse(results['Homework 3']
                         ['Google Tests']['Inject fail'].succeeded())
        self.assertIn(tools.EXPIRED_TAG, results['Homework 3'])
