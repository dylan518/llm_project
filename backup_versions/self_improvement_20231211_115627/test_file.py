
def is_palindrome(s: str) -> bool:
    clean_s = ''.join((char for char in s if char.isalnum())).lower()
    return clean_s == clean_s[::-1]
