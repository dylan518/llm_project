
def is_palindrome(s: str) -> bool:
    stripped_str = ''.join((e for e in s if e.isalnum())).lower()
    return stripped_str == stripped_str[::-1]
