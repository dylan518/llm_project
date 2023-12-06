
def is_palindrome(s: str) -> bool:
    sanitized_str = ''.join((char.lower() for char in s if char.isalnum()))
    return sanitized_str == sanitized_str[::-1]
