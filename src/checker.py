"""Check the homework."""

from os import path

import logging
import tools
from schema_tags import Tags, LangTags, BuildTags
from schema_manager import SchemaManager

OUTPUT_MISMATCH_MESSAGE = """Given input: '{input}'
Your output '{actual}'
Expected output: '{expected}'"""

OUTPUT_CONVERSION_ERROR = """Expected output of type: '{expected_type}'.
Got the output of type '{actual_type}'"""


log = logging.getLogger("GHC")


class Exercise:
    """Define an abstract exercise."""

    @staticmethod
    def from_yaml_node(exercise_node, root_folder):
        """Create an exercise appropriate for the language."""
        if exercise_node[Tags.LANGUAGE_TAG] == LangTags.CPP:
            return CppExercise(exercise_node, root_folder)
        else:
            log.error("Unknown exercise language.")
            return None

    def __init__(self, exercise_node, root_folder):
        """Initialize a generic exercise."""
        self.name = exercise_node[Tags.NAME_TAG]
        self._test_nodes = exercise_node[Tags.TESTS_TAG]
        self._output_type = exercise_node[Tags.OUTPUT_TYPE_TAG]
        self._cwd = path.join(root_folder, exercise_node[Tags.FOLDER_TAG])
        if Tags.BINARY_NAME_TAG in exercise_node:
            self._binary_name = exercise_node[Tags.BINARY_NAME_TAG]
        else:
            self._binary_name = "main"

    def check_all_tests(self):
        """Iterate over the tests and check them."""
        # Generate empty results.
        results = {}
        # Build the source if this is needed.
        build_result = self._build_if_needed()
        if not build_result.succeeded():
            # The build has failed, so no further testing needed.
            results['Build Failed'] = build_result
            return results
        # The build is either not needed or succeeded. Continue testing.
        for test_node in self._test_nodes:
            test_result = self._run_test(test_node)
            results[test_node[Tags.NAME_TAG]] = test_result
        return results

    def _build_if_needed(self):
        raise NotImplementedError('This method is not implemented.')

    def _run_test(self, test_node):
        raise NotImplementedError('This method is not implemented.')


class CppExercise(Exercise):
    """Define a C++ exercise."""
    BUILD_CMD = "cmake .. && make"
    BUILD_CMD_SIMPLE = "clang++ -std=c++11 -o {binary} {binary}.cpp"

    def __init__(self, exercise_node, root_folder):
        """Initialize the C++ exercise."""
        super().__init__(exercise_node, root_folder)
        self._build_type = exercise_node[Tags.BUILD_TYPE_TAG]
        if self._build_type == BuildTags.CMAKE:
            # The cmake project will always work from build folder.
            self._cwd = path.join(self._cwd, 'build')
            tools.create_folder_if_needed(self._cwd)

    def _build_if_needed(self):
        if self._build_type == BuildTags.CMAKE:
            return tools.run_command(CppExercise.BUILD_CMD, cwd=self._cwd)
        return tools.run_command(CppExercise.BUILD_CMD_SIMPLE.format(
            binary=self._binary_name), cwd=self._cwd)

    def _run_test(self, test_node):
        input_str = ''
        if Tags.INPUT_TAG in test_node:
            input_str = test_node[Tags.INPUT_TAG]
        run_cmd = "./{binary_name} {args}".format(
            binary_name=self._binary_name, args=input_str)
        run_result = tools.run_command(run_cmd, cwd=self._cwd)
        if not run_result.succeeded():
            return run_result
        our_output, error = tools.convert_to(
            self._output_type, run_result.stdout)
        if not our_output:
            # Conversion has failed.
            run_result.stderr = error
            return run_result
        expected_output, error = tools.convert_to(
            self._output_type, test_node[Tags.OUTPUT_TAG])
        if our_output != expected_output:
            run_result.stderr = OUTPUT_MISMATCH_MESSAGE.format(
                actual=our_output, input=input_str, expected=expected_output)
        return run_result


class Checker:
    """Check homework."""

    def __init__(self, job_file_path):
        """Initialize the checker from file."""
        schema_manager = SchemaManager(job_file_path)
        self._base_node = schema_manager.validated_yaml

        self._root_folder = tools.expand_if_needed(
            self._base_node[Tags.FOLDER_TAG])
        # The results of all tests will be kept here.
        self._results = {}

    def check_homework(self):
        """Run over all exercises in all homeworks."""
        results = {}
        for homework_node in self._base_node[Tags.HOMEWORKS_TAG]:
            current_folder = path.join(
                self._root_folder, homework_node[Tags.FOLDER_TAG])
            hw_name = homework_node[Tags.NAME_TAG]
            results[hw_name] = {}
            for exercise_node in homework_node[Tags.EXERCISES_TAG]:
                exercise = Exercise.from_yaml_node(exercise_node,
                                                   current_folder)
                results[hw_name][exercise.name] = exercise.check_all_tests()
        return results
