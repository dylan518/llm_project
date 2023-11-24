





def is_palindrome(s: str) -> bool:
    s = ''.join((c for c in s if c.isalnum())).lower()
    return s == s[::-1]
