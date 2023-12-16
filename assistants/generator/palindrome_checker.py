def is_palindrome(s):
    return s == s[::-1]

# Test cases to check if the function works correctly
test_strings = ['radar', 'hello', 'level', 'world', 'civic']

for test_string in test_strings:
    result = is_palindrome(test_string)
    print(f"'{test_string}' is a palindrome: {result}")
