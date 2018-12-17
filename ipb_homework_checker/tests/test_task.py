#!/usr/bin/python3
"""Test the checker."""

import unittest
from os import path


from ipb_homework_checker.checker import Checker
from ipb_homework_checker.tasks import Task
from ipb_homework_checker.schema_tags import Tags


class TestTask(unittest.TestCase):
    """Test the checker."""

    def test_injecting_new(self):
        """Check that we can inject folders that are now present yet."""
        self.maxDiff = None

        checker = Checker(
            'ipb_homework_checker/tests/data/dummy/dummy_solution/solution.yml')
        homework_node = checker._base_node[Tags.HOMEWORKS_TAG][0]
        current_folder = path.join(
            checker._checked_code_folder, homework_node[Tags.FOLDER_TAG])
        task_node = homework_node[Tags.TASKS_TAG][0]
        task = Task.from_yaml_node(task_node=task_node,
                                   student_hw_folder=current_folder,
                                   job_file=checker._job_file_path)
        self.assertTrue(path.exists(task._student_task_folder))
        folder_to_inject = 'blah'
        task._inject_folder(folder_to_inject, folder_to_inject)
        self.assertTrue(path.isdir(task._backup_folder))
        self.assertTrue(path.exists(
            path.join(task._student_task_folder, folder_to_inject, 'blah.cpp')))
        task._revert_injections(folder_to_inject)
        self.assertFalse(path.isdir(
            path.join(task._backup_folder, folder_to_inject)))
        self.assertFalse(path.exists(
            path.join(task._backup_folder, folder_to_inject, 'blah.cpp')))

    def test_injecting_existing(self):
        """Check that we can inject folders that are now present yet."""
        self.maxDiff = None

        checker = Checker(
            'ipb_homework_checker/tests/data/dummy/dummy_solution/solution.yml')
        homework_node = checker._base_node[Tags.HOMEWORKS_TAG][0]
        current_folder = path.join(
            checker._checked_code_folder, homework_node[Tags.FOLDER_TAG])
        task_node = homework_node[Tags.TASKS_TAG][0]
        task = Task.from_yaml_node(task_node=task_node,
                                   student_hw_folder=current_folder,
                                   job_file=checker._job_file_path)
        self.assertTrue(path.exists(task._student_task_folder))
        folder_to_inject = 'tests'
        task._inject_folder(folder_to_inject, folder_to_inject)
        self.assertTrue(path.isdir(task._backup_folder))
        self.assertTrue(path.exists(path.join(task._student_task_folder,
                                              folder_to_inject,
                                              'CMakeLists.txt')))
        self.assertTrue(path.exists(path.join(task._student_task_folder,
                                              folder_to_inject,
                                              'test_dummy.cpp')))
        task._revert_injections(folder_to_inject)
        self.assertFalse(path.isdir(
            path.join(task._backup_folder, folder_to_inject)))
        self.assertFalse(path.exists(path.join(task._backup_folder,
                                               folder_to_inject,
                                               'CMakeLists.txt')))
        self.assertFalse(path.exists(path.join(task._backup_folder,
                                               folder_to_inject,
                                               'test_dummy.cpp')))
