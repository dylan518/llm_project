import os
import sys
import unittest
from unittest.mock import patch, mock_open

project_directory = "/Users/dylanwilson/Documents/GitHub/llm_project/"
module_directories = [
    "main", "llm_requests", "enviroment_setup_and_run", "running_tests",
    "logging"
]

for dir in module_directories:
    sys.path.append(project_directory + dir)

from task_manager import TaskManager
from setup_and_run import EnvironmentManager

os.chdir(project_directory)


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
        """Test the set_target_file method."""
        target = "target.py"
        with patch("builtins.open", mock_open()) as mock_file:
            self.manager.set_target_file(target)
            mock_file.assert_called_once_with(self.manager.target_file_path,
                                              'w')
            mock_file().write.assert_called_once_with(target)

    @patch("setup_and_run.EnvironmentManager")
    def test_run_self_improvement_loop(self, MockEnvironmentManager):
        """Test the run_self_improvement_loop method."""
        self.manager.run_self_improvement_loop()
        MockEnvironmentManager.assert_called_once()
        MockEnvironmentManager().setup_and_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
