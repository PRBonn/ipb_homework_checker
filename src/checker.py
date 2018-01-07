#!/usr/bin/python3
"""Check the homework."""
import sys
import yaml
import logging

from os import path

import tools

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
EXCERCISES_TAG = 'excercises'

CPP_TAGS = ['cpp', 'c++', 'CPP', 'C++']


class Checker:
    """Check homework."""

    def __init__(self, job_file_path):
        """Initialize the checker from file."""
        with open(job_file_path, 'r') as stream:
            self._base_node = yaml.safe_load(stream)[BASE_TAG]
            self._root_folder = path.expanduser(
                self._base_node[ROOT_FOLDER_TAG])

    def check_homework(self):
        """Run over all excercises in a homework."""
        for excercise in self._base_node[EXCERCISES_TAG]:
            cwd = path.join(self._root_folder, excercise[FOLDER_TAG], 'build')
            tools.create_folder_if_needed(cwd)
            build_result = self._build_excercise(excercise, cwd)
            if not build_result.succeeded():
                log.error("Build failed with error: \n%s", build_result.error)
                continue
            self._run_all_tests(excercise, cwd)

    def _run_all_tests(self, excercise, cwd):
        """Iterate over the tests in the job and check them."""
        language = excercise[LANGUAGE_TAG]
        for test in excercise[TESTS_TAG]:
            test_result = self._run_test(test, language, cwd)
            if test_result.succeeded():
                log.info('Passed test: %s', test[NAME_TAG])
            else:
                log.error('Test %s FAILED with output: %s.',
                          test[NAME_TAG], test_result.error)

    def _build_excercise(self, excercise, cwd):
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
    checker.check_homework()


if __name__ == "__main__":
    main()
