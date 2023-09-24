import unittest
from unittest.mock import patch, Mock
from llm_request import LLMRequester


class TestLLMRequester(unittest.TestCase):

    def setUp(self):
        self.requester = LLMRequester()

    def test_read_request_limit(self):
        with patch('builtins.open', unittest.mock_open(read_data="10")):
            limit = self.requester.read_request_limit()
            self.assertEqual(limit, 10)

    def test_decrement_request_limit(self):
        with patch('llm_request.LLMRequester.read_request_limit',
                   return_value=10):
            with patch('builtins.open', unittest.mock_open()) as mock_file:
                self.requester.decrement_request_limit()
                mock_file.assert_called_with(LLMRequester.REQUEST_LIMIT_FILE,
                                             'w')
                mock_file().write.assert_called_with("9")

    def test_request_gpt3(self):
        with patch('llm_request.LLMRequester.read_request_limit',
                   return_value=10):
            with patch('llm_request.LLMRequester.decrement_request_limit'):
                mock_response = Mock()
                mock_response.generations = [[Mock(text="response")]]
                with patch.object(self.requester.llm_gpt3,
                                  'generate',
                                  return_value=mock_response):
                    response = self.requester.request("gpt3", "prompt")
                    self.assertEqual(response, "response")

    def test_request_gpt4(self):
        with patch('llm_request.LLMRequester.read_request_limit',
                   return_value=10):
            with patch('llm_request.LLMRequester.decrement_request_limit'):
                mock_response = Mock()
                mock_response.generations = [[Mock(text="response")]]
                with patch.object(self.requester.llm_gpt4,
                                  'generate',
                                  return_value=mock_response):
                    response = self.requester.request("gpt4", "prompt")
                    self.assertEqual(response, "response")

    def test_save_interactions(self):
        self.requester.interactions = [{
            "model": "gpt3",
            "prompt": "prompt",
            "response": "response"
        }]
        with patch('builtins.open', unittest.mock_open()) as mock_file:
            self.requester.save_interactions()
            mock_file.assert_called_with("interactions.json", 'w')
            mock_file().write.assert_called_with(
                json.dumps(self.requester.interactions))


if __name__ == '__main__':
    unittest.main()
