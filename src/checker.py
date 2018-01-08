#!/usr/bin/python3
"""Check the homework."""
import sys
import yaml
import logging

from os import path

import tools
from md_writer import MdWriter

logging.basicConfig()
log = logging.getLogger("GHC")
log.setLevel(logging.DEBUG)


BASE_TAG = 'base_node'
NAME_TAG = 'name'
TESTS_TAG = 'tests'
FOLDER_TAG = 'folder'
INPUT_TAG = 'input_args'
LANGUAGE_TAG = 'language'
OUTPUT_TAG = 'expected_output'
ROOT_FOLDER_TAG = 'root_folder'
EXERCISES_TAG = 'exercises'

CPP_TAGS = ['cpp', 'c++', 'CPP', 'C++']


class Checker:
    """Check homework."""

    def __init__(self, job_file_path):
        """Initialize the checker from file."""
        with open(job_file_path, 'r') as stream:
            self._base_node = yaml.safe_load(stream)[BASE_TAG]
            self._root_folder = tools.expand_if_needed(
                self._base_node[ROOT_FOLDER_TAG])
            # The results of all tests will be kept here.
            self._results = {}

    def check_homework(self):
        """Run over all exercises in a homework."""
        results = {}
        for exercise in self._base_node[EXERCISES_TAG]:
            cwd = path.join(self._root_folder, exercise[FOLDER_TAG], 'build')
            tools.create_folder_if_needed(cwd)
            build_result = self._build_exercise(exercise, cwd)
            if not build_result.succeeded():
                log.error("Build failed with error: \n%s", build_result.error)
                results.update(build_result)
                continue
            results.update(self._run_all_tests(exercise, cwd))
        return results

    def _run_all_tests(self, exercise, cwd):
        """Iterate over the tests in the job and check them."""
        language = exercise[LANGUAGE_TAG]
        results = {}
        for test in exercise[TESTS_TAG]:
            test_result = self._run_test(test, language, cwd)
            results[test[NAME_TAG]] = test_result
        return results

    def _build_exercise(self, exercise, cwd):
        build_cmd = "cmake .. && make"
        return tools.run_command(build_cmd, cwd=cwd)

    def _run_test(self, current_test, language, cwd):
        if language in CPP_TAGS:
            return self._run_cpp_test(current_test, cwd)
        return None

    def _run_cpp_test(self, current_test, cwd):
        input_str = ''
        if INPUT_TAG in current_test:
            input_str = current_test[INPUT_TAG]
        run_cmd = "./main {args}".format(args=input_str)
        return tools.run_command(run_cmd, cwd=cwd)


def main():
    """Run this script."""
    checker = Checker(sys.argv[1])
    results = checker.check_homework()
    md_writer = MdWriter()
    md_writer.update(results)
    md_writer.write_md_file('test.md')


if __name__ == "__main__":
    main()
