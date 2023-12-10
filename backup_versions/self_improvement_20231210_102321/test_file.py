def is_palindrome(s: str) -> bool:
    cleaned_string = ''.join((c for c in s if c.isalnum())).lower()
    return cleaned_string == cleaned_string[::-1]