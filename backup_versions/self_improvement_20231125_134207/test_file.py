










def is_palindrome(s: str) -> bool:
    cleaned_s = ''.join((char.lower() for char in s if char.isalnum()))
    return cleaned_s == cleaned_s[::-1]
