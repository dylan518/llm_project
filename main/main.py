import os

#TARGET_DIR = "self_improvement"
#REQUEST_LIMIT_FILE = os.path.join("llm_requests", "request_limit.txt")
#TASK_FILE = os.path.join(TARGET_DIR, "task.txt")
#TARGET_PATH = "target_code.py"
#BACKUP_DIR = "backup_versions"
#LAST_GOOD_VERSION = "last_good_version.txt"
#VERSION_LOG = "version_log.txt"
#LOCAL_TASK = "self_improve_task.txt"


class Main:

    def __init__(self):
        self.backup_manager = BackupManager()
        self.task_manager = TaskManager()
        self.env_manager = EnvironmentManager()
        self.test_validator = TestValidator()

    def run(self):
        # Get the list of all backups sorted by creation time (oldest first)
        all_backups = sorted(os.listdir("backup_versions"))

        for backup in all_backups:
            # Restore the backup
            self.backup_manager.restore_directory(
                os.path.join("backup_versions", backup))

            # Run the self-improvement loop
            self.task_manager.run_self_improvement_loop(time_limit=3600,
                                                        request_limit=10)

            # Test the results
            test_passed = self.test_validator.run_tests(
                "unittest0.py",
                os.path.join("self_improvement", "self_improve.py"))

            # If tests failed, restore the last good version
            if not test_passed:
                last_good_version = self.backup_manager.get_last_good_version()
                if last_good_version:
                    self.backup_manager.restore_directory(last_good_version)
                    print(
                        f"Restored to the last good version ({last_good_version}) due to test failure."
                    )
                else:
                    # If no last good version is found, restore to the very first backup
                    self.backup_manager.restore_directory(
                        os.path.join("backup_versions", all_backups[0]))
                    print(
                        "Restored to the very first backup due to test failure."
                    )


if __name__ == "__main__":
    main = Main()
    main.run()
