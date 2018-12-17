#!/usr/bin/python3
"""Test the tools."""

import unittest
from os import path

from ipb_homework_checker import tools
from ipb_homework_checker.schema_tags import OutputTags


class TestTools(unittest.TestCase):
    """Test the checker."""

    def test_pkg_name(self):
        """Pkg name test."""
        self.assertEqual(tools.PKG_NAME, 'ipb_homework_checker')
        if path.basename(tools.PROJECT_ROOT_FOLDER):
            self.assertEqual(path.basename(tools.PROJECT_ROOT_FOLDER),
                             'ipb_homework_checker')

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

    def test_max_date(self):
        """Make sure we can rely on max date."""
        self.assertEqual(tools.MAX_DATE_STR, "9999-12-31 23:59:59")

    def test_sleep_timeout(self):
        """Test that we can break an endless loop."""
        from time import monotonic as timer
        start = timer()
        cmd_result = tools.run_command("sleep 10", timeout=1)
        self.assertFalse(cmd_result.succeeded())
        self.assertLess(timer() - start, 5)
        self.assertEqual(
            cmd_result.stderr,
            "Timeout: command 'sleep 10' ran longer than 1 seconds")

    def test_git_url(self):
        """Test that we can break an endless loop."""
        domain, user, project = tools.parse_git_url(
            "https://gitlab.ipb.uni-bonn.de/igor/some_project.git")
        self.assertEqual(domain, "gitlab.ipb.uni-bonn.de")
        self.assertEqual(user, "igor")
        self.assertEqual(project, "some_project")
        domain, user, project = tools.parse_git_url(
            "git@gitlab.ipb.uni-bonn.de:igor/some_project.git")
        self.assertEqual(domain, "gitlab.ipb.uni-bonn.de")
        self.assertEqual(user, "igor")
        self.assertEqual(project, "some_project")
        domain, user, project = tools.parse_git_url(
            "git@github.com:PRBonn/depth_clustering.git")
        self.assertEqual(domain, "github.com")
        self.assertEqual(user, "PRBonn")
        self.assertEqual(project, "depth_clustering")

    def test_endless_loop_timeout(self):
        """Test that we can break an endless loop."""
        from time import monotonic as timer
        path_to_data = path.join(path.dirname(__file__), 'data')
        path_to_file = path.join(path_to_data, 'endless.cpp')
        cmd_build = "c++ -o endless -O0 " + path_to_file
        cmd_result = tools.run_command(cmd_build)
        print(cmd_result.stderr)
        self.assertTrue(cmd_result.succeeded())
        start = timer()
        cmd_result = tools.run_command("./endless", timeout=2)
        self.assertFalse(cmd_result.succeeded())
        self.assertLess(timer() - start, 5)
        self.assertEqual(
            cmd_result.stderr,
            "Timeout: command './endless' ran longer than 2 seconds")
