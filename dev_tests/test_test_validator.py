import unittest
from unittest.mock import patch, Mock
import os
import sys

project_directory = "/Users/dylanwilson/Documents/GitHub/llm_project/"
module_directories = [
    "main", "llm_requests", "enviroment_setup_and_run", "running_tests",
    "logging"
]
for dir in module_directories:
    sys.path.append(project_directory + dir)
from test_validator import TestValidator
from manage_backups import BackupManager


class TestTestValidator(unittest.TestCase):

    def setUp(self):
        self.validator = TestValidator()
        self.project_directory = "/Users/dylanwilson/Documents/GitHub/llm_project/"

    def test_create_blank_code_file(self):
        # Test that a blank code file is created
        self.validator.create_blank_code_file("test_file.py")
        self.assertTrue(
            os.path.exists(
                os.path.join(self.project_directory, "self_improvement",
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
            self.project_directory + "running_tests/tasks/" + "test_task.txt",
            self.project_directory + "self_improvement/" + "test_file.py")
        self.assertFalse(result)

    # ... other tests for TestValidator


if __name__ == "__main__":
    unittest.main()
