
def is_palindrome(s: str) -> bool:
    clean_string = ''.join((e for e in s if e.isalnum())).lower()
    return clean_string == clean_string[::-1]
