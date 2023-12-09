
def is_palindrome(s: str) -> bool:
    normalized_str = ''.join((char for char in s if char.isalnum())).lower()
    return normalized_str == normalized_str[::-1]
