"""Pure Python implementation of the RIPEMD160 algorithm.

This implementation does not rely on any external libraries or system dependencies.
It is based on the RIPEMD160 specification and various open source implementations.
"""

# Initial values for RIPEMD160
h0 = 0x67452301
h1 = 0xEFCDAB89
h2 = 0x98BADCFE
h3 = 0x10325476
h4 = 0xC3D2E1F0

# Constants
K = [0x00000000, 0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xA953FD4E]
KK = [0x50A28BE6, 0x5C4DD124, 0x6D703EF3, 0x7A6D76E9, 0x00000000]

# Message schedule
r = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    7, 4, 13, 1, 10, 6, 15, 3, 12, 0, 9, 5, 2, 14, 11, 8,
    3, 10, 14, 4, 9, 15, 8, 1, 2, 7, 0, 6, 13, 11, 5, 12,
    1, 9, 11, 10, 0, 8, 12, 4, 13, 3, 7, 15, 14, 5, 6, 2,
    4, 0, 5, 9, 7, 12, 2, 10, 14, 1, 3, 8, 11, 6, 15, 13
]

rr = [
    5, 14, 7, 0, 9, 2, 11, 4, 13, 6, 15, 8, 1, 10, 3, 12,
    6, 11, 3, 7, 0, 13, 5, 10, 14, 15, 8, 12, 4, 9, 1, 2,
    15, 5, 1, 3, 7, 14, 6, 9, 11, 8, 12, 2, 10, 0, 4, 13,
    8, 6, 4, 1, 3, 11, 15, 0, 5, 12, 2, 13, 9, 7, 10, 14,
    12, 15, 10, 4, 1, 5, 8, 7, 6, 2, 13, 14, 0, 3, 9, 11
]

s = [
    11, 14, 15, 12, 5, 8, 7, 9, 11, 13, 14, 15, 6, 7, 9, 8,
    7, 6, 8, 13, 11, 9, 7, 15, 7, 12, 15, 9, 11, 7, 13, 12,
    11, 13, 6, 7, 14, 9, 13, 15, 14, 8, 13, 6, 5, 12, 7, 5,
    11, 12, 14, 15, 14, 15, 9, 8, 9, 14, 5, 6, 8, 6, 5, 12,
    9, 15, 5, 11, 6, 8, 13, 12, 5, 12, 13, 14, 11, 8, 5, 6
]

ss = [
    8, 9, 9, 11, 13, 15, 15, 5, 7, 7, 8, 11, 14, 14, 12, 6,
    9, 13, 15, 7, 12, 8, 9, 11, 7, 7, 12, 7, 6, 15, 13, 11,
    9, 7, 15, 11, 8, 6, 6, 14, 12, 13, 5, 14, 13, 13, 7, 5,
    15, 5, 8, 11, 14, 14, 6, 14, 6, 9, 12, 9, 12, 5, 15, 8,
    8, 5, 12, 9, 12, 5, 14, 6, 8, 13, 6, 5, 15, 13, 11, 11
]

def rol(n, b):
    """Left rotate a 32-bit integer n by b bits."""
    return ((n << b) | (n >> (32 - b))) & 0xffffffff

def f(j, x, y, z):
    """The f functions."""
    if 0 <= j <= 15:
        return x ^ y ^ z
    elif 16 <= j <= 31:
        return (x & y) | (~x & z)
    elif 32 <= j <= 47:
        return (x | ~y) ^ z
    elif 48 <= j <= 63:
        return (x & z) | (y & ~z)
    elif 64 <= j <= 79:
        return x ^ (y | ~z)
    else:
        return 0

def ripemd160(message):
    """Core RIPEMD160 algorithm."""
    if isinstance(message, str):
        message = message.encode()

    h = [h0, h1, h2, h3, h4]  # Initialize state
    length = len(message)
    
    # Pre-processing: padding
    message += b'\x80'
    while (len(message) + 8) % 64 != 0:
        message += b'\x00'
    
    message += length.to_bytes(8, byteorder='little')
    
    # Process message in 64-byte chunks
    for chunk_start in range(0, len(message), 64):
        chunk = message[chunk_start:chunk_start + 64]
        
        # Break chunk into sixteen 32-bit words
        X = [int.from_bytes(chunk[i:i+4], byteorder='little') 
             for i in range(0, 64, 4)]
        
        # Initialize working variables
        A = h[0]
        B = h[1]
        C = h[2]
        D = h[3]
        E = h[4]
        AA = A
        BB = B
        CC = C
        DD = D
        EE = E
        
        # Main loop
        for j in range(80):
            T = (rol(A + f(j, B, C, D) + X[r[j]] + K[j//16], s[j]) + E) & 0xffffffff
            A = E
            E = D
            D = rol(C, 10)
            C = B
            B = T
            T = (rol(AA + f(79-j, BB, CC, DD) + X[rr[j]] + KK[j//16], ss[j]) + EE) & 0xffffffff
            AA = EE
            EE = DD
            DD = rol(CC, 10)
            CC = BB
            BB = T
        
        # Final additions
        T = (h[1] + C + DD) & 0xffffffff
        h[1] = (h[2] + D + EE) & 0xffffffff
        h[2] = (h[3] + E + AA) & 0xffffffff
        h[3] = (h[4] + A + BB) & 0xffffffff
        h[4] = (h[0] + B + CC) & 0xffffffff
        h[0] = T
    
    # Produce final hash value
    result = b''
    for x in h:
        result += x.to_bytes(4, byteorder='little')
    return result

def hexdigest(message):
    """Return the RIPEMD160 hash as a hexadecimal string."""
    return ripemd160(message).hex() 