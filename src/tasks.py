"""Different types of Tasks."""

import logging
import tools

from os import path

from schema_tags import Tags, LangTags, BuildTags


log = logging.getLogger("GHC")


OUTPUT_MISMATCH_MESSAGE = """Given input: '{input}'
Your output '{actual}'
Expected output: '{expected}'"""


class Task:
    """Define an abstract Task."""

    @staticmethod
    def from_yaml_node(task_node, root_folder):
        """Create an Task appropriate for the language."""
        curr_folder = path.join(root_folder, task_node[Tags.FOLDER_TAG])
        if not path.exists(curr_folder):
            log.warning("Folder '%s' does not exist. Skipping.", curr_folder)
            return None
        language_tag = task_node[Tags.LANGUAGE_TAG]
        if language_tag == LangTags.CPP:
            return CppTask(task_node, curr_folder)
        elif language_tag == LangTags.BASH:
            return BashTask(task_node, curr_folder)
        else:
            log.error("Unknown Task language.")
            return None

    def __init__(self, task_node, curr_folder):
        """Initialize a generic Task."""
        self._test_nodes = []  # Sometimes we don't have tests.
        self.name = task_node[Tags.NAME_TAG]
        if Tags.TESTS_TAG in task_node:
            self._test_nodes = task_node[Tags.TESTS_TAG]
        self._output_type = task_node[Tags.OUTPUT_TYPE_TAG]
        self._curr_folder = curr_folder
        self._cwd = curr_folder
        if Tags.BINARY_NAME_TAG in task_node:
            self._binary_name = task_node[Tags.BINARY_NAME_TAG]
        else:
            self._binary_name = "main"

    def check_all_tests(self):
        """Iterate over the tests and check them."""
        # Generate empty results.
        results = {}
        # Build the source if this is needed.
        build_result = self._build_if_needed()
        if build_result and not build_result.succeeded():
            # The build has failed, so no further testing needed.
            results['Build Failed'] = build_result
            return results
        # The build is either not needed or succeeded. Continue testing.
        for test_node in self._test_nodes:
            test_result = self._run_test(test_node)
            results[test_node[Tags.NAME_TAG]] = test_result
        style_errors = self._code_style_errors()
        if style_errors:
            results['Style Errors'] = style_errors
        return results

    def _build_if_needed(self):
        raise NotImplementedError('This method is not implemented.')

    def _run_test(self, test_node):
        raise NotImplementedError('This method is not implemented.')

    def _code_style_errors(self):
        return None  # Empty implementation.


class CppTask(Task):
    """Define a C++ Task."""
    BUILD_CMD = "cmake .. && make"
    BUILD_CMD_SIMPLE = "clang++ -std=c++11 -o {binary} {binary}.cpp"

    def __init__(self, task_node, root_folder):
        """Initialize the C++ Task."""
        super().__init__(task_node, root_folder)
        self._build_type = task_node[Tags.BUILD_TYPE_TAG]
        if self._build_type == BuildTags.CMAKE:
            # The cmake project will always work from build folder.
            self._cwd = path.join(self._cwd, 'build')
            tools.create_folder_if_needed(self._cwd)

    def _build_if_needed(self):
        if self._build_type == BuildTags.CMAKE:
            return tools.run_command(CppTask.BUILD_CMD, cwd=self._cwd)
        return tools.run_command(CppTask.BUILD_CMD_SIMPLE.format(
            binary=self._binary_name), cwd=self._cwd)

    def _code_style_errors(self):
        """Check if code conforms to Google Style."""
        command = 'cpplint --counting=detailed ' +\
            '--filter=-legal,-readability/todo,-build/include_order' +\
            ' $( find . -name "*.h" -o -name "*.cpp" | grep -vE "^./build/" )'
        result = tools.run_command(command, cwd=self._curr_folder)
        if result.stderr and "Total errors found" in result.stderr:
            return result
        return None

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


class BashTask(Task):
    """Define a Bash Task."""
    RUN_CMD = "sh {binary_name}.sh {args}"

    def __init__(self, task_node, root_folder):
        """Initialize the Task."""
        super().__init__(task_node, root_folder)

    def _build_if_needed(self):
        pass  # There is nothing to build in Bash.

    def _run_test(self, test_node):
        input_str = ''
        if Tags.INPUT_TAG in test_node:
            input_str = test_node[Tags.INPUT_TAG]
        run_cmd = BashTask.RUN_CMD.format(
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
