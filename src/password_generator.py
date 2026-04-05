"""
Password Generator Utilities
Generate password candidates for brute force attacks.
"""

from itertools import product
from typing import Iterator, List
import string


# Common character sets
CHARSET_LOWERCASE = string.ascii_lowercase
CHARSET_UPPERCASE = string.ascii_uppercase
CHARSET_DIGITS = string.digits
CHARSET_ALPHANUMERIC = CHARSET_LOWERCASE + CHARSET_UPPERCASE + CHARSET_DIGITS
CHARSET_ALL = CHARSET_ALPHANUMERIC + string.punctuation


def generate_passwords(charset: str, length: int) -> Iterator[str]:
    """
    Generate all possible passwords of a given length.

    Args:
        charset: Characters to use
        length: Password length

    Yields:
        Password strings
    """
    for combo in product(charset, repeat=length):
        yield ''.join(combo)


def generate_passwords_range(charset: str, min_length: int, max_length: int) -> Iterator[str]:
    """
    Generate all possible passwords within a length range.

    Args:
        charset: Characters to use
        min_length: Minimum password length
        max_length: Maximum password length

    Yields:
        Password strings
    """
    for length in range(min_length, max_length + 1):
        yield from generate_passwords(charset, length)


def count_combinations(charset: str, length: int) -> int:
    """
    Count total number of possible passwords.

    Args:
        charset: Characters to use
        length: Password length

    Returns:
        Total number of combinations
    """
    return len(charset) ** length


def count_combinations_range(charset: str, min_length: int, max_length: int) -> int:
    """
    Count total combinations within a length range.

    Args:
        charset: Characters to use
        min_length: Minimum password length
        max_length: Maximum password length

    Returns:
        Total number of combinations
    """
    total = 0
    for length in range(min_length, max_length + 1):
        total += count_combinations(charset, length)
    return total


def load_wordlist(filepath: str) -> List[str]:
    """
    Load a wordlist from a file.

    Args:
        filepath: Path to wordlist file (one password per line)

    Returns:
        List of passwords
    """
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        return [line.strip() for line in f if line.strip()]


def get_common_passwords(limit: int = 100) -> List[str]:
    """
    Get a list of common passwords for testing.

    Args:
        limit: Number of passwords to return

    Returns:
        List of common passwords
    """
    common = [
        "password", "123456", "123456789", "12345678", "12345",
        "1234567", "password1", "123123", "1234567890", "000000",
        "abc123", "qwerty", "admin", "letmein", "welcome",
        "monkey", "dragon", "master", "sunshine", "princess",
        "login", "admin123", "root", "pass", "test",
        "guest", "123321", "654321", "password123", "qwerty123"
    ]
    return common[:limit]
