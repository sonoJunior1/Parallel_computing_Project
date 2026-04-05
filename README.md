# GPU-Accelerated Password Cracker

A parallel computing project demonstrating GPU acceleration benefits for password cracking, comparing CPU sequential, CPU parallel, and GPU implementations.

## Project Overview

This project implements password cracking using multiple approaches:
- **CPU Sequential**: Baseline single-threaded implementation
- **CPU Parallel**: Multi-process parallelization using Python multiprocessing
- **GPU Accelerated**: CUDA-based GPU implementation using CuPy

## Hardware

- **GPU**: NVIDIA GeForce RTX 3060 (3584 CUDA cores, 6GB GDDR6)
- **CUDA**: Version 12.4
- **Driver**: 550.163.01

## Features

- Multiple hash algorithms (MD5, SHA-256)
- Brute force and dictionary attacks
- Performance benchmarking and comparison
- Visualization of performance metrics
- Scalability analysis across different problem sizes

## Project Structure

```
GPU_Password_Cracker/
├── src/                    # Source code
│   ├── cpu_sequential.py   # CPU baseline implementation
│   ├── cpu_parallel.py     # Multiprocessing implementation
│   ├── gpu_cuda.py         # GPU CUDA implementation
│   ├── hash_functions.py   # Hash utilities
│   └── password_generator.py
├── benchmarks/             # Benchmarking framework
│   ├── benchmark_runner.py
│   ├── performance_analyzer.py
│   └── visualizer.py
├── data/                   # Data directory
│   ├── wordlists/         # Password wordlists
│   └── results/           # Benchmark results
├── tests/                 # Unit tests
├── notebooks/             # Jupyter notebooks for analysis
├── app.py                 # Main CLI application
├── config.py              # Configuration
└── requirements.txt       # Dependencies
```

## Installation

1. Install CUDA Toolkit 12.4 (already installed)

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
# Run the main application
python app.py

# Run benchmarks
python -m benchmarks.benchmark_runner

# Run tests
pytest tests/
```

## Performance Goals

- Demonstrate significant GPU speedup vs CPU implementations
- Analyze scalability across different password lengths
- Compare MD5 vs SHA-256 performance characteristics
- Evaluate impact of optimization strategies

## Educational Purpose

This project is for educational purposes only, demonstrating:
- Parallel computing concepts
- GPU programming with CUDA
- Performance optimization techniques
- Cryptographic hash functions

**Warning**: Only use on systems and data you own or have explicit permission to test.

## License

Educational/Academic Use Only
