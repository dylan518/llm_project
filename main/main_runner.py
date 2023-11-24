import os
import unittest
import sys
import shutil  # Import shutil for rmtree

PROJECT_DIRECTORY = "/Users/dylanwilson/Documents/GitHub/llm_project/"
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
        print("TestValidator initialized:",
              isinstance(self.test_validator, TestValidator))
        self.back_up_dir = self.backup_manager.BACKUP_DIR
        self.PROJECT_DIRECTORY = "/Users/dylanwilson/Documents/GitHub/llm_project"
        print(self.back_up_dir)

    def run(self):
        # Get the list of all backups sorted by creation time (oldest first)
        self.backup_manager.backup_directory()
        #set self_improve.txt to task.txt
        #set traget file as project direct /self_improvement/self_improve.py
        # Run the self-improvement loop
        #        self.task_manager.run_self_improvement_loop(time_limit=3600,
        #                                                    request_limit=20)
        #read test instruction to test_task
        task_file_path = self.PROJECT_DIRECTORY + "/running_tests/tasks/test_task0.txt"
        print(task_file_path)
        with open(task_file_path, 'r') as task_file:
            test_task = task_file.read()

        self.task_manager.update_task(test_task)

        self.task_manager.set_target_file(self.PROJECT_DIRECTORY +
                                          "/self_improvement/test_file.py")

        #have self improvement loop complete test task
        self.task_manager.run_self_improvement_loop(time_limit=3600,
                                                    request_limit=3)
        # Test the results
        test_passed = self.test_validator.validate(
            self.PROJECT_DIRECTORY + "/running_tests/unittests/unittest0.py",
            self.PROJECT_DIRECTORY + "/self_improvement/test_file.py")


if __name__ == "__main__":
    main = Main()
    main.run()
