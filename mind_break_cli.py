#!/usr/bin/env python3
"""Mind Break CLI game.

The player sets a secret positive integer (3 to 10 digits), then keeps guessing it.
After each guess, the game reports:
- Digits in the correct position
- Digits present in the secret number but in the wrong position
"""


def prompt_secret_number() -> str:
    while True:
        raw = input("Choose the secret number (3 to 10 digits, positive integer): ").strip()

        if not raw.isdigit():
            print("Invalid input. Please enter digits only.")
            continue

        if raw.startswith("0"):
            print("Invalid input. The number must be positive and cannot start with 0.")
            continue

        if not 3 <= len(raw) <= 10:
            print("Invalid length. The number must be between 3 and 10 digits.")
            continue

        return raw


def prompt_max_attempts() -> int | None:
    while True:
        raw = input(
            "Max attempts (press Enter for unlimited, or type a positive integer): "
        ).strip()

        if raw == "":
            return None

        if not raw.isdigit() or raw == "0":
            print("Invalid input. Enter a positive integer, or press Enter for unlimited.")
            continue

        return int(raw)


def score_guess(secret: str, guess: str) -> tuple[int, int]:
    # Count exact matches by index.
    correct_position = sum(1 for s_digit, g_digit in zip(secret, guess) if s_digit == g_digit)

    # Count shared digits including duplicates, regardless of position.
    secret_counts: dict[str, int] = {}
    guess_counts: dict[str, int] = {}

    for digit in secret:
        secret_counts[digit] = secret_counts.get(digit, 0) + 1

    for digit in guess:
        guess_counts[digit] = guess_counts.get(digit, 0) + 1

    shared_digits = sum(
        min(secret_counts.get(digit, 0), guess_counts.get(digit, 0))
        for digit in set(secret_counts) | set(guess_counts)
    )

    wrong_position = shared_digits - correct_position
    return correct_position, wrong_position


def prompt_guess(expected_len: int) -> str:
    while True:
        raw = input(f"Enter your guess ({expected_len} digits): ").strip()

        if not raw.isdigit():
            print("Invalid input. Please enter digits only.")
            continue

        if len(raw) != expected_len:
            print(f"Invalid length. Guess must be exactly {expected_len} digits.")
            continue

        return raw


def main() -> None:
    print("=== Mind Break CLI ===")
    secret = prompt_secret_number()
    max_attempts = prompt_max_attempts()

    print("\nGame started! Try to guess the number.")
    if max_attempts is None:
        print("Attempts: unlimited")
    else:
        print(f"Attempts allowed: {max_attempts}")

    attempts_used = 0

    while True:
        if max_attempts is not None and attempts_used >= max_attempts:
            print("\nNo attempts left. Game over!")
            print(f"The secret number was: {secret}")
            return

        guess = prompt_guess(len(secret))
        attempts_used += 1

        if guess == secret:
            print(f"\nCorrect! You guessed the number in {attempts_used} attempt(s).")
            return

        correct_position, wrong_position = score_guess(secret, guess)
        print(
            f"Result: {correct_position} digit(s) in the correct position, "
            f"{wrong_position} digit(s) present but in the wrong position."
        )


if __name__ == "__main__":
    main()
