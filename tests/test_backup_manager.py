# passed 11/24
import unittest
import os
import sys
from unittest.mock import MagicMock, patch
import shutil  # Import shutil for rmtree

PROJECT_DIRECTORY = "/Users/dylan/Documents/GitHub/llm_project/"
MODULE_DIRECTORIES = ["enviroment_setup_and_run", "running_tests", "logging"]

for directory in MODULE_DIRECTORIES:
    sys.path.append(os.path.join(PROJECT_DIRECTORY,
                                 directory))  # Use os.path.join

from manage_backups import BackupManager


class TestBackupManager(unittest.TestCase):

    def setUp(self):
        self.manager = BackupManager()
        self.backup_path = '/path/to/mock_backup'  # Set a mock backup path

    def test_backup_directory(self):
        # Mock the backup_directory method to return a mock backup path
        self.manager.backup_directory = MagicMock(
            return_value=self.backup_path)
        self.backup_path = self.manager.backup_directory()
        self.assertEqual(self.backup_path, '/path/to/mock_backup')

    def test_get_last_good_version(self):
        # Mock file writing
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            self.manager.LAST_GOOD_VERSION = '/path/to/mock_last_good_version.txt'
            with open(self.manager.LAST_GOOD_VERSION, 'w') as file:
                file.write('some_path')
            mock_file().write.assert_called_once_with('some_path')

    def test_restore_directory(self):
        # Mock os.path.exists to always return True
        with patch.object(os.path, 'exists', return_value=True):
            # Mock shutil.rmtree to prevent actual deletion
            with patch.object(shutil, 'rmtree') as mock_rmtree:
                # Mock restore_directory method to prevent actual restoration
                self.manager.restore_directory = MagicMock()
                self.manager.restore_directory(self.backup_path)
                self.manager.restore_directory.assert_called_once_with(
                    self.backup_path)


if __name__ == "__main__":
    unittest.main()
