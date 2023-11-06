import unittest
from unittest.mock import MagicMock, patch
import sys
import os

import unittest
import os
import sys
import shutil  # Import shutil for rmtree

PROJECT_DIRECTORY = "/Users/dylanwilson/Documents/GitHub/llm_project/"

MODULE_DIRECTORIES = [
    "main", "llm_requests", "enviroment_setup_and_run", "running_tests",
    "logging"
]
for directory in MODULE_DIRECTORIES:
    sys.path.append(PROJECT_DIRECTORY + directory)
from test_validator import TestValidator
from manage_backups import BackupManager
from main import Main
from llm_request import LLMRequester
from task_manager import TaskManager
from setup_and_run import EnvironmentManager

main = Main()
main.run()
