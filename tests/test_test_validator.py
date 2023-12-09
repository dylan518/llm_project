# passed 11/24
import unittest
from unittest.mock import patch, Mock
import os
import sys

PROJECT_DIRECTORY = os.sep.join(
    os.path.abspath(__file__).split(os.sep)
    [:next((i for i, p in enumerate(os.path.abspath(__file__).split(os.sep))
            if 'llm_project' in p), None) +
     1]) if 'llm_project' in os.path.abspath(__file__) else None

MODULE_DIRECTORIES = [
    "main", "llm_requests", "enviroment_setup_and_run", "running_tests",
    "logging"
]
for directory in MODULE_DIRECTORIES:
    sys.path.append(PROJECT_DIRECTORY + directory)
from test_validator import TestValidator
from manage_backups import BackupManager


class TestTestValidator(unittest.TestCase):

    def setUp(self):
        self.validator = TestValidator()
        self.PROJECT_DIRECTORY = os.sep.join(
            os.path.abspath(__file__).split(os.sep)
            [:next((
                i
                for i, p in enumerate(os.path.abspath(__file__).split(os.sep))
                if 'llm_project' in p), None) +
             1]) if 'llm_project' in os.path.abspath(__file__) else None

    def test_create_blank_code_file(self):
        # Test that a blank code file is created
        self.validator.create_blank_code_file("test_file.py")
        self.assertTrue(
            os.path.exists(
                os.path.join(self.PROJECT_DIRECTORY, "self_improvement",
                             "test_file.py")))

    def test_update_task(self):
        # Test that the task is updated
        self.validator.update_task("test_task.txt")
        with open(os.path.join(self.validator.TASK_DIR, "test_task.txt"),
                  'r') as f:
            content = f.read()
        self.assertEqual(
            content, os.path.join(self.validator.TASK_DIR, "test_task.txt"))

    @patch.object(TestValidator, 'run_tests', return_value=True)
    @patch.object(TestValidator, 'create_blank_code_file')
    @patch.object(TestValidator, 'update_task')
    def test_validate_success(self, mock_update_task,
                              mock_create_blank_code_file, mock_run_tests):
        # Test the validate method when run_tests returns True
        result = self.validator.validate("test_task.txt", "test_file.py")
        self.assertTrue(result)

    @patch.object(TestValidator, 'run_tests', return_value=False)
    @patch.object(TestValidator, 'create_blank_code_file')
    @patch.object(TestValidator, 'update_task')
    @patch.object(BackupManager,
                  'backup_directory',
                  return_value='fake_backup_path')
    @patch.object(BackupManager, 'restore_directory')
    @patch.object(BackupManager,
                  'get_last_good_version',
                  return_value='fake_backup_path')
    @patch.object(BackupManager, 'set_last_good_version')
    def test_validate_failure(self, mock_set_last_good_version,
                              mock_get_last_good_version,
                              mock_restore_directory, mock_backup_directory,
                              mock_update_task, mock_create_blank_code_file,
                              mock_run_tests):
        # Test the validate method when run_tests returns False
        result = self.validator.validate(
            self.PROJECT_DIRECTORY + "running_tests/tasks/" + "test_task.txt",
            self.PROJECT_DIRECTORY + "self_improvement/" + "test_file.py")
        self.assertFalse(result)

    # ... other tests for TestValidator


if __name__ == "__main__":
    unittest.main()
