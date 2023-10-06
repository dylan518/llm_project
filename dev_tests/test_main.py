import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Get the directory containing the current test file.
current_directory = os.path.dirname(os.path.abspath(__file__))

# Compute the path to the directory containing the modules.
# Adjust the path based on the test file's needs.
module_directory = os.path.join(current_directory, '..', 'main')

# Append this path to sys.path.
sys.path.append(module_directory)


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
