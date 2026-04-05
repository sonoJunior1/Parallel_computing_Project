"""
CPU Sequential Password Cracker
Baseline implementation using single-threaded approach.
"""

import hashlib
import time
from typing import Optional, Tuple


class CPUSequentialCracker:
    """Sequential CPU-based password cracker (baseline)."""

    def __init__(self, hash_algorithm: str = "md5"):
        """
        Initialize the sequential cracker.

        Args:
            hash_algorithm: Hash algorithm to use (md5, sha256)
        """
        self.hash_algorithm = hash_algorithm.lower()
        self.attempts = 0

    def hash_password(self, password: str) -> str:
        """
        Hash a password using the specified algorithm.

        Args:
            password: Plain text password

        Returns:
            Hexadecimal hash string
        """
        if self.hash_algorithm == "md5":
            return hashlib.md5(password.encode()).hexdigest()
        elif self.hash_algorithm == "sha256":
            return hashlib.sha256(password.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {self.hash_algorithm}")

    def brute_force(self, target_hash: str, charset: str, max_length: int) -> Tuple[Optional[str], dict]:
        """
        Brute force attack trying all combinations.

        Args:
            target_hash: The hash to crack
            charset: Characters to use (e.g., 'abc123')
            max_length: Maximum password length to try

        Returns:
            Tuple of (found_password, statistics)
        """
        self.attempts = 0
        start_time = time.time()

        # Try all lengths from 1 to max_length
        for length in range(1, max_length + 1):
            result = self._try_length(target_hash, charset, length)
            if result:
                elapsed = time.time() - start_time
                stats = {
                    'attempts': self.attempts,
                    'time': elapsed,
                    'rate': self.attempts / elapsed if elapsed > 0 else 0
                }
                return result, stats

        elapsed = time.time() - start_time
        stats = {
            'attempts': self.attempts,
            'time': elapsed,
            'rate': self.attempts / elapsed if elapsed > 0 else 0
        }
        return None, stats

    def _try_length(self, target_hash: str, charset: str, length: int) -> Optional[str]:
        """Try all combinations of a specific length."""
        from itertools import product

        for combo in product(charset, repeat=length):
            password = ''.join(combo)
            self.attempts += 1

            if self.hash_password(password) == target_hash:
                return password

        return None

    def dictionary_attack(self, target_hash: str, wordlist: list) -> Tuple[Optional[str], dict]:
        """
        Dictionary attack using a wordlist.

        Args:
            target_hash: The hash to crack
            wordlist: List of password candidates

        Returns:
            Tuple of (found_password, statistics)
        """
        self.attempts = 0
        start_time = time.time()

        for password in wordlist:
            self.attempts += 1
            if self.hash_password(password) == target_hash:
                elapsed = time.time() - start_time
                stats = {
                    'attempts': self.attempts,
                    'time': elapsed,
                    'rate': self.attempts / elapsed if elapsed > 0 else 0
                }
                return password, stats

        elapsed = time.time() - start_time
        stats = {
            'attempts': self.attempts,
            'time': elapsed,
            'rate': self.attempts / elapsed if elapsed > 0 else 0
        }
        return None, stats
