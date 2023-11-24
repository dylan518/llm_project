import unittest
from unittest import mock
import os
import sys

PROJECT_DIRECTORY = "/Users/dylanwilson/Documents/GitHub/llm_project/"
MODULE_DIRECTORIES = ["self_improvement"]

for directory in MODULE_DIRECTORIES:
    sys.path.append(os.path.join(PROJECT_DIRECTORY,
                                 directory))  # Use os.path.join

from self_improve import (
    update_code,
    get_current_code,
    backup_code,
    restore_code,
    parse_AI_response_and_update,
    next_iteration,
    main,
)


class TestSelfImprovement(unittest.TestCase):

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('ast.parse')
    def test_update_code(self, mock_ast_parse, mock_open):
        func = 'def hello():\n    print("hello")\n'
        target_file = 'self_improve.py'
        update_code(func, target_file)
        mock_open.assert_called()
        mock_ast_parse.assert_called()

    @mock.patch('builtins.open',
                new_callable=mock.mock_open,
                read_data='def hello():\n    print("hello")\n')
    def test_get_current_code(self, mock_open):
        code = get_current_code()
        self.assertEqual(code, 'def hello():\n    print("hello")\n')

    @mock.patch('shutil.copy2')
    def test_backup_code(self, mock_copy2):
        backup_code()
        mock_copy2.assert_called()

    @mock.patch('os.remove')
    @mock.patch('os.rename')
    def test_restore_code(self, mock_rename, mock_remove):
        restore_code()
        mock_remove.assert_called()
        mock_rename.assert_called()

    @mock.patch('self_improve.extract_python_code')
    @mock.patch('self_improve.extract_function_definitions')
    @mock.patch('self_improve.update_code')
    @mock.patch('self_improve.os.remove')
    @mock.patch('self_improve.restore_code')
    @mock.patch('self_improve.backup_code')
    def test_parse_AI_response_and_update(self, mock_backup_code,
                                          mock_restore_code, mock_os_remove,
                                          mock_update_code,
                                          mock_extract_function_definitions,
                                          mock_extract_python_code):
        response = 'Response from GPT-3'
        file = 'self_improve.py'
        parse_AI_response_and_update(response, file)
        mock_backup_code.assert_called()
        mock_restore_code.assert_called()
        mock_os_remove.assert_called()
        mock_update_code.assert_called()
        mock_extract_function_definitions.assert_called()
        mock_extract_python_code.assert_called()

    @mock.patch('self_improve.LLMRequester')
    @mock.patch('self_improve.parse_AI_response_and_update')
    def test_next_iteration(self, mock_parse_AI_response_and_update,
                            mock_LLMRequester):
        messages = [{'role': 'user', 'content': 'hello'}]
        tokens = 600
        file = 'self_improve.py'
        next_iteration(messages, tokens, file)
        mock_LLMRequester.assert_called()
        mock_parse_AI_response_and_update.assert_called()

    @mock.patch('self_improve.get_target_file')
    @mock.patch('self_improve.get_task')
    @mock.patch('self_improve.get_current_code')
    @mock.patch('self_improve.shorten_messages')
    @mock.patch('self_improve.next_iteration')
    def test_main(self, mock_next_iteration, mock_shorten_messages,
                  mock_get_current_code, mock_get_task, mock_get_target_file):
        main()
        mock_next_iteration.assert_called()
        mock_shorten_messages.assert_called()
        mock_get_current_code.assert_called()
        mock_get_task.assert_called()
        mock_get_target_file.assert_called()


if __name__ == '__main__':
    unittest.main()
