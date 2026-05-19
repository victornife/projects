# Closest Prime Project (Mini)

A tiny Python project that finds the prime number closest to a given integer.

## Features

- Fast primality check using trial division up to `sqrt(n)`
- Finds the nearest prime above or below a target number
- Tie-breaker behavior: if two primes are equally close, it returns the smaller one

## Run

```bash
python closest-prime-project/closest_prime.py
```

## Test

```bash
pytest -q
```
