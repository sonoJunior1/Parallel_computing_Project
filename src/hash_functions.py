"""
Hash Function Utilities
Common hash functions and utilities for password cracking.
"""

import hashlib


def hash_md5(password: str) -> str:
    """
    Compute MD5 hash of a password.

    Args:
        password: Plain text password

    Returns:
        Hexadecimal MD5 hash
    """
    return hashlib.md5(password.encode()).hexdigest()


def hash_sha256(password: str) -> str:
    """
    Compute SHA-256 hash of a password.

    Args:
        password: Plain text password

    Returns:
        Hexadecimal SHA-256 hash
    """
    return hashlib.sha256(password.encode()).hexdigest()


def hash_sha1(password: str) -> str:
    """
    Compute SHA-1 hash of a password.

    Args:
        password: Plain text password

    Returns:
        Hexadecimal SHA-1 hash
    """
    return hashlib.sha1(password.encode()).hexdigest()


def verify_hash(password: str, target_hash: str, algorithm: str = "md5") -> bool:
    """
    Verify if a password matches a hash.

    Args:
        password: Plain text password to test
        target_hash: Target hash to match
        algorithm: Hash algorithm (md5, sha256, sha1)

    Returns:
        True if password matches hash
    """
    algorithm = algorithm.lower()

    if algorithm == "md5":
        computed_hash = hash_md5(password)
    elif algorithm == "sha256":
        computed_hash = hash_sha256(password)
    elif algorithm == "sha1":
        computed_hash = hash_sha1(password)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    return computed_hash == target_hash


def get_supported_algorithms() -> list:
    """Get list of supported hash algorithms."""
    return ["md5", "sha256", "sha1"]
