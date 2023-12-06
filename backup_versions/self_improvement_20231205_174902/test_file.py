
def is_palindrome(s: str) -> bool:
    s_cleaned = ''.join((c for c in s if c.isalnum())).lower()
    return s_cleaned == s_cleaned[::-1]
