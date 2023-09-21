import os
import subprocess
import sys

# Mock requirements and imports
MOCK_REQUIREMENTS = """
numpy
pandas
requests
"""

MOCK_IMPORTS = """
import numpy
import pandas
import requests
"""

MOCK_CODE = """
print("code.py executed successfully!")
"""

# Paths
TEST_REQUIREMENTS_FILE = "test_requirements.txt"
TEST_IMPORTS_FILE = "test_import.txt"
ENV_NAME = "myenv"
CODE_FILE = "code.py"


def create_mock_files():
    with open(TEST_REQUIREMENTS_FILE, 'w') as f:
        f.write(MOCK_REQUIREMENTS)

    with open(TEST_IMPORTS_FILE, 'w') as f:
        f.write(MOCK_IMPORTS)

    with open(CODE_FILE, 'w') as f:
        f.write(MOCK_CODE)


def run_setup_script():
    result = subprocess.run(
        [sys.executable, "setup_environment.py", CODE_FILE],
        capture_output=True,
        text=True)
    # Return both stdout and stderr for better debugging
    return result.stdout + "\n" + result.stderr


def test_environment():
    # Check if environment directory exists
    assert os.path.exists(ENV_NAME), f"{ENV_NAME} was not created."

    # Check if test_requirements.txt and test_import.txt were processed
    assert os.path.exists(
        TEST_REQUIREMENTS_FILE), f"{TEST_REQUIREMENTS_FILE} does not exist."
    assert os.path.exists(
        TEST_IMPORTS_FILE), f"{TEST_IMPORTS_FILE} does not exist."

    # Check if code.py was executed successfully
    output = run_setup_script()
    print(f"Output from run_setup_script: {output}")
    assert "code.py executed successfully!" in output, "code.py was not executed or did not produce expected output."

    print("All tests passed!")


def main():
    create_mock_files()
    test_environment()


if __name__ == "__main__":
    main()
