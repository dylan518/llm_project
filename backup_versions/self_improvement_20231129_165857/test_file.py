
def is_palindrome(s: str) -> bool:
    cleaned_string = ''.join((char for char in s if char.isalnum())).lower()
    return cleaned_string == cleaned_string[::-1]
