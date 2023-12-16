def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def prime_factors(number):
    i = 2
    factors = []
    while i * i <= number:
        if number % i:
            i += 1
        else:
            number //= i
            if is_prime(i):
                factors.append(i)
    if number > 1:
        if is_prime(number):
            factors.append(number)
    return factors

# Test cases
def test_prime_factors():
    assert prime_factors(60) == [2, 2, 3, 5]
    assert prime_factors(13) == [13]
    assert prime_factors(100) == [2, 2, 5, 5]
    print('All tests passed!')

if __name__ == '__main__':
    test_prime_factors()