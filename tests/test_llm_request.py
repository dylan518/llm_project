import unittest
import os
import sys

# Add local modules to path
PROJECT_DIRECTORY = "/Users/dylan/Documents/GitHub/llm_project/"
MODULE_DIRECTORIES = ["llm_requests"]

for directory in MODULE_DIRECTORIES:
    sys.path.append(os.path.join(PROJECT_DIRECTORY, directory))

from llm_request import LLMRequester


class TestLLMRequester(unittest.TestCase):

    def setUp(self):
        self.requester = LLMRequester()

    def test_request_gpt3_successful(self):
        response = self.requester.request("gpt3", "Hello, how are you?")
        print("Response from GPT-3:", response)
        self.assertIsInstance(response,
                              str)  # Check if the response is a string

    def test_request_gpt4_successful(self):
        response = self.requester.request("gpt4", "Hello, how are you?")
        print("Response from GPT-4:", response)
        self.assertIsInstance(response,
                              str)  # Check if the response is a string

    def test_read_request_limit(self):
        limit = self.requester.read_request_limit()
        self.assertIsInstance(limit, int)  # Check if the limit is an integer

    def test_decrement_request_limit(self):
        initial_limit = self.requester.read_request_limit()
        self.requester.decrement_request_limit()
        new_limit = self.requester.read_request_limit()
        self.assertEqual(new_limit, initial_limit -
                         1)  # Check if the limit has been decremented

    def test_parse_to_messages_with_string(self):
        result = self.requester.parse_to_messages("Hello, how are you?")
        self.assertEqual(result, [{
            "role": "user",
            "content": "Hello, how are you?"
        }])

    def test_parse_to_messages_with_list(self):
        input_list = [{
            "role": "user",
            "content": "Hello"
        }, {
            "role": "user",
            "content": "How are you?"
        }]
        result = self.requester.parse_to_messages(input_list)
        self.assertEqual(result, input_list)

    def test_parse_to_messages_invalid_input(self):
        with self.assertRaises(ValueError):
            self.requester.parse_to_messages(123)


if __name__ == '__main__':
    unittest.main()
