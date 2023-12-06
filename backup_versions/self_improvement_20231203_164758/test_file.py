
def is_palindrome(s: str) -> bool:
    clean_s = ''.join((c.lower() for c in s if c.isalnum()))
    return clean_s == clean_s[::-1]
