"""Different types of Tasks."""

import logging
from os import path

from . import tools
from .schema_tags import Tags, LangTags, BuildTags


log = logging.getLogger("GHC")


OUTPUT_MISMATCH_MESSAGE = """Given input: '{input}'
Your output '{actual}'
Expected output: '{expected}'"""

BUILD_SUCCESS_TAG = "0. Build succeeded"
STYLE_ERROR_TAG = "0. Style errors"


class Task:
    """Define an abstract Task."""
    BACKUP_FOLDER = '.backup'

    @staticmethod
    def from_yaml_node(task_node, student_hw_folder, job_file):
        """Create an Task appropriate for the language."""
        student_task_folder = path.join(
            student_hw_folder, task_node[Tags.FOLDER_TAG])
        if not path.exists(student_task_folder):
            log.warning("Folder '%s' does not exist. Skipping.",
                        student_task_folder)
            return None
        language_tag = task_node[Tags.LANGUAGE_TAG]
        if language_tag == LangTags.CPP:
            return CppTask(task_node, student_task_folder, job_file)
        elif language_tag == LangTags.BASH:
            return BashTask(task_node, student_task_folder, job_file)
        else:
            log.error("Unknown Task language.")
            return None

    def __init__(self, task_node, student_task_folder, job_file):
        """Initialize a generic Task."""
        self.name = task_node[Tags.NAME_TAG]
        self._job_yaml_folder = path.dirname(job_file)
        self._output_type = task_node[Tags.OUTPUT_TYPE_TAG]
        self._cwd = student_task_folder
        self._student_task_folder = student_task_folder
        self._binary_name = task_node[Tags.BINARY_NAME_TAG]
        self._pipe_through = task_node[Tags.PIPE_TAG]
        self._backup_folder = path.join(
            student_task_folder, Task.BACKUP_FOLDER)
        if Tags.TESTS_TAG in task_node:
            self._test_nodes = task_node[Tags.TESTS_TAG]
        else:
            self._test_nodes = []  # Sometimes we don't have tests.
        self._task_node = task_node

    def check_all_tests(self):
        """Iterate over the tests and check them."""
        # Generate empty results.
        results = {}
        # Build the source if this is needed.
        injected_folders = self.__inject_folders_if_needed(self._task_node)
        build_result = self._build_if_needed()
        self.__restore_injected_folders(self._task_node, injected_folders)
        if build_result:
            results[BUILD_SUCCESS_TAG] = build_result
            if not build_result.succeeded():
                # The build has failed, so no further testing needed.
                return results
        # The build is either not needed or succeeded. Continue testing.
        for test_node in self._test_nodes:
            injected_folders = self.__inject_folders_if_needed(test_node)
            test_result = self._run_test(test_node)
            self.__restore_injected_folders(test_node, injected_folders)
            results[test_node[Tags.NAME_TAG]] = test_result
        style_errors = self._code_style_errors()
        if style_errors:
            results[STYLE_ERROR_TAG] = style_errors
        return results

    def __inject_folders_if_needed(self, node):
        injected_folders = []
        if Tags.INJECT_FOLDER_TAG in node:
            # Inject all needed folders.
            for folder in node[Tags.INJECT_FOLDER_TAG]:
                inject_folder = path.join(self._job_yaml_folder, folder)
                folder_name = path.basename(folder)
                self._inject_folder(folder_name, inject_folder)
                injected_folders.append(folder_name)
        return injected_folders

    def __restore_injected_folders(self, node, injected_folders):
        if Tags.INJECT_FOLDER_TAG in node:
            for folder in injected_folders:
                self._revert_injections(folder)
            from os import rmdir
            rmdir(self._backup_folder)

    def _inject_folder(self, dest_folder, inject_folder):
        full_path_from = inject_folder
        if not path.isabs(full_path_from):
            full_path_from = path.join(self._job_yaml_folder, full_path_from)
        full_path_to = path.join(self._student_task_folder, dest_folder)
        if not path.isdir(self._backup_folder):
            from os import mkdir
            mkdir(self._backup_folder)
        from shutil import copytree, move
        if path.exists(full_path_to):
            # Move the existing data to the backup folder if needed.
            move(full_path_to, self._backup_folder)
        copytree(full_path_from, full_path_to)

    def _revert_injections(self, dest_folder):
        injected_folder = path.join(self._student_task_folder, dest_folder)
        backed_up_folder = path.join(self._backup_folder, dest_folder)
        if path.isdir(injected_folder):
            from shutil import rmtree
            rmtree(injected_folder)
        if not path.isdir(backed_up_folder):
            # There is no backup, so nothing to restore.
            return
        from shutil import move
        move(backed_up_folder, self._student_task_folder)

    def _run_test(self, test_node):
        raise NotImplementedError('This method is not implemented.')

    def _build_if_needed(self):
        return None

    def _code_style_errors(self):
        return None  # Empty implementation.


class CppTask(Task):
    """Define a C++ Task."""
    CMAKE_BUILD_CMD = "cmake .. && make -j2"
    REMAKE_AND_TEST = \
        "make clean && rm -r * && cmake .. && make -j2 && ctest -VV"
    BUILD_CMD_SIMPLE = \
        "clang++ -std=c++14 -o {binary} {compiler_flags} {binary}.cpp"

    def __init__(self, task_node, root_folder, job_file):
        """Initialize the C++ Task."""
        super().__init__(task_node, root_folder, job_file)
        self._compiler_flags = task_node[Tags.COMPILER_FLAGS_TAG]
        self._build_type = task_node[Tags.BUILD_TYPE_TAG]
        if self._build_type == BuildTags.CMAKE:
            # The cmake project will always work from build folder.
            self._cwd = path.join(self._cwd, 'build')
            tools.create_folder_if_needed(self._cwd)

    def _build_if_needed(self):
        if self._build_type == BuildTags.CMAKE:
            return tools.run_command(CppTask.CMAKE_BUILD_CMD,
                                     cwd=self._cwd,
                                     timeout=60)
        return tools.run_command(
            CppTask.BUILD_CMD_SIMPLE.format(
                binary=self._binary_name,
                compiler_flags=self._compiler_flags),
            cwd=self._cwd)

    def _code_style_errors(self):
        """Check if code conforms to Google Style."""
        command = 'cpplint --counting=detailed ' +\
            '--filter=-legal,-readability/todo,' +\
            '-build/include_order,-runtime/threadsafe_fn,' +\
            '-runtime/arrays' +\
            ' $( find . -name "*.h" -o -name "*.cpp" | grep -vE "^./build/" )'
        result = tools.run_command(command, cwd=self._student_task_folder)
        if result.stderr and "Total errors found" in result.stderr:
            return result
        return None

    def _run_test(self, test_node):
        if test_node[Tags.RUN_GTESTS_TAG]:
            return tools.run_command(
                CppTask.REMAKE_AND_TEST, cwd=self._cwd, timeout=60)
        input_str = ''
        if Tags.INPUT_TAG in test_node:
            input_str = test_node[Tags.INPUT_TAG]
        run_cmd = "./{binary_name} {args}".format(
            binary_name=self._binary_name, args=input_str)
        if self._pipe_through:
            run_cmd += ' ' + self._pipe_through
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
            self._output_type, test_node[Tags.EXPECTED_OUTPUT_TAG])
        if our_output != expected_output:
            run_result.stderr = OUTPUT_MISMATCH_MESSAGE.format(
                actual=our_output, input=input_str, expected=expected_output)
        return run_result


class BashTask(Task):
    """Define a Bash Task."""
    RUN_CMD = "sh {binary_name}.sh {args}"

    def __init__(self, task_node, root_folder, job_file):
        """Initialize the Task."""
        super().__init__(task_node, root_folder, job_file)

    def _build_if_needed(self):
        pass  # There is nothing to build in Bash.

    def _run_test(self, test_node):
        input_str = ''
        if Tags.INPUT_TAG in test_node:
            input_str = test_node[Tags.INPUT_TAG]
        run_cmd = BashTask.RUN_CMD.format(
            binary_name=self._binary_name, args=input_str)
        if self._pipe_through:
            run_cmd += ' ' + self._pipe_through
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
            self._output_type, test_node[Tags.EXPECTED_OUTPUT_TAG])
        if our_output != expected_output:
            run_result.stderr = OUTPUT_MISMATCH_MESSAGE.format(
                actual=our_output, input=input_str, expected=expected_output)
        return run_result
