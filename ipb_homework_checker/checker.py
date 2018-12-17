"""Check the homework."""

from os import path

import logging
from datetime import datetime

from . import tools
from .schema_manager import SchemaManager
from .schema_tags import Tags
from .tasks import Task


log = logging.getLogger("GHC")


class Checker:
    """Check homework."""
    TESTS_TAG = 'tests'

    def __init__(self, job_file_path):
        """Initialize the checker from file."""
        self._job_file_path = tools.expand_if_needed(job_file_path)
        schema_manager = SchemaManager(self._job_file_path)
        self._base_node = schema_manager.validated_yaml
        self._checked_code_folder = tools.expand_if_needed(
            self._base_node[Tags.FOLDER_TAG])
        # The results of all tests will be kept here.
        self._results = {}

    def check_homework(self):
        """Run over all Tasks in all homeworks."""
        results = {}
        for homework_node in self._base_node[Tags.HOMEWORKS_TAG]:
            current_folder = path.join(
                self._checked_code_folder, homework_node[Tags.FOLDER_TAG])
            if not path.exists(current_folder):
                log.warning("Folder '%s' does not exist. Skiping.",
                            current_folder)
                continue
            hw_name = homework_node[Tags.NAME_TAG]
            results[hw_name] = {}
            deadline_str = homework_node[Tags.DEADLINE_TAG]
            deadline_datetime = datetime.strptime(deadline_str,
                                                  tools.DATE_PATTERN)
            if datetime.now() > deadline_datetime:
                results[hw_name][tools.EXPIRED_TAG] = True
            for task_node in homework_node[Tags.TASKS_TAG]:
                task = Task.from_yaml_node(task_node=task_node,
                                           student_hw_folder=current_folder,
                                           job_file=self._job_file_path)
                if not task:
                    continue
                results[hw_name][task.name] = task.check_all_tests()

        return results
