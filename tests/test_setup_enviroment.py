# passed 11/24
import os
import subprocess
import sys
import shutil
import unittest

PROJECT_DIRECTORY = "/Users/dylan/Documents/GitHub/llm_project/"
MODULE_DIRECTORIES = [
    "main", "llm_requests", "enviroment_setup_and_run", "running_tests",
    "logging"
]

for directory in MODULE_DIRECTORIES:
    sys.path.append(PROJECT_DIRECTORY + directory)

from task_manager import TaskManager
from setup_and_run import EnvironmentManager

os.chdir(PROJECT_DIRECTORY)


class TestEnvironmentManager(unittest.TestCase):

    def setUp(self):
        self.manager = EnvironmentManager()

    def test_create_virtual_env(self):
        self.manager.create_virtual_env()
        self.assertTrue(os.path.exists(self.manager.ENV_NAME))

    def test_install_missing_packages(self):
        # Assuming 'requests' is in your requirements.txt
        self.manager.install_missing_packages(['requests'])
        installed_packages = self.manager.get_installed_packages()
        self.assertIn('requests', installed_packages)

    def test_setup_environment(self):
        self.manager.setup_environment()
        installed_packages = self.manager.get_installed_packages()
        required_packages = self.manager.get_required_packages()
        for package in required_packages:
            self.assertIn(package, installed_packages)

    def test_execute_imports(self):
        # Assuming 'import os' is in your import.txt
        self.manager.execute_imports()
        # If no exception is raised, the test will pass

    def test_run_script(self):
        # Create a simple script for testing
        with open('test_script.py', 'w') as f:
            f.write("print('Hello from test_script')")

        self.manager.run_script('test_script.py')
        output = self.manager.get_output('test_script.py')
        self.assertEqual(output.strip(), 'Hello from test_script')

    def tearDown(self):
        # Clean up any files or directories created during testing
        if os.path.exists('test_script.py'):
            os.remove('test_script.py')


#        if os.path.exists(self.manager.ENV_NAME):
#            shutil.rmtree(self.manager.ENV_NAME
#                          )  # Note: This will only remove an empty directory

if __name__ == "__main__":
    unittest.main()
