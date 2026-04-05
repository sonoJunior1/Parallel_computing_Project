# GPU Password Cracker - Project Summary

## 📁 Project Structure

```
GPU_Password_Cracker/
├── app.py                      # Main GUI application
├── src/
│   ├── cpu_sequential.py       # CPU sequential implementation
│   ├── cpu_parallel.py         # CPU parallel (multiprocessing)
│   ├── gpu_cuda.py             # GPU CUDA implementation
│   ├── cuda_kernels.py         # Custom MD5 CUDA kernel (250+ lines)
│   ├── hash_functions.py       # Hash utilities (MD5, SHA-1, SHA-256)
│   └── password_generator.py   # Brute force generator
├── data/
│   └── wordlists/
│       └── rockyou.txt         # 14.3M password wordlist
├── CLASS_PRESENTATION.md       # Complete presentation guide
├── PERFORMANCE_NOTES.md        # Detailed performance analysis
├── README.md                   # Project documentation
└── requirements.txt            # Python dependencies
```

## 🚀 Quick Start

### Run the GUI
```bash
python3 app.py
```

### Features
- Modern dark-themed GUI
- Real-time performance comparison
- Dataset size slider (10k to 14.3M passwords)
- 4-panel detailed performance analysis charts
- Support for MD5, SHA-1, SHA-256 (GPU only supports MD5)
- Dictionary attack with RockyOU wordlist
- Brute force attack mode

## 📊 Key Results

**Full RockyOU Dataset (14,344,380 passwords):**

| Implementation | Time | Hash Rate | Speedup |
|----------------|------|-----------|---------|
| **GPU CUDA** | **2.66s** | **5.4M h/s** | **2.33x** |
| CPU Parallel (8 cores) | 4.25s | 3.4M h/s | 1.46x |
| CPU Sequential | 6.19s | 2.3M h/s | 1.00x |

## 🎯 Project Goals Achieved

✅ Implemented custom CUDA MD5 kernel from scratch (educational)
✅ Demonstrated serial vs parallel performance differences
✅ Achieved realistic 2.33x GPU speedup for MD5
✅ Explained Amdahl's Law with actual results
✅ Professional GUI with real-time visualization
✅ Handled UTF-8 encoding challenges
✅ Comprehensive presentation materials

## 💻 Hardware Used

- **GPU**: NVIDIA RTX 3060
  - 3,584 CUDA cores
  - 12GB GDDR6
  - Compute Capability 8.6

## 🧠 Key Concepts Demonstrated

1. **Amdahl's Law**: Serial portions limit parallelization (2.33x vs theoretical 20x)
2. **Memory-Bound vs Compute-Bound**: MD5 is memory-bound (realistic 2-5x speedup)
3. **GPU Overhead**: Startup costs require large datasets (GPU slower on < 50k items)
4. **Data Parallelism**: Same operation on different data (SIMD on steroids)
5. **Atomic Operations**: Thread-safe result reporting with `atomicCAS`
6. **UTF-8 Encoding**: Byte-level operations require byte lengths (not character counts)

## 🔧 Technical Highlights

### CUDA Kernel
- Custom MD5 implementation (250+ lines of CUDA C)
- Batch processing (100k passwords per batch)
- Flattened memory layout for GPU efficiency
- Thread-safe result reporting with atomic operations

### Critical Bugs Fixed
1. **UTF-8 byte length**: Characters like `¡` are 2 bytes, not 1 character
2. **Atomic operations**: Changed from `atomicMin` to `atomicCAS` for correctness
3. **Encoding issues**: Mixed latin-1/UTF-8 in RockyOU wordlist

## 📚 Documentation

- **CLASS_PRESENTATION.md**: Complete guide for class presentation
  - Performance explanations
  - Amdahl's Law breakdown
  - Demo talking points
  - Anticipated Q&A

- **PERFORMANCE_NOTES.md**: Technical performance analysis
  - GPU characteristics
  - Scalability analysis
  - Optimization strategies

- **README.md**: General project documentation

## 🎓 Educational Value

This project demonstrates that **GPU acceleration is not magic** - it's a tool with specific use cases:

- **When to use GPU**: Large datasets, compute-intensive operations, embarrassingly parallel
- **When NOT to use GPU**: Small datasets, memory-bound operations, sequential dependencies
- **Realistic expectations**: 2-5x for MD5, 50-100x for complex hashes like bcrypt

**Achievement**: Real speedup 2.33x | Educational value 100x 🎓

## 📝 Notes for Presentation

1. Start with 10k dataset - show GPU is **slower** (explain overhead)
2. Move slider to 100k - show GPU catching up
3. Run full 14.3M - show **2.33x speedup**
4. Explain why this is realistic (memory-bound, Amdahl's Law)
5. Show 4-panel charts for detailed analysis

## 🔒 Ethics & Legal

This tool is for:
- Authorized security testing
- Password recovery (your own data)
- CTF competitions
- Educational purposes
- Academic research

**Never use on systems you don't own or have explicit permission to test!**

---

**Course**: Parallel Computing
**Hardware**: NVIDIA RTX 3060 (3,584 CUDA cores)
**Dataset**: RockyOU (14.3M passwords)
**Result**: 2.33x GPU speedup (realistic for memory-bound MD5)
