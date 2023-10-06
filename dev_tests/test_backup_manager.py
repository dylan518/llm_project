import unittest
import os
import sys

# Get the directory containing the current test file.
current_directory = os.path.dirname(os.path.abspath(__file__))

# Compute the path to the directory containing the modules.
# Adjust the path based on the test file's needs.
module_directory = os.path.join(current_directory, '..', 'running_tests')

# Append this path to sys.path.
sys.path.append(module_directory)


class TestBackupManager(unittest.TestCase):

    def setUp(self):
        self.manager = BackupManager()
        self.backup_path = None

    def test_backup_directory(self):
        # Backup the directory and get the backup path
        self.backup_path = self.manager.backup_directory()

        # Check if the backup directory exists
        self.assertTrue(os.path.exists(self.backup_path),
                        "Backup directory does not exist.")

        # Check if the backup directory has the expected structure (you can expand on this)
        self.assertTrue(
            os.path.exists(os.path.join(self.backup_path, "self_improve.py")),
            "self_improve.py not found in backup.")

    def test_restore_directory(self):
        # For this test, we assume that the backup_directory test has passed and we have a valid backup_path
        if not self.backup_path:
            self.backup_path = self.manager.backup_directory()

        # Delete the current directory to simulate a failure
        if os.path.exists(BackupManager.TARGET_DIR):
            os.rmdir(BackupManager.TARGET_DIR)

        # Restore the directory
        self.manager.restore_directory(self.backup_path)

        # Check if the directory was restored correctly
        self.assertTrue(os.path.exists(BackupManager.TARGET_DIR),
                        "Target directory was not restored.")
        self.assertTrue(
            os.path.exists(
                os.path.join(BackupManager.TARGET_DIR, "self_improve.py")),
            "self_improve.py not found after restore.")

    def test_set_last_good_version(self):
        # Set the last good version
        self.manager.set_last_good_version("test_version_path")

        # Check if the last good version was set correctly
        with open(BackupManager.LAST_GOOD_VERSION, 'r') as file:
            last_good_version = file.read().strip()
        self.assertEqual(last_good_version, "test_version_path",
                         "Last good version was not set correctly.")

    def test_get_last_good_version(self):
        # Set a known last good version
        with open(BackupManager.LAST_GOOD_VERSION, 'w') as file:
            file.write("test_version_path")

        # Get the last good version and check if it matches
        last_good_version = self.manager.get_last_good_version()
        self.assertEqual(last_good_version, "test_version_path",
                         "Retrieved last good version does not match.")

    def tearDown(self):
        # Cleanup any created files or directories
        if self.backup_path and os.path.exists(self.backup_path):
            os.rmdir(self.backup_path)


if __name__ == "__main__":
    unittest.main()
