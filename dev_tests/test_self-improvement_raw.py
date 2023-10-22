import unittest
from unittest.mock import MagicMock, patch
import sys
import os

import unittest
import os
import sys
import shutil  # Import shutil for rmtree

project_directory = "/Users/dylanwilson/Documents/GitHub/llm_project/"

module_directories = [
    "main", "llm_requests", "enviroment_setup_and_run", "running_tests",
    "logging"
]
for dir in module_directories:
    sys.path.append(project_directory + dir)
from test_validator import TestValidator
from manage_backups import BackupManager
from main import Main
from llm_request import LLMRequester
from task_manager import TaskManager
from setup_and_run import EnvironmentManager

validator = TestValidator()
result = validator.validate(
    project_director + "running_tests/tasks/" + "test_task.txt",
    "code_file_name.py")
print("Test Passed" if result else "Test Failed")
