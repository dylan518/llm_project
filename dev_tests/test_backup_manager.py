import unittest
import os
import sys
import shutil  # Import shutil for rmtree

project_directory = "/Users/dylanwilson/Documents/GitHub/llm_project/"
module_directories = ["enviroment_setup_and_run", "running_tests", "logging"]

for dir in module_directories:
    sys.path.append(os.path.join(project_directory, dir))  # Use os.path.join

from manage_backups import BackupManager


class TestBackupManager(unittest.TestCase):

    def setUp(self):
        self.manager = BackupManager()  # Create an instance of BackupManager
        self.backup_path = None  # Initialize backup_path to None

    def test_backup_directory(self):
        self.backup_path = self.manager.backup_directory()
        self.assertTrue(os.path.exists(self.backup_path),
                        "Backup directory was not created.")

    def test_get_last_good_version(self):
        with open(self.manager.LAST_GOOD_VERSION, 'w') as file:
            file.write('some_path')

    def test_restore_directory(self):
        if not self.backup_path:
            self.backup_path = self.manager.backup_directory()

        if os.path.exists(self.manager.TARGET_DIR):  # Access through instance
            shutil.rmtree(self.manager.TARGET_DIR)  # Use shutil.rmtree

        self.manager.restore_directory(self.backup_path)

        self.assertTrue(os.path.exists(self.manager.TARGET_DIR),
                        "Target directory was not restored.")
        self.assertTrue(
            os.path.exists(
                os.path.join(self.manager.TARGET_DIR, "self_improve.py")),
            "self_improve.py not found after restore.")

    def tearDown(self):
        if self.backup_path and os.path.exists(
                self.backup_path
        ):  # Check if self.backup_path is defined and exists
            shutil.rmtree(self.backup_path)


if __name__ == "__main__":
    unittest.main()
