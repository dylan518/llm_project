
def is_palindrome(s: str) -> bool:
    stripped_str = ''.join(filter(str.isalnum, s)).lower()
    return stripped_str == stripped_str[::-1]
