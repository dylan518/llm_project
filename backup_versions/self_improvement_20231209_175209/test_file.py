
def is_palindrome(s: str) -> bool:
    transformed_string = ''.join((ch.lower() for ch in s if ch.isalnum()))
    return transformed_string == transformed_string[::-1]
