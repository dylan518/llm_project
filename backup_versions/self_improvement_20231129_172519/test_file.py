
def is_palindrome(s: str) -> bool:
    sanitized = ''.join((char for char in s if char.isalnum())).lower()
    return sanitized == sanitized[::-1]
