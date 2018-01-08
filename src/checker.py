"""Check the homework."""
import yaml

from os import path

import tools

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


class Exercise:
    """Define an exercise."""

    @staticmethod
    def from_yaml_node(exercise_node, root_folder):
        """Create an exercise appropriate for the language."""
        if exercise_node[LANGUAGE_TAG] in CPP_TAGS:
            return CppExercise(exercise_node, root_folder)

    def __init__(self, exercise_node, root_folder):
        """Initialize a generic exercise."""
        self.name = exercise_node[NAME_TAG]
        self._test_nodes = exercise_node[TESTS_TAG]
        self._cwd = path.join(root_folder, exercise_node[FOLDER_TAG])

    def check_all_tests(self):
        """Iterate over the tests and check them."""
        # Generate empty results.
        results = {}
        # Build the source if this is needed.
        build_result = self._build_if_needed()
        if not build_result.succeeded():
            # The build has failed, so no further testing needed.
            results[self.name] = build_result
            return results
        # The build is either not needed or succeeded. Continue testing.
        for test_node in self._test_nodes:
            test_result = self._run_test(test_node)
            results[test_node[NAME_TAG]] = test_result
        return results

    def _build_if_needed(self):
        raise NotImplementedError('This method is not implemented.')

    def _run_test(self, test_node):
        raise NotImplementedError('This method is not implemented.')


class CppExercise(Exercise):
    """Define a C++ exercise."""
    BUILD_CMD = "cmake .. && make"

    def __init__(self, exercise_node, root_folder):
        """Initialize the C++ exercise."""
        super().__init__(exercise_node, root_folder)
        # The C++ project will always work from build folder.
        self._cwd = path.join(self._cwd, 'build')
        tools.create_folder_if_needed(self._cwd)

    def _build_if_needed(self):
        return tools.run_command(CppExercise.BUILD_CMD, cwd=self._cwd)

    def _run_test(self, test_node):
        input_str = ''
        if INPUT_TAG in test_node:
            input_str = test_node[INPUT_TAG]
        run_cmd = "./main {args}".format(args=input_str)
        return tools.run_command(run_cmd, cwd=self._cwd)


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
        for exercise_node in self._base_node[EXERCISES_TAG]:
            exercise = Exercise.from_yaml_node(exercise_node,
                                               self._root_folder)
            results[exercise.name] = exercise.check_all_tests()
        return results
