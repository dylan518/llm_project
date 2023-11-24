import os
import shutil
import datetime


class BackupManager:

    def __init__(self, target_dir="self_improvement"):
        self.PROJECT_DIRECTORY = "/Users/dylanwilson/Documents/GitHub/llm_project"
        self.BACKUP_DIR = os.path.join(self.PROJECT_DIRECTORY,
                                       "backup_versions")
        self.LAST_GOOD_VERSION = os.path.join(self.PROJECT_DIRECTORY,
                                              "last_good_version.txt")
        self.TARGET_DIR = os.path.join(self.PROJECT_DIRECTORY, target_dir)

        if not os.path.exists(self.BACKUP_DIR):
            os.makedirs(self.BACKUP_DIR)

    def backup_directory(self):
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(self.BACKUP_DIR,
                                   f"self_improvement_{timestamp}")
        shutil.copytree(self.TARGET_DIR, backup_path)
        init_file_path = os.path.join(backup_path, '__init__.py')
        if not os.path.exists(init_file_path):
            with open(init_file_path, 'w') as init_file:
                pass  # Create an empty __init__.py file
        return backup_path

    def restore_directory(self):
        backup_to_restore = self.get_most_recent_version(
        )  # or get_last_good_version
        if not backup_to_restore:
            print("No backup available to restore.")
            return

        if os.path.exists(self.TARGET_DIR):
            shutil.rmtree(self.TARGET_DIR)

        shutil.copytree(backup_to_restore, self.TARGET_DIR)

    def get_last_good_version(self):
        if os.path.exists(self.LAST_GOOD_VERSION):
            with open(self.LAST_GOOD_VERSION, 'r') as file:
                return file.read().strip()
        return None

    def set_last_good_version(self, backup_path):
        with open(self.LAST_GOOD_VERSION, 'w') as file:
            file.write(backup_path)

    def get_most_recent_version(self):
        backups = sorted(os.listdir(self.BACKUP_DIR), reverse=True)
        if backups:
            return os.path.join(self.BACKUP_DIR, backups[0])
        return None