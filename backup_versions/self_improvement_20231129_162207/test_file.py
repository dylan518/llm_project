
def is_palindrome(s: str) -> bool:
    alphanumeric_filter = filter(str.isalnum, s.lower())
    filtered_chars = ''.join(alphanumeric_filter)
    return filtered_chars == filtered_chars[::-1]
