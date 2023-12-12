
def is_palindrome(s: str) -> bool:
    clean_s = ''.join((e for e in s if e.isalnum())).lower()
    return clean_s == clean_s[::-1]
