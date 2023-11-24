"""
test for self improvement
"""
import sys
import os
import unittest
from unittest import mock

PROJECT_DIRECTORY = "/Users/dylanwilson/Documents/GitHub/llm_project/"
MODULE_DIRECTORIES = [
    "enviroment_setup_and_run", "running_tests", "logging", "self_improvement"
]

for directory in MODULE_DIRECTORIES:
    sys.path.append(os.path.join(PROJECT_DIRECTORY,
                                 directory))  # Use os.path.join

from self_improve import (read_file, get_task, get_target_file,
                          extract_python_code, extract_function_definitions,
                          update_code, backup_code, restore_code,
                          parse_AI_response_and_update,
                          shorten_messages)  #pylint


class TestSelfImprover(unittest.TestCase):

    def test_read_file(self):
        # Mocking the open built-in to return a specific string when read
        with mock.patch('builtins.open',
                        mock.mock_open(read_data='Hello, world!')) as m:
            self.assertEqual(read_file('test_file.txt'), 'Hello, world!')

        # Mocking os.path.exists to return False
        with mock.patch('os.path.exists', return_value=False) as m:
            self.assertIsNone(read_file('non_existent_file.txt'))

    def test_get_task(self):
        # Mocking the read_file function to return a specific string
        with mock.patch('self_improve.read_file',
                        return_value='Test task') as mocked_read_file:
            self.assertEqual(get_task(), 'Test task')
            mocked_read_file.assert_called_with('task.txt')

    def test_get_target_file(self):
        # Mocking the read_file function to return a specific string
        with mock.patch('self_improve.read_file',
                        return_value='Test target file') as mocked_read_file:
            self.assertEqual(get_target_file(), 'Test target file')
            mocked_read_file.assert_called_with(
                '/Users/dylanwilson/Documents/GitHub/llm_project/self_improvement/task.txt'
            )

    def test_extract_python_code(self):
        gpt_output = "Here's some code:\n```python\ndef function(x, y):\n    pass\n```"
        self.assertEqual(extract_python_code(gpt_output),
                         ["def function(x, y):\n    pass"])

    def test_extract_function_definitions(self):
        code = "```python\ndef foo():\n    print('foo')\ndef bar():\n    print('bar')\n```"
        code = extract_python_code(code)
        self.assertEqual(
            extract_function_definitions(code[0]),
            ["def foo():\n    print('foo')", "def bar():\n    print('bar')"])


if __name__ == '__main__':
    unittest.main()