
def is_palindrome(s: str) -> bool:
    cleaned_str = ''.join((e for e in s.lower() if e.isalnum()))
    return cleaned_str == cleaned_str[::-1]
