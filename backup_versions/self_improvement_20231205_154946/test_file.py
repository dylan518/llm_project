
def is_palindrome(s: str) -> bool:
    """
    This function checks if the string 's' is a palindrome. 
    A palindrome is a sequence that reads the same backwards as forwards.
    
    :param s: str - The string to be checked.
    :return: bool - Returns True if 's' is a palindrome, False otherwise.
    """
    clean_s = ''.join((char for char in s if char.isalnum())).lower()
    return clean_s == clean_s[::-1]
