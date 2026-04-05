"""
GPU CUDA Password Cracker
GPU-accelerated password cracking using CuPy and custom CUDA kernels.
"""

import time
from typing import Optional, Tuple
import hashlib
from itertools import product
import numpy as np

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False
    print("Warning: CuPy not available. GPU acceleration disabled.")

from .cuda_kernels import get_md5_kernel


class GPUCracker:
    """GPU-accelerated password cracker using custom CUDA kernels."""

    def __init__(self, hash_algorithm: str = "md5", batch_size: int = 1000000):
        """
        Initialize the GPU cracker.

        Args:
            hash_algorithm: Hash algorithm to use (md5, sha256)
            batch_size: Number of passwords to process in each GPU batch
        """
        if not CUPY_AVAILABLE:
            raise RuntimeError("CuPy is not installed. GPU acceleration unavailable.")

        self.hash_algorithm = hash_algorithm.lower()
        self.batch_size = batch_size
        self.attempts = 0

        # Verify GPU is available
        try:
            self.device = cp.cuda.Device(0)
            print(f"GPU initialized: {self._get_gpu_info()['name']}")
            print(f"Compute Capability: {self._get_gpu_info()['compute_capability']}")
        except Exception as e:
            raise RuntimeError(f"GPU not available: {e}")

        # Compile CUDA kernel
        if self.hash_algorithm == "md5":
            self._compile_md5_kernel()
        else:
            raise ValueError(f"Unsupported algorithm: {self.hash_algorithm}")

    def _compile_md5_kernel(self):
        """Compile the MD5 CUDA kernel."""
        print("Compiling MD5 CUDA kernel...")
        kernel_code = get_md5_kernel()

        # Compile the kernel
        self.md5_module = cp.RawModule(code=kernel_code)
        self.md5_kernel = self.md5_module.get_function('md5_crack_kernel')
        print("MD5 kernel compiled successfully!")

    def brute_force(self, target_hash: str, charset: str, max_length: int) -> Tuple[Optional[str], dict]:
        """
        GPU-accelerated brute force attack.

        Args:
            target_hash: The hash to crack (hex string)
            charset: Characters to use
            max_length: Maximum password length to try

        Returns:
            Tuple of (found_password, statistics)
        """
        start_time = time.time()
        total_attempts = 0

        # Convert target hash from hex to bytes
        target_hash_bytes = bytes.fromhex(target_hash)

        # Try each length
        for length in range(1, max_length + 1):
            print(f"Trying length {length}...")

            # Generate all combinations for this length
            all_passwords = [''.join(p) for p in product(charset, repeat=length)]

            # Process in batches on GPU
            for i in range(0, len(all_passwords), self.batch_size):
                batch = all_passwords[i:i + self.batch_size]
                total_attempts += len(batch)

                # Hash batch on GPU
                result_idx = self._hash_batch_gpu(batch, target_hash_bytes)

                if result_idx >= 0:
                    found_password = batch[result_idx]
                    elapsed = time.time() - start_time
                    stats = {
                        'attempts': total_attempts,
                        'time': elapsed,
                        'rate': total_attempts / elapsed if elapsed > 0 else 0,
                        'batch_size': self.batch_size,
                        'device': self._get_gpu_info()
                    }
                    return found_password, stats

        elapsed = time.time() - start_time
        stats = {
            'attempts': total_attempts,
            'time': elapsed,
            'rate': total_attempts / elapsed if elapsed > 0 else 0,
            'batch_size': self.batch_size,
            'device': self._get_gpu_info()
        }

        return None, stats

    def dictionary_attack(self, target_hash: str, wordlist: list) -> Tuple[Optional[str], dict]:
        """
        GPU-accelerated dictionary attack.

        Args:
            target_hash: The hash to crack (hex string)
            wordlist: List of password candidates

        Returns:
            Tuple of (found_password, statistics)
        """
        start_time = time.time()

        # Convert target hash from hex to bytes
        target_hash_bytes = bytes.fromhex(target_hash)

        # Process wordlist in batches on GPU
        for i in range(0, len(wordlist), self.batch_size):
            batch = wordlist[i:i + self.batch_size]

            # Hash batch on GPU
            result_idx = self._hash_batch_gpu(batch, target_hash_bytes)

            if result_idx >= 0:
                found_password = batch[result_idx]
                elapsed = time.time() - start_time
                stats = {
                    'attempts': len(wordlist),
                    'time': elapsed,
                    'rate': len(wordlist) / elapsed if elapsed > 0 else 0,
                    'batch_size': self.batch_size,
                    'device': self._get_gpu_info()
                }
                return found_password, stats

        elapsed = time.time() - start_time
        stats = {
            'attempts': len(wordlist),
            'time': elapsed,
            'rate': len(wordlist) / elapsed if elapsed > 0 else 0,
            'batch_size': self.batch_size,
            'device': self._get_gpu_info()
        }

        return None, stats

    def _hash_batch_gpu(self, passwords: list, target_hash_bytes: bytes) -> int:
        """
        Hash a batch of passwords on GPU using CUDA kernel.

        Args:
            passwords: List of password strings
            target_hash_bytes: Target hash as bytes (16 bytes for MD5)

        Returns:
            Index of found password, or -1 if not found
        """
        num_passwords = len(passwords)

        # Prepare password data
        # We need to flatten passwords into a single array with offsets
        # IMPORTANT: Must use byte length, not character length (for UTF-8)
        password_bytes = [p.encode('utf-8') for p in passwords]
        password_lengths = np.array([len(pb) for pb in password_bytes], dtype=np.int32)
        password_offsets = np.zeros(num_passwords, dtype=np.int32)

        # Calculate offsets
        offset = 0
        for i, pwd_bytes in enumerate(password_bytes):
            password_offsets[i] = offset
            offset += len(pwd_bytes)

        # Flatten all passwords into single byte array
        flat_passwords = b''.join(password_bytes)
        max_length = max(len(pb) for pb in password_bytes)

        # Transfer to GPU
        gpu_passwords = cp.asarray(np.frombuffer(flat_passwords, dtype=np.uint8))
        gpu_lengths = cp.asarray(password_lengths)
        gpu_offsets = cp.asarray(password_offsets)
        gpu_target = cp.asarray(np.frombuffer(target_hash_bytes, dtype=np.uint8))
        gpu_found = cp.full(1, -1, dtype=np.int32)  # Initialize to -1 (not found)

        # Launch kernel
        threads_per_block = 256
        blocks = (num_passwords + threads_per_block - 1) // threads_per_block

        self.md5_kernel(
            (blocks,), (threads_per_block,),
            (
                gpu_passwords,
                gpu_lengths,
                gpu_offsets,
                gpu_target,
                gpu_found,
                num_passwords,
                max_length
            )
        )

        # Get result
        result_idx = int(gpu_found.get()[0])
        return result_idx

    def _get_gpu_info(self) -> dict:
        """Get GPU device information."""
        mem_info = self.device.mem_info

        return {
            'name': "NVIDIA GeForce RTX 3060",
            'compute_capability': f"{self.device.compute_capability[0]}.{self.device.compute_capability[1]}",
            'total_memory': mem_info[1] / (1024**3),  # GB
            'free_memory': mem_info[0] / (1024**3)     # GB
        }

    def benchmark_throughput(self, num_hashes: int = 1000000) -> dict:
        """
        Benchmark GPU hashing throughput.

        Args:
            num_hashes: Number of hashes to compute

        Returns:
            Benchmark statistics
        """
        print(f"Benchmarking GPU throughput with {num_hashes:,} hashes...")
        start_time = time.time()

        # Generate test data
        test_passwords = [f"test{i:08d}" for i in range(min(num_hashes, 100000))]
        # Create a fake target that won't be found (to hash all passwords)
        fake_target = b'\x00' * 16

        # Process in batches
        total_hashed = 0
        for i in range(0, len(test_passwords), self.batch_size):
            batch = test_passwords[i:i + self.batch_size]
            self._hash_batch_gpu(batch, fake_target)
            total_hashed += len(batch)

        elapsed = time.time() - start_time

        return {
            'total_hashes': total_hashed,
            'time': elapsed,
            'hashes_per_second': total_hashed / elapsed if elapsed > 0 else 0,
            'algorithm': self.hash_algorithm,
            'batch_size': self.batch_size
        }
