def is_palindrome(s: str) -> bool:
    cleaned = ''.join((char for char in s if char.isalnum())).lower()
    return cleaned == cleaned[::-1]