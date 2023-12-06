
def is_palindrome(s: str) -> bool:
    cleaned_s = ''.join((char for char in s if char.isalnum())).lower()
    return cleaned_s == cleaned_s[::-1]
