
def is_palindrome(s: str) -> bool:
    """
    This function checks if the input string s is a palindrome.
    It ignores spaces, punctuation, and capitalization.

    :param s: The input string to check
    :return: True if s is a palindrome, False otherwise
    """
    clean_s = ''.join((char.lower() for char in s if char.isalnum()))
    return clean_s == clean_s[::-1]
