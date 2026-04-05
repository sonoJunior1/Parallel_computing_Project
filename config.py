"""
Configuration Settings
Global configuration for the password cracker.
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
WORDLIST_DIR = DATA_DIR / "wordlists"
RESULTS_DIR = DATA_DIR / "results"

# Ensure directories exist
WORDLIST_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Default settings
DEFAULT_HASH_ALGORITHM = "md5"
DEFAULT_CHARSET = "abcdefghijklmnopqrstuvwxyz0123456789"
DEFAULT_MAX_LENGTH = 5

# CPU Parallel settings
DEFAULT_CPU_WORKERS = os.cpu_count()

# GPU settings
DEFAULT_GPU_BATCH_SIZE = 1000000  # 1 million passwords per batch
GPU_MEMORY_LIMIT = 0.8  # Use up to 80% of GPU memory

# Benchmark settings
BENCHMARK_ITERATIONS = 3  # Number of times to run each benchmark
BENCHMARK_WARMUP = 1  # Number of warmup runs before timing

# Hash algorithms supported
SUPPORTED_ALGORITHMS = ["md5", "sha256", "sha1"]

# Character sets
CHARSET_LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
CHARSET_UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CHARSET_DIGITS = "0123456789"
CHARSET_ALPHANUMERIC = CHARSET_LOWERCASE + CHARSET_UPPERCASE + CHARSET_DIGITS
CHARSET_SPECIAL = "!@#$%^&*()-_=+[]{}|;:,.<>?/"
CHARSET_ALL = CHARSET_ALPHANUMERIC + CHARSET_SPECIAL
