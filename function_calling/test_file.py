def factorial(n):
    if n < 0:
        raise ValueError('Input must be a non-negative integer')
    result = 1
    for i in range(1, n + 1):
        result *= i
print(factorial(5))

def sum_up_to(n):
    if n < 0:
        raise ValueError('Input must be a non-negative integer')
    return sum(range(1, n + 1))

print(sum_up_to(5))

print(factorial(5))
