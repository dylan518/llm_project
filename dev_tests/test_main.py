import unittest
from unittest.mock import MagicMock, patch
import sys
import os

import unittest
import os
import sys
import shutil  # Import shutil for rmtree

PROJECT_DIRECTORY = "/Users/dylanwilson/Documents/GitHub/llm_project/"

MODULE_DIRECTORIES = [
    "main", "llm_requests", "enviroment_setup_and_run", "running_tests",
    "logging"
]
for directory in MODULE_DIRECTORIES:
    sys.path.append(PROJECT_DIRECTORY + directory)
from test_validator import TestValidator
from manage_backups import BackupManager
from main import Main
from llm_request import LLMRequester
from task_manager import TaskManager
from setup_and_run import EnvironmentManager


class TestMain(unittest.TestCase):

    def setUp(self):
        self.main = Main()

    @patch('main.BackupManager')
    @patch('main.TaskManager')
    @patch('main.EnvironmentManager')
    @patch('main.TestValidator')
    def test_run(self, MockTestValidator, MockEnvironmentManager,
                 MockTaskManager, MockBackupManager):
        # Mocking the behavior of the components
        mock_backup_manager = MockBackupManager.return_value
        mock_backup_manager.get_last_good_version.return_value = "backup_1"
        mock_backup_manager.restore_directory.return_value = None

        mock_task_manager = MockTaskManager.return_value
        mock_task_manager.run_self_improvement_loop.return_value = None

        mock_test_validator = MockTestValidator.return_value
        mock_test_validator.run_tests.return_value = True

        # Running the main process
        self.main.run()

        # Assertions to check if the methods were called
        mock_backup_manager.restore_directory.assert_called()
        mock_task_manager.run_self_improvement_loop.assert_called()
        mock_test_validator.run_tests.assert_called()

        # Simulate a test failure
        mock_test_validator.run_tests.return_value = False
        self.main.run()
        mock_backup_manager.restore_directory.assert_called_with("backup_1")

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
