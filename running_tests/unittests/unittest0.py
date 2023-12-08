import unittest
import sys

PROJECT_DIRECTORY = "/Users/dylan/Documents/GitHub/llm_project/"
MODULE_DIRECTORIES = ["self_improvement"]
for directory in MODULE_DIRECTORIES:
    sys.path.append(PROJECT_DIRECTORY + directory)


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