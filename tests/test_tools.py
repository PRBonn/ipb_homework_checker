#!/usr/bin/python3
"""Test the tools."""

import unittest
from os import sys
from os import path

sys.path.append('src')
sys.path.append('../src')

import tools
from schema_tags import OutputTags


class TestTools(unittest.TestCase):
    """Test the checker."""

    def test_pkg_name(self):
        """Pkg name test."""
        self.assertEqual(tools.PKG_NAME, 'homework_checker')
        if path.basename(tools.PROJECT_ROOT_FOLDER):
            self.assertEqual(path.basename(tools.PROJECT_ROOT_FOLDER),
                             'generic-homework-checker')

    def test_convert_to(self):
        """Test conversion to expected type."""
        output, error = tools.convert_to(OutputTags.NUMBER, "value")
        self.assertEqual(output, None)
        self.assertEqual(error, "could not convert string to float: 'value'")

        output, error = tools.convert_to(OutputTags.STRING, 3.14)
        self.assertEqual(output, "3.14")
        self.assertEqual(error, "OK")

        output, error = tools.convert_to(OutputTags.NUMBER, "3.14")
        self.assertEqual(output, 3.14)
        self.assertEqual(error, "OK")
