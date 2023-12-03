
def is_palindrome(s: str) -> bool:
    normalized_s = ''.join((c.lower() for c in s if c.isalnum()))
    return normalized_s == normalized_s[::-1]
