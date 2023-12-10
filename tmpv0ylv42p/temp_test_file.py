
def is_palindrome(s: str) -> bool:
    """
    This function checks if the input string s is a palindrome.
    It ignores spaces, punctuation, and capitalization.

    :param s: The input string to check
    :return: True if s is a palindrome, False otherwise
    """
    clean_s = ''.join((char.lower() for char in s if char.isalnum()))
    return clean_s == clean_s[::-1]

import unittest
import sys
import os

PROJECT_DIRECTORY = os.sep.join(
    os.path.abspath(__file__).split(os.sep)
    [:next((i for i, p in enumerate(os.path.abspath(__file__).split(os.sep))
            if 'llm_project' in p), None) +
     1]) if 'llm_project' in os.path.abspath(__file__) else None

MODULE_DIRECTORIES = ["self_improvement"]
for directory in MODULE_DIRECTORIES:
    sys.path.append(os.path.join(PROJECT_DIRECTORY, directory))


class PalindromeTester(unittest.TestCase):

    def setUp(self):
        # Assuming the function is_palindrome is imported from the test file
        from test_file import is_palindrome
        self.is_palindrome = is_palindrome

    def test_palindrome(self):
        self.assertTrue(self.is_palindrome("A man a plan a canal Panama"))
        self.assertTrue(self.is_palindrome("Was it a car or a cat I saw"))
        self.assertFalse(self.is_palindrome("Hello"))


if __name__ == "__main__":
    unittest.main()