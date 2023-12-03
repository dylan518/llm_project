
def is_palindrome(s: str) -> bool:
    cleaned = ''.join((c for c in s if c.isalnum())).lower()
    return cleaned == cleaned[::-1]
