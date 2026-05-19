"""Utilities for finding the closest prime number."""

from __future__ import annotations


def is_prime(n: int) -> bool:
    """Return True if n is prime, else False."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    factor = 3
    while factor * factor <= n:
        if n % factor == 0:
            return False
        factor += 2
    return True


def closest_prime(target: int) -> int:
    """Return the prime number closest to target.

    If two primes are equally close, returns the smaller one.
    """
    if target <= 2:
        return 2

    distance = 0
    while True:
        lower = target - distance
        if lower >= 2 and is_prime(lower):
            return lower

        upper = target + distance
        if is_prime(upper):
            return upper

        distance += 1


if __name__ == "__main__":
    user_input = int(input("Enter an integer: ").strip())
    print(f"Closest prime to {user_input} is {closest_prime(user_input)}")
