
def is_palindrome(s: str) -> bool:
    clean_s = ''.join(filter(str.isalnum, s)).lower()
    return clean_s == clean_s[::-1]
