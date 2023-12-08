#passed 11/24
import os
import sys
import unittest
from unittest.mock import patch, mock_open

PROJECT_DIRECTORY = "/Users/dylan/Documents/GitHub/llm_project/"
MODULE_DIRECTORIES = [
    "main", "llm_requests", "enviroment_setup_and_run", "running_tests",
    "logging"
]

for directory in MODULE_DIRECTORIES:
    sys.path.append(os.path.join(PROJECT_DIRECTORY, directory))

from task_manager import TaskManager
from setup_and_run import EnvironmentManager

#os.chdir(PROJECT_DIRECTORY)


class TestTaskManager(unittest.TestCase):

    def setUp(self):
        """Set up testing environment before each test."""
        self.manager = TaskManager()

    def test_load_task(self):
        """Test the load_task method."""
        mock_file_content = "Sample Task"
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            result = self.manager.load_task()
            self.assertEqual(result, mock_file_content, "Failed to load task.")

    def test_update_task(self):
        """Test the update_task method."""
        new_task = "New Task"
        with patch("builtins.open", mock_open()) as mock_file:
            self.manager.update_task(new_task)
            mock_file.assert_called_once_with(self.manager.task_file_path, 'w')
            mock_file().write.assert_called_once_with(new_task)

    def test_get_current_task(self):
        """Test the get_current_task method."""
        mock_file_content = "Sample Task"
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            result = self.manager.get_current_task()
            self.assertEqual(result, mock_file_content,
                             "Failed to get current task.")

    def test_set_target_file(self):
        target = "target.py"
        expected_file_path = '/Users/dylan/Documents/GitHub/llm_project/self_improvement/target_file.txt'
        with patch("builtins.open", mock_open()) as mock_file:
            self.manager.set_target_file(target)
            mock_file.assert_called_once_with(expected_file_path, 'w')
            mock_file().write.assert_called_once_with(target)

    def test_run_self_improvement_loop(self):
        """Test the run_self_improvement_loop method."""
        with unittest.mock.patch(
                'task_manager.EnvironmentManager') as MockEnvironmentManager:
            self.manager.run_self_improvement_loop()
            MockEnvironmentManager.assert_called_once()
            MockEnvironmentManager().setup_and_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
