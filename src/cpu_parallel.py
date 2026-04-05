"""
CPU Parallel Password Cracker
Uses multiprocessing to parallelize password cracking across CPU cores.
"""

import hashlib
import time
from typing import Optional, Tuple, List
from multiprocessing import Pool, cpu_count
from itertools import product


class CPUParallelCracker:
    """Parallel CPU-based password cracker using multiprocessing."""

    def __init__(self, hash_algorithm: str = "md5", num_workers: int = None):
        """
        Initialize the parallel cracker.

        Args:
            hash_algorithm: Hash algorithm to use (md5, sha256)
            num_workers: Number of worker processes (default: CPU count)
        """
        self.hash_algorithm = hash_algorithm.lower()
        self.num_workers = num_workers or cpu_count()
        self.attempts = 0

    def hash_password(self, password: str) -> str:
        """Hash a password using the specified algorithm."""
        if self.hash_algorithm == "md5":
            return hashlib.md5(password.encode()).hexdigest()
        elif self.hash_algorithm == "sha256":
            return hashlib.sha256(password.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {self.hash_algorithm}")

    def brute_force(self, target_hash: str, charset: str, max_length: int) -> Tuple[Optional[str], dict]:
        """
        Parallel brute force attack.

        Args:
            target_hash: The hash to crack
            charset: Characters to use
            max_length: Maximum password length to try

        Returns:
            Tuple of (found_password, statistics)
        """
        start_time = time.time()
        total_attempts = 0

        # Try each length sequentially, but parallelize within each length
        for length in range(1, max_length + 1):
            result, attempts = self._try_length_parallel(target_hash, charset, length)
            total_attempts += attempts

            if result:
                elapsed = time.time() - start_time
                stats = {
                    'attempts': total_attempts,
                    'time': elapsed,
                    'rate': total_attempts / elapsed if elapsed > 0 else 0,
                    'workers': self.num_workers
                }
                return result, stats

        elapsed = time.time() - start_time
        stats = {
            'attempts': total_attempts,
            'time': elapsed,
            'rate': total_attempts / elapsed if elapsed > 0 else 0,
            'workers': self.num_workers
        }
        return None, stats

    def _try_length_parallel(self, target_hash: str, charset: str, length: int) -> Tuple[Optional[str], int]:
        """Try all combinations of a specific length using parallel processing."""
        # Generate all combinations
        all_combos = [''.join(combo) for combo in product(charset, repeat=length)]

        # Split work into chunks for workers
        chunk_size = max(1, len(all_combos) // self.num_workers)

        # Create worker arguments
        worker_args = [
            (all_combos[i:i + chunk_size], target_hash, self.hash_algorithm)
            for i in range(0, len(all_combos), chunk_size)
        ]

        # Process in parallel
        with Pool(processes=self.num_workers) as pool:
            results = pool.map(_worker_check_passwords, worker_args)

        # Check results
        for result in results:
            if result is not None:
                return result, len(all_combos)

        return None, len(all_combos)

    def dictionary_attack(self, target_hash: str, wordlist: list) -> Tuple[Optional[str], dict]:
        """
        Parallel dictionary attack.

        Args:
            target_hash: The hash to crack
            wordlist: List of password candidates

        Returns:
            Tuple of (found_password, statistics)
        """
        start_time = time.time()

        # Split wordlist into chunks for workers
        chunk_size = max(1, len(wordlist) // self.num_workers)
        worker_args = [
            (wordlist[i:i + chunk_size], target_hash, self.hash_algorithm)
            for i in range(0, len(wordlist), chunk_size)
        ]

        # Process in parallel
        with Pool(processes=self.num_workers) as pool:
            results = pool.map(_worker_check_passwords, worker_args)

        elapsed = time.time() - start_time

        # Check results
        for result in results:
            if result is not None:
                stats = {
                    'attempts': len(wordlist),
                    'time': elapsed,
                    'rate': len(wordlist) / elapsed if elapsed > 0 else 0,
                    'workers': self.num_workers
                }
                return result, stats

        stats = {
            'attempts': len(wordlist),
            'time': elapsed,
            'rate': len(wordlist) / elapsed if elapsed > 0 else 0,
            'workers': self.num_workers
        }
        return None, stats


def _worker_check_passwords(args: Tuple[List[str], str, str]) -> Optional[str]:
    """
    Worker function to check a chunk of passwords.

    Args:
        args: Tuple of (password_list, target_hash, hash_algorithm)

    Returns:
        Found password or None
    """
    passwords, target_hash, hash_algorithm = args

    for password in passwords:
        if hash_algorithm == "md5":
            pwd_hash = hashlib.md5(password.encode()).hexdigest()
        elif hash_algorithm == "sha256":
            pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        else:
            continue

        if pwd_hash == target_hash:
            return password

    return None
