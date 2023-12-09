import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Assuming your project directory and module directories are correctly set up
PROJECT_DIRECTORY = os.sep.join(
    os.path.abspath(__file__).split(os.sep)
    [:next((i for i, p in enumerate(os.path.abspath(__file__).split(os.sep))
            if 'llm_project' in p), None) +
     1]) if 'llm_project' in os.path.abspath(__file__) else None

MODULE_DIRECTORIES = [
    "enviroment_setup_and_run", "running_tests", "logging", "main"
]
for directory in MODULE_DIRECTORIES:
    sys.path.append(os.path.join(PROJECT_DIRECTORY, directory))

from main_runner import Main
from manage_backups import BackupManager
from test_validator import TestValidator
from manage_backups import BackupManager
from llm_request import LLMRequester
from task_manager import TaskManager
from setup_and_run import EnvironmentManager

if __name__ == '__main__':
    main = Main()
    main.run()
