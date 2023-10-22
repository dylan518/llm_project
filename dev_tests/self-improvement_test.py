import unittest
import os
import sys
import shutil  # Import shutil for rmtree

project_directory = "/Users/dylanwilson/Documents/GitHub/llm_project/"
module_directories = [
    "enviroment_setup_and_run", "running_tests", "logging", "self_improvement"
]

for dir in module_directories:
    sys.path.append(os.path.join(project_directory, dir))  # Use os.path.join
import unittest
from unittest import mock
from self_improver import (read_file, get_task, get_target_file,
                           extract_python_code, extract_function_definitions,
                           update_code, backup_code, restore_code,
                           parse_AI_response_and_update, shorten_messages)


class TestSelfImprover(unittest.TestCase):

    def test_read_file(self):
        # Test reading a file that exists
        with open('test_file.txt', 'w') as f:
            f.write('Hello, world!')
        self.assertEqual(read_file('test_file.txt'), 'Hello, world!')

        # Test reading a file that doesn't exist
        self.assertIsNone(read_file('non_existent_file.txt'))

    def test_get_task(self):
        with mock.patch('self_improver.read_file') as mocked_read_file:
            get_task()
            mocked_read_file.assert_called_with('task.txt')

    def test_get_target_file(self):
        with mock.patch('self_improver.read_file') as mocked_read_file:
            get_target_file()
            mocked_read_file.assert_called_with('target_file.txt')

    def test_extract_python_code(self):
        gpt_output = "Here's some code:\n'''python\ndef function(x, y):\n    pass\n'''"
        self.assertEqual(extract_python_code(gpt_output),
                         ["def function(x, y):\n    pass"])

    def test_extract_function_definitions(self):
        code = "'''python\ndef foo():\n    print('foo')\ndef bar():\n    print('bar')\n'''"
        self.assertEqual(
            extract_function_definitions(code),
            ["def foo():\n    print('foo')", "def bar():\n    print('bar')"])

    # Add more tests for other functions as needed


if __name__ == '__main__':
    unittest.main()