#!/usr/bin/python3
"""Test the tools."""

import unittest
from os import sys
from os import path

sys.path.append('src')
sys.path.append('../src')

import tools


class TestTools(unittest.TestCase):
    """Test the checker."""

    def test_pkg_name(self):
        """Pkg name test."""
        self.assertEqual(tools.PKG_NAME, 'homework_checker')
        if path.basename(tools.ROOT_FOLDER):
            self.assertEqual(path.basename(tools.ROOT_FOLDER),
                             'generic-homework-checker')
