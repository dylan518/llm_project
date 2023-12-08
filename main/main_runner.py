import os
import unittest
import sys
import shutil  # Import shutil for rmtree

PROJECT_DIRECTORY = "/Users/dylan/Documents/GitHub/llm_project/"
MODULE_DIRECTORIES = ["enviroment_setup_and_run", "running_tests", "logging"]

for directory in MODULE_DIRECTORIES:
    sys.path.append(os.path.join(PROJECT_DIRECTORY,
                                 directory))  # Use os.path.join

from manage_backups import BackupManager
from test_validator import TestValidator
from manage_backups import BackupManager
from llm_request import LLMRequester
from task_manager import TaskManager
from setup_and_run import EnvironmentManager


class Main:

    def __init__(self):
        self.backup_manager = BackupManager()
        self.task_manager = TaskManager()
        self.env_manager = EnvironmentManager()
        self.test_validator = TestValidator()
        self.back_up_dir = self.backup_manager.BACKUP_DIR
        self.PROJECT_DIRECTORY = "/Users/dylan/Documents/GitHub/llm_project"
        print(self.back_up_dir)

    def run(self):
        #set self_improve_task.txt to task.txt
        task_file_path = self.PROJECT_DIRECTORY + "/main/self_improve_task.txt"
        print(task_file_path)
        with open(task_file_path, 'r') as task_file:
            improve_task = task_file.read()

        self.task_manager.update_task(improve_task)

        #set traget file as project direct /self_improvement/self_improve.py
        self.task_manager.set_target_file(self.PROJECT_DIRECTORY +
                                          "/self_improvement/self_improve.py")
        # Run the self-improvement loop
        self.task_manager.run_self_improvement_loop(time_limit=3600,
                                                    request_limit=20)
        #read test instruction to test_task
        task_file_path = self.PROJECT_DIRECTORY + "/running_tests/tasks/test_task0.txt"
        print(task_file_path)
        with open(task_file_path, 'r') as task_file:
            test_task = task_file.read()

        self.task_manager.update_task(test_task)

        test_file_path = os.path.join(self.PROJECT_DIRECTORY,
                                      "self_improvement", "test_file.py")
        with open(test_file_path, 'w') as test_file:
            pass
        self.task_manager.set_target_file(test_file_path)

        #have self improvement loop complete test task
        self.task_manager.run_self_improvement_loop(time_limit=3600,
                                                    request_limit=3)
        # Test the results
        test_passed = self.test_validator.validate(
            self.PROJECT_DIRECTORY + "/running_tests/unittests/unittest0.py",
            self.PROJECT_DIRECTORY + "/self_improvement/test_file.py")

    def only_test(self):
        task_file_path = self.PROJECT_DIRECTORY + "/running_tests/tasks/test_task0.txt"
        print(task_file_path)
        with open(task_file_path, 'r') as task_file:
            test_task = task_file.read()

        self.task_manager.update_task(test_task)

        test_file_path = os.path.join(self.PROJECT_DIRECTORY,
                                      "self_improvement", "test_file.py")
        with open(test_file_path, 'w') as test_file:
            pass
        self.task_manager.set_target_file(test_file_path)

        #have self improvement loop complete test task
        self.task_manager.run_self_improvement_loop(time_limit=3600,
                                                    request_limit=3)
        # Test the results
        test_passed = self.test_validator.validate(
            self.PROJECT_DIRECTORY + "/running_tests/unittests/unittest0.py",
            self.PROJECT_DIRECTORY + "/self_improvement/test_file.py")

    def safe_test(self):
        backup_manager = BackupManager()
        backup_path = backup_manager.backup_directory()
        try:
            task_file_path = self.PROJECT_DIRECTORY + "/running_tests/tasks/test_task0.txt"
            print(task_file_path)
            with open(task_file_path, 'r') as task_file:
                test_task = task_file.read()

            self.task_manager.update_task(test_task)

            test_file_path = os.path.join(self.PROJECT_DIRECTORY,
                                          "self_improvement", "test_file.py")
            with open(test_file_path, 'w') as test_file:
                pass
            self.task_manager.set_target_file(test_file_path)

            #have self improvement loop complete test task
            self.task_manager.run_self_improvement_loop(time_limit=3600,
                                                        request_limit=3)
            # Test the results
            test_passed = self.test_validator.validate(
                self.PROJECT_DIRECTORY +
                "/running_tests/unittests/unittest0.py",
                self.PROJECT_DIRECTORY + "/self_improvement/test_file.py")
            if not test_passed:
                print(
                    "Test failed. Consider restoring from backup if necessary."
                )
                # Optionally restore the backup
                # backup_manager.restore_directory()
            else:
                backup_manager.set_last_good_version(backup_path)
                print("Test passed.")

        except Exception as e:
            print(f"An error occurred during the test: {e}")


if __name__ == "__main__":
    main = Main()
    main.run()
