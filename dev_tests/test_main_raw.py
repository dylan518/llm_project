"""run main to test raw without any mocks"""

import sys

PROJECT_DIRECTORY = "/Users/dylanwilson/Documents/GitHub/llm_project/"

MODULE_DIRECTORIES = [
    "main", "llm_requests", "enviroment_setup_and_run", "running_tests",
    "logging"
]
for directory in MODULE_DIRECTORIES:
    sys.path.append(PROJECT_DIRECTORY + directory)

from main import Main

main = Main()
main.run()
