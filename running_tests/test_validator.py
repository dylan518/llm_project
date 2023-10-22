import unittest
import os
import datetime
import traceback
import sys

project_directory = "/Users/dylanwilson/Documents/GitHub/llm_project/"
module_directories = [
    "main", "llm_requests", "enviroment_setup_and_run", "running_tests",
    "logging"
]
for dir in module_directories:
    sys.path.append(project_directory + dir)

from manage_backups import BackupManager
from setup_and_run import EnvironmentManager


class TestValidator:

    def __init__(self):
        self.PROJECT_DIRECTORY = "/Users/dylanwilson/Documents/GitHub/llm_project/"
        self.LOG_DIR = self.PROJECT_DIRECTORY + "logs"
        self.backup_manager = BackupManager()
        self.backup_path = self.backup_manager.BACKUP_DIR
        self.env_manager = EnvironmentManager()
        self.TASK_DIR = self.PROJECT_DIRECTORY + "running_tests/tasks"

    def print_file_contents(self, file_path):
        try:
            with open(file_path, 'r') as f:
                print(f"Contents of {file_path}:\n")
                print(f.read())
                print("\n" + "=" * 80 + "\n")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    def create_blank_code_file(self, file_name):
        dir_path = os.path.join(self.PROJECT_DIRECTORY, "self_improvement")
        os.makedirs(dir_path, exist_ok=True)
        with open(os.path.join(dir_path, file_name), 'w') as f:
            f.write("")

    def update_task(self, file_name):
        task_path = os.path.join(self.TASK_DIR, file_name)
        with open(task_path, 'w') as f:
            f.write(task_path)

    def run_tests(self, test_file, code_file):
        """
        Run the tests in the given test file against the code in code_file and return a boolean indicating success or failure.
        """
        # Setup environment
        self.env_manager.setup_environment()
        self.print_file_contents(code_file)
        self.print_file_contents(test_file)

        # Add the directory containing the code_file to the system path
        sys.path.append(os.path.dirname(os.path.abspath(code_file)))

        # Dynamically import the test module
        test_module_name = os.path.splitext(test_file)[0]
        test_module = __import__(f"tests.{test_module_name}",
                                 fromlist=[test_module_name])

        # Create a test suite from the test module
        suite = unittest.TestLoader().loadTestsFromModule(test_module)

        # Create a test runner
        runner = unittest.TextTestRunner()

        # Run the tests
        result = runner.run(suite)

        # Log the results
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file_path = os.path.join(self.LOG_DIR,
                                     f"{test_module_name}_{timestamp}.log")

        with open(log_file_path, 'w') as log_file:
            log_file.write(
                f"Ran {result.testsRun} tests for {test_module_name}\n")
            log_file.write("=" * 40 + "\n")
            for error in result.errors:
                log_file.write(f"ERROR: {error[0]}\n")
                log_file.write(f"{traceback.format_tb(error[1])}\n")
                log_file.write("=" * 40 + "\n")
            for failure in result.failures:
                log_file.write(f"FAILURE: {failure[0]}\n")
                log_file.write(f"{traceback.format_tb(failure[1])}\n")
                log_file.write("=" * 40 + "\n")

        # Return a boolean indicating success or failure
        return result.wasSuccessful()

    def validate(self, test_file, code_file):
        self.create_blank_code_file(code_file)
        self.update_task(test_file)
        success = self.run_tests(test_file, code_file)
        if not success:
            backup_path = self.backup_manager.get_last_good_version()
            if self.backup_path:
                self.backup_manager.restore_directory(self.backup_path)
        else:
            self.backup_manager.backup_directory()
            self.backup_manager.set_last_good_version(self.backup_path)
        return success
