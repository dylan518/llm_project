
def is_palindrome(s: str) -> bool:
    stripped_str = ''.join((c.lower() for c in s if c.isalnum()))
    return stripped_str == stripped_str[::-1]
