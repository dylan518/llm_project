def is_palindrome(s: str) -> bool:
    cleaned_str = ''.join((char for char in s if char.isalnum())).lower()
    return cleaned_str == cleaned_str[::-1]