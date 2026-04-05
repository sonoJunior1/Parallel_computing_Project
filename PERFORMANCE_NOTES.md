# GPU Password Cracker - Performance Analysis

## Key Performance Characteristics

### GPU Startup Overhead

GPUs have inherent startup overhead that includes:
1. **Kernel compilation** (~100-500ms first time, cached afterwards)
2. **Memory allocation** on GPU (~5-20ms)
3. **Data transfer** CPU → GPU and GPU → CPU
4. **Kernel launch latency** (~10-50μs per launch)

### Performance by Dataset Size

#### Small Datasets (< 50,000 passwords)
- **GPU**: Startup overhead dominates execution time
- **Result**: CPU often faster than GPU
- **Example**: 10,000 passwords
  - GPU: ~596k hashes/sec
  - CPU Sequential: ~2.2M hashes/sec
  - **Winner**: CPU ✓

#### Medium Datasets (50k - 1M passwords)
- **GPU**: Overhead becomes smaller percentage of total time
- **Result**: GPU starts to show advantage
- **Example**: 100,000 passwords
  - GPU: ~2-3M hashes/sec
  - CPU Sequential: ~2.2M hashes/sec
  - **Winner**: Depends on implementation

#### Large Datasets (> 1M passwords)
- **GPU**: Massive parallelism shines, overhead is negligible
- **Result**: GPU significantly faster
- **Example**: 14,344,380 passwords (full rockyou.txt)
  - **GPU**: **5.4M hashes/sec** ⚡
  - CPU Parallel (8 cores): 3.4M hashes/sec
  - CPU Sequential: 2.3M hashes/sec
  - **Speedup**: **2.33x faster than CPU sequential**

## Why This Happens

### GPU Architecture
- **3,584 CUDA cores** (RTX 3060) can process many passwords in parallel
- Each core is simpler/slower than CPU core
- Advantage comes from **massive parallelism**, not individual core speed

### Memory Bandwidth
- **Memory transfer** takes time:
  - 14.3M passwords ≈ 150MB of data
  - PCIe bandwidth: ~16 GB/s (theoretical)
  - Actual transfer: ~5-10 GB/s
  - Transfer time: ~15-30ms for 150MB

### Amdahl's Law
The speedup is limited by:
- **Serial portions**: Memory transfer, kernel launch
- **Parallel portions**: Actual MD5 hashing

Formula: `Speedup = 1 / ((1 - P) + P/N)`
- P = Parallelizable portion (~95% for password cracking)
- N = Number of parallel units (3584 CUDA cores)
- Theoretical max: ~20x
- Actual: ~2-3x due to memory bandwidth limits

## Optimization Strategies Implemented

### 1. Batch Processing
- Process passwords in batches of 100,000
- Reduces number of kernel launches
- Amortizes overhead across many passwords

### 2. Flattened Memory Layout
- Store all passwords in single contiguous array
- Use offset array to locate each password
- **Critical fix**: Use **byte length** not character length (for UTF-8)

### 3. Atomic Operations
- Use `atomicCAS` (Compare-And-Swap) instead of `atomicMin`
- Only first thread to find match writes result
- Prevents race conditions

### 4. Character Encoding
- **UTF-8 multi-byte characters** (¡, é, ñ, etc.)
- Characters like `¡` = 2 bytes in UTF-8
- Must use `len(password.encode('utf-8'))` not `len(password)`
- **Bug**: Using character length truncated passwords with special chars

## Real-World Performance

### Test Case: Password "abygurl69"
- Hash: `b5ef37e9b4b066f667dd5b635f48495a`
- Position in rockyou.txt: 14,344,378 / 14,344,380 (last 3 passwords!)

| Implementation | Time | Hash Rate | Speedup |
|----------------|------|-----------|---------|
| GPU CUDA | 2.66s | 5,395,301 h/s | 2.33x |
| CPU Parallel (8) | 4.25s | 3,376,949 h/s | 1.46x |
| CPU Sequential | 6.19s | 2,317,838 h/s | 1.00x |

### Realistic Expectations

**NOT** 50-100x speedup because:
- MD5 is memory-bound, not compute-bound
- Memory bandwidth limits throughput
- PCIe transfer overhead
- Small individual work items (MD5 is fast)

**Typical** password cracking speedups:
- Dictionary attack: 2-5x (this project: **2.33x** ✓)
- Brute force: 5-20x (more compute-intensive)
- Complex hashes (bcrypt, scrypt): 50-100x

## Lessons for Parallel Computing Class

1. **Problem Size Matters**: GPUs need large datasets to overcome overhead
2. **Memory vs Compute**: Know if your problem is memory-bound or compute-bound
3. **Overhead Analysis**: Fixed costs (startup) vs variable costs (computation)
4. **Amdahl's Law**: Serial portions limit speedup potential
5. **Real vs Theoretical**: Theoretical speedup ≠ actual speedup
6. **Data Transfer**: Moving data can be as expensive as computing
7. **Character Encoding**: Byte-level operations require byte-accurate lengths
8. **Atomic Operations**: Critical for thread-safe result handling

## Scalability Analysis

Tested password lengths and charsets:

1. **4-digit numeric** (10,000 combinations)
   - Small dataset → CPU faster

2. **4-char alphanumeric** (1,679,616 combinations)
   - Medium dataset → GPU competitive

3. **5-char lowercase** (11,881,376 combinations)
   - Large dataset → GPU faster

4. **Full rockyou.txt** (14,344,380 passwords)
   - Very large dataset → **GPU 2.33x faster** ✓

## Conclusion

This project demonstrates that:
- GPU acceleration provides **realistic 2-3x speedup** for MD5 dictionary attacks
- Performance matches expectations for memory-bound workloads
- Implementation correctly handles UTF-8 multi-byte characters
- Proper atomic operations ensure thread-safe results
- Educational value: Understanding when/why to use GPU parallelism
