import unittest
import sys
import os
import json  # Imported json as it is used in test_save_interactions
from unittest.mock import patch, Mock, mock_open, ANY

PROJECT_DIRECTORY = "/Users/dylanwilson/Documents/GitHub/llm_project/"
MODULE_DIRECTORIES = ["llm_requests", "running_tests", "logging"]

for directory in MODULE_DIRECTORIES:
    sys.path.append(os.path.join(PROJECT_DIRECTORY,
                                 directory))  # Use os.path.join

from llm_request import LLMRequester


class TestLLMRequester(unittest.TestCase):

    def setUp(self):
        self.requester = LLMRequester()
        self.PROJECT_DIRECTORY = "/Users/dylanwilson/Documents/GitHub/llm_project/"

    def test_request_gpt3(self):
        with patch('llm_request.LLMRequester.read_request_limit',
                   return_value=10):
            with patch('llm_request.LLMRequester.decrement_request_limit'):
                mock_response = Mock()
                print(self.requester.llm_gpt3.__dict__)
                #                print(dir(self.requester.llm_gpt3))
                mock_response.generations = [[Mock(text="response")]]
                with patch('llm_request.OpenAI.generate',
                           return_value=mock_response):
                    response = self.requester.request("gpt3", "prompt")
                    self.assertEqual(type(response), str)

    def test_request_gpt4(self):
        with patch('llm_request.LLMRequester.read_request_limit',
                   return_value=10):
            with patch('llm_request.LLMRequester.decrement_request_limit'):
                mock_response = Mock()
                print(self.requester.llm_gpt4.__dict__)
                #                print(dir(self.requester.llm_gpt3))
                mock_response.generations = [[Mock(text="response")]]
                with patch('llm_request.OpenAI.generate',
                           return_value=mock_response):
                    response = self.requester.request("gpt4", "prompt")
                    self.assertEqual(type(response), str)

    def test_read_request_limit(self):
        with patch(
                'builtins.open',
                mock_open(read_data="10")) as mock_file:  # Corrected mock_open
            limit = self.requester.read_request_limit()
            self.assertEqual(limit, 10)
            mock_file().read.assert_called_once(
            )  # Assert read method was called on file object

    def test_decrement_request_limit(self):
        with patch('llm_request.LLMRequester.read_request_limit',
                   return_value=10):
            with patch('builtins.open',
                       mock_open()) as mock_file:  # Corrected mock_open
                self.requester.decrement_request_limit()
                mock_file.assert_called_with(self.PROJECT_DIRECTORY +
                                             self.requester.REQUEST_LIMIT_FILE,
                                             'w')  # Accessed through instance
                mock_file().write.assert_called_with("9")

    def test_save_interactions(self):
        self.requester.interactions = [{
            "model": "gpt3",
            "prompt": "prompt",
            "response": "response"
        }]
        with patch('json.dump') as mock_json_dump:
            self.requester.save_interactions()
            mock_json_dump.assert_called_with(self.requester.interactions, ANY)


if __name__ == '__main__':
    unittest.main()
