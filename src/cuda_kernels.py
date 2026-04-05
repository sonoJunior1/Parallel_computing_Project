"""
CUDA Kernels for GPU Password Cracking
Contains raw CUDA C code for MD5 hashing on GPU.
"""

# Complete MD5 implementation in CUDA
MD5_CUDA_KERNEL = r'''
extern "C" {

// MD5 Constants
#define S11 7
#define S12 12
#define S13 17
#define S14 22
#define S21 5
#define S22 9
#define S23 14
#define S24 20
#define S31 4
#define S32 11
#define S33 16
#define S34 23
#define S41 6
#define S42 10
#define S43 15
#define S44 21

// MD5 basic functions
#define F(x, y, z) (((x) & (y)) | ((~x) & (z)))
#define G(x, y, z) (((x) & (z)) | ((y) & (~z)))
#define H(x, y, z) ((x) ^ (y) ^ (z))
#define I(x, y, z) ((y) ^ ((x) | (~z)))

// Rotate left
#define ROTATE_LEFT(x, n) (((x) << (n)) | ((x) >> (32-(n))))

// MD5 transformations
#define FF(a, b, c, d, x, s, ac) { \
    (a) += F((b), (c), (d)) + (x) + (unsigned int)(ac); \
    (a) = ROTATE_LEFT((a), (s)); \
    (a) += (b); \
}

#define GG(a, b, c, d, x, s, ac) { \
    (a) += G((b), (c), (d)) + (x) + (unsigned int)(ac); \
    (a) = ROTATE_LEFT((a), (s)); \
    (a) += (b); \
}

#define HH(a, b, c, d, x, s, ac) { \
    (a) += H((b), (c), (d)) + (x) + (unsigned int)(ac); \
    (a) = ROTATE_LEFT((a), (s)); \
    (a) += (b); \
}

#define II(a, b, c, d, x, s, ac) { \
    (a) += I((b), (c), (d)) + (x) + (unsigned int)(ac); \
    (a) = ROTATE_LEFT((a), (s)); \
    (a) += (b); \
}

__device__ void md5_transform(unsigned int state[4], const unsigned char block[64]) {
    unsigned int a = state[0];
    unsigned int b = state[1];
    unsigned int c = state[2];
    unsigned int d = state[3];
    unsigned int x[16];

    // Decode input block into x
    for (int i = 0, j = 0; j < 64; i++, j += 4) {
        x[i] = ((unsigned int)block[j]) |
               (((unsigned int)block[j+1]) << 8) |
               (((unsigned int)block[j+2]) << 16) |
               (((unsigned int)block[j+3]) << 24);
    }

    // Round 1
    FF(a, b, c, d, x[ 0], S11, 0xd76aa478);
    FF(d, a, b, c, x[ 1], S12, 0xe8c7b756);
    FF(c, d, a, b, x[ 2], S13, 0x242070db);
    FF(b, c, d, a, x[ 3], S14, 0xc1bdceee);
    FF(a, b, c, d, x[ 4], S11, 0xf57c0faf);
    FF(d, a, b, c, x[ 5], S12, 0x4787c62a);
    FF(c, d, a, b, x[ 6], S13, 0xa8304613);
    FF(b, c, d, a, x[ 7], S14, 0xfd469501);
    FF(a, b, c, d, x[ 8], S11, 0x698098d8);
    FF(d, a, b, c, x[ 9], S12, 0x8b44f7af);
    FF(c, d, a, b, x[10], S13, 0xffff5bb1);
    FF(b, c, d, a, x[11], S14, 0x895cd7be);
    FF(a, b, c, d, x[12], S11, 0x6b901122);
    FF(d, a, b, c, x[13], S12, 0xfd987193);
    FF(c, d, a, b, x[14], S13, 0xa679438e);
    FF(b, c, d, a, x[15], S14, 0x49b40821);

    // Round 2
    GG(a, b, c, d, x[ 1], S21, 0xf61e2562);
    GG(d, a, b, c, x[ 6], S22, 0xc040b340);
    GG(c, d, a, b, x[11], S23, 0x265e5a51);
    GG(b, c, d, a, x[ 0], S24, 0xe9b6c7aa);
    GG(a, b, c, d, x[ 5], S21, 0xd62f105d);
    GG(d, a, b, c, x[10], S22, 0x02441453);
    GG(c, d, a, b, x[15], S23, 0xd8a1e681);
    GG(b, c, d, a, x[ 4], S24, 0xe7d3fbc8);
    GG(a, b, c, d, x[ 9], S21, 0x21e1cde6);
    GG(d, a, b, c, x[14], S22, 0xc33707d6);
    GG(c, d, a, b, x[ 3], S23, 0xf4d50d87);
    GG(b, c, d, a, x[ 8], S24, 0x455a14ed);
    GG(a, b, c, d, x[13], S21, 0xa9e3e905);
    GG(d, a, b, c, x[ 2], S22, 0xfcefa3f8);
    GG(c, d, a, b, x[ 7], S23, 0x676f02d9);
    GG(b, c, d, a, x[12], S24, 0x8d2a4c8a);

    // Round 3
    HH(a, b, c, d, x[ 5], S31, 0xfffa3942);
    HH(d, a, b, c, x[ 8], S32, 0x8771f681);
    HH(c, d, a, b, x[11], S33, 0x6d9d6122);
    HH(b, c, d, a, x[14], S34, 0xfde5380c);
    HH(a, b, c, d, x[ 1], S31, 0xa4beea44);
    HH(d, a, b, c, x[ 4], S32, 0x4bdecfa9);
    HH(c, d, a, b, x[ 7], S33, 0xf6bb4b60);
    HH(b, c, d, a, x[10], S34, 0xbebfbc70);
    HH(a, b, c, d, x[13], S31, 0x289b7ec6);
    HH(d, a, b, c, x[ 0], S32, 0xeaa127fa);
    HH(c, d, a, b, x[ 3], S33, 0xd4ef3085);
    HH(b, c, d, a, x[ 6], S34, 0x04881d05);
    HH(a, b, c, d, x[ 9], S31, 0xd9d4d039);
    HH(d, a, b, c, x[12], S32, 0xe6db99e5);
    HH(c, d, a, b, x[15], S33, 0x1fa27cf8);
    HH(b, c, d, a, x[ 2], S34, 0xc4ac5665);

    // Round 4
    II(a, b, c, d, x[ 0], S41, 0xf4292244);
    II(d, a, b, c, x[ 7], S42, 0x432aff97);
    II(c, d, a, b, x[14], S43, 0xab9423a7);
    II(b, c, d, a, x[ 5], S44, 0xfc93a039);
    II(a, b, c, d, x[12], S41, 0x655b59c3);
    II(d, a, b, c, x[ 3], S42, 0x8f0ccc92);
    II(c, d, a, b, x[10], S43, 0xffeff47d);
    II(b, c, d, a, x[ 1], S44, 0x85845dd1);
    II(a, b, c, d, x[ 8], S41, 0x6fa87e4f);
    II(d, a, b, c, x[15], S42, 0xfe2ce6e0);
    II(c, d, a, b, x[ 6], S43, 0xa3014314);
    II(b, c, d, a, x[13], S44, 0x4e0811a1);
    II(a, b, c, d, x[ 4], S41, 0xf7537e82);
    II(d, a, b, c, x[11], S42, 0xbd3af235);
    II(c, d, a, b, x[ 2], S43, 0x2ad7d2bb);
    II(b, c, d, a, x[ 9], S44, 0xeb86d391);

    state[0] += a;
    state[1] += b;
    state[2] += c;
    state[3] += d;
}

__device__ void md5_hash(const char* input, int length, unsigned char* output) {
    unsigned int state[4] = {0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476};
    unsigned char buffer[64];
    int i;

    // Process full 64-byte blocks
    int num_blocks = length / 64;
    for (int block = 0; block < num_blocks; block++) {
        md5_transform(state, (const unsigned char*)(input + block * 64));
    }

    // Handle remaining bytes and padding
    int remaining = length % 64;
    for (i = 0; i < remaining; i++) {
        buffer[i] = input[num_blocks * 64 + i];
    }

    // Append padding bit
    buffer[remaining] = 0x80;
    remaining++;

    // If not enough space for length, process this block and start new one
    if (remaining > 56) {
        for (i = remaining; i < 64; i++) {
            buffer[i] = 0;
        }
        md5_transform(state, buffer);
        remaining = 0;
    }

    // Pad with zeros
    for (i = remaining; i < 56; i++) {
        buffer[i] = 0;
    }

    // Append length in bits (little-endian)
    unsigned long long bit_length = (unsigned long long)length * 8;
    for (i = 0; i < 8; i++) {
        buffer[56 + i] = (bit_length >> (i * 8)) & 0xFF;
    }

    md5_transform(state, buffer);

    // Output hash (little-endian)
    for (i = 0; i < 4; i++) {
        output[i*4 + 0] = (state[i] >> 0) & 0xFF;
        output[i*4 + 1] = (state[i] >> 8) & 0xFF;
        output[i*4 + 2] = (state[i] >> 16) & 0xFF;
        output[i*4 + 3] = (state[i] >> 24) & 0xFF;
    }
}

__global__ void md5_crack_kernel(
    const unsigned char* passwords,      // Flattened password strings
    const int* lengths,         // Length of each password
    const int* offsets,         // Offset of each password in the flat array
    const unsigned char* target_hash,  // Target hash (16 bytes)
    int* found_index,           // Output: index of found password (-1 if not found)
    int num_passwords,
    int max_password_length
) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;

    if (idx < num_passwords) {
        unsigned char hash[16];
        int offset = offsets[idx];
        int length = lengths[idx];

        // Compute MD5 hash of this password
        md5_hash((const char*)(passwords + offset), length, hash);

        // Compare with target hash
        bool match = true;
        for (int i = 0; i < 16; i++) {
            if (hash[i] != target_hash[i]) {
                match = false;
                break;
            }
        }

        // If match found, atomically set the result
        if (match) {
            atomicCAS(found_index, -1, idx);
        }
    }
}

} // extern "C"
'''

def get_md5_kernel():
    """Return the MD5 CUDA kernel code."""
    return MD5_CUDA_KERNEL
