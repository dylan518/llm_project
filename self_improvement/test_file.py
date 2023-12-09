
def is_palindrome(s: str) -> bool:
    normalized_string = ''.join((char for char in s if char.isalnum())).lower()
    return normalized_string == normalized_string[::-1]
