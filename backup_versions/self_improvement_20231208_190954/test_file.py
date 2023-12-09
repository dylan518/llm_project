
def is_palindrome(s: str) -> bool:
    s = ''.join((char for char in s if char.isalnum())).lower()
    return s == s[::-1]
