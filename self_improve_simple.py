
def is_palindrome(s: str) -> bool:
    s = re.sub('[\\W_]+', '', s).lower()
    return s == s[::-1]
