import unittest
import os
import datetime
import traceback
import sys
import tempfile
import subprocess

PROJECT_DIRECTORY = os.sep.join(
    os.path.abspath(__file__).split(os.sep)
    [:next((i for i, p in enumerate(os.path.abspath(__file__).split(os.sep))
            if 'llm_project' in p), None) +
     1]) if 'llm_project' in os.path.abspath(__file__) else None

MODULE_DIRECTORIES = [
    "main",
    "enviroment_setup_and_run",
    "running_tests",
]
for directory in MODULE_DIRECTORIES:
    sys.path.append(os.path.join(PROJECT_DIRECTORY, directory))

from manage_backups import BackupManager
from setup_and_run import EnvironmentManager


class TestValidator:

    def __init__(self):
        self.PROJECT_DIRECTORY = os.sep.join(
            os.path.abspath(__file__).split(os.sep)
            [:next((
                i
                for i, p in enumerate(os.path.abspath(__file__).split(os.sep))
                if 'llm_project' in p), None) +
             1]) if 'llm_project' in os.path.abspath(__file__) else None
        self.LOG_DIR = self.PROJECT_DIRECTORY + "logs"
        self.backup_manager = BackupManager()
        self.backup_path = self.backup_manager.BACKUP_DIR
        self.env_manager = EnvironmentManager()
        self.TASK_DIR = os.path.join(self.PROJECT_DIRECTORY,
                                     "running_tests/tasks")
        os.makedirs(self.LOG_DIR, exist_ok=True)

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
        try:
            # Create a temporary file
            temp_dir = tempfile.mkdtemp(dir=self.PROJECT_DIRECTORY)
            temp_file_path = os.path.join(temp_dir, 'temp_test_file.py')
            with open(temp_file_path, 'w') as temp_file:
                # Write the contents of code_file and test_file to temp_file
                with open(code_file, 'r') as cf, open(test_file, 'r') as tf:
                    temp_file.write(cf.read() + '\n' + tf.read())

            # Run the tests using the temporary file
            result = subprocess.run([sys.executable, temp_file_path],
                                    capture_output=True,
                                    text=True)

        except:
            print("error running test script")
        # Log the results
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file_name = f"test_results_{timestamp}.log"
        log_file_path = os.path.join(self.LOG_DIR, log_file_name)

        with open(log_file_path, 'w') as log_file:
            log_file.write(result.stdout)
            if result.stderr:
                log_file.write("\n" + "ERRORS:" + "\n" + "=" * 40 + "\n")
                log_file.write(result.stderr)

        # Return a boolean indicating success or failure based on the return code
        return result.returncode == 0

    def validate(self, test_file, code_file):
        success = self.run_tests(test_file, code_file)
        if not success:
            print("failed")
            self.backup_path = self.backup_manager.get_last_good_version()
            if self.backup_path:
                self.backup_manager.restore_directory()
        else:
            print("success")
            self.backup_manager.backup_directory()
            self.backup_manager.set_last_good_version(self.backup_path)
            return success
