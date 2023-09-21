import unittest
import os
import datetime
import traceback
import sys

LOG_DIR = "logs"


def run_tests(test_file, code_file):
    """
    Run the tests in the given test file against the code in code_file and return a boolean indicating success or failure.
    """
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
    log_file_path = os.path.join(LOG_DIR,
                                 f"{test_module_name}_{timestamp}.log")

    with open(log_file_path, 'w') as log_file:
        log_file.write(f"Ran {result.testsRun} tests for {test_module_name}\n")
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


if __name__ == "__main__":
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    if len(sys.argv) < 3:
        print("Usage: python test_runner.py <test_file> <code_file>")
        sys.exit(1)

    test_file_name = sys.argv[1]
    code_file_name = sys.argv[2]

    success = run_tests(test_file_name, code_file_name)
    if success:
        print(f"All tests in {test_file_name} passed!")
    else:
        print(
            f"Some tests in {test_file_name} failed. Check the logs for details."
        )
