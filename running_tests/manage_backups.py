import os
import shutil
import datetime


class BackupManager:

    def __init__(self, target_dir="self_improvement"):
        self.BACKUP_DIR = "backup_versions"
        self.LAST_GOOD_VERSION = "last_good_version.txt"
        self.TARGET_DIR = target_dir

        if not os.path.exists(self.BACKUP_DIR):
            os.makedirs(self.BACKUP_DIR)

    def backup_directory(self):
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(self.BACKUP_DIR,
                                   f"self_improvement_{timestamp}")
        shutil.copytree(self.TARGET_DIR, backup_path)
        return backup_path

    def restore_directory(self, backup_path):
        if os.path.exists(self.TARGET_DIR):
            shutil.rmtree(self.TARGET_DIR)
        shutil.copytree(backup_path, self.TARGET_DIR)

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
