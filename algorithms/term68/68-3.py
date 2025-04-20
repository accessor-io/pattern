import hashlib
import math

# Secp256k1 constants
N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
P = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
Gx = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8

# Sequence values
T1 = int("1a838b13505b26867", 16)
T2 = int("2832ed74f2b5e35ee", 16)
T3 = int("730fc235c1942c1ae", 16)
T6 = int("349b84b6431a6c4ef1", 16)

# Public key hashes (hash160) for T4 and T5 (target hashes, not addresses)
T4_hash160 = bytes.fromhex("e0b8a2baee1b77fc703455f39d51477451fc8cfc")  # Matches address 1MsXqaX...
T5_hash160 = bytes.fromhex("61eb8a50c86b0584bb727dd65bed8d2400d6d5aa")  # Matches address 1A1zP1e...

# Hardcoded RIPEMD-160 implementation
def rol(n, rotations, width=32):
    return ((n << rotations) | (n >> (width - rotations))) & ((1 << width) - 1)

def f(j, x, y, z):
    if j < 16: return x ^ y ^ z
    elif j < 32: return (x & y) | (~x & z)
    elif j < 48: return (x | ~y) ^ z
    elif j < 64: return (x & z) | (y & ~z)
    else: return x ^ (y | ~z)

def ripemd160(data):
    h = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xc3d2e1f0]
    s = [11, 14, 15, 12, 5, 8, 7, 9, 11, 13, 14, 15, 6, 7, 9, 8,
         7, 6, 8, 9, 11, 15, 13, 14, 7, 6, 9, 8, 13, 11, 12, 14,
         12, 15, 5, 7, 9, 11, 8, 6, 13, 14, 7, 9, 12, 15, 5, 11,
         9, 14, 15, 5, 7, 6, 8, 13, 11, 12, 14, 15, 5, 8, 6, 13,
         9, 13, 6, 14, 15, 11, 7, 12, 5, 8, 13, 14, 6, 9, 15, 11]
    k = [0, 0x5a827999, 0x6ed9eba1, 0x8f1bbcdc, 0xa953fd4e]
    kp = [0x50a28be6, 0x5c4dd124, 0x6d703ef3, 0x7a6d76e9, 0]

    msg = bytearray(data)
    orig_len = len(msg) * 8
    msg.append(0x80)
    while (len(msg) * 8) % 512 != 448:
        msg.append(0)
    msg += (orig_len & 0xffffffffffffffff).to_bytes(8, "little")

    for i in range(0, len(msg), 64):
        block = msg[i:i+64]
        w = [int.from_bytes(block[j:j+4], "little") for j in range(0, 64, 4)]
        a, b, c, d, e = h
        ap, bp, cp, dp, ep = h
        for j in range(80):
            t = rol(a + f(j, b, c, d) + w[(j % 16) ^ (j // 16)] + k[j // 16], s[j]) + e
            a, b, c, d, e = e, t, b, rol(c, 10), d
            tp = rol(ap + f(79 - j, bp, cp, dp) + w[(j % 16) ^ (79 - j) // 16] + kp[j // 16], s[79 - j]) + ep
            ap, bp, cp, dp, ep = ep, tp, bp, rol(cp, 10), dp
        h = [(h[i] + x + y) & 0xffffffff for i, (x, y) in enumerate(zip((a, b, c, d, e), (ap, bp, cp, dp, ep)))]
    return bytes().join(x.to_bytes(4, "little") for x in h)

def mod_inverse(a, m):
    def egcd(a, b):
        if a == 0: return b, 0, 1
        gcd, x, y = egcd(b % a, a)
        return gcd, y - (b // a) * x, x
    _, x, _ = egcd(a % m, m)
    return x % m

def ec_double(x, y):
    l = ((3 * x * x) * mod_inverse(2 * y, P)) % P
    x3 = (l * l - 2 * x) % P
    y3 = (l * (x - x3) - y) % P
    return x3, y3

def ec_add(x1, y1, x2, y2):
    if x1 == x2 and y1 == y2: return ec_double(x1, y1)
    l = ((y2 - y1) * mod_inverse(x2 - x1, P)) % P
    x3 = (l * l - x1 - x2) % P
    y3 = (l * (x1 - x3) - y1) % P
    return x3, y3

def ec_mult(k, x=Gx, y=Gy):
    k = k % N
    rx, ry = x, y
    qx, qy = None, None
    while k:
        if k & 1:
            qx, qy = (rx, ry) if qx is None else ec_add(qx, qy, rx, ry)
        rx, ry = ec_double(rx, ry)
        k >>= 1
    return qx, qy

def private_to_public(private_key):
    x, y = ec_mult(private_key)
    prefix = b'\x02' if y % 2 == 0 else b'\x03'
    x_bytes = x.to_bytes(32, "big")
    return prefix + x_bytes

def compute_hash160(pubkey_bytes):
    sha256 = hashlib.sha256(pubkey_bytes).digest()
    return ripemd160(sha256)

def solve_missing_keys():
    d1 = T2 - T1
    d2 = T3 - T2
    d_avg = (T6 - T3) // 3

    print(f"Estimated increments: d1={hex(d1)}, d2={hex(d2)}, d_avg={hex(d_avg)}")
    print(f"Search range: {hex(T3)} to {hex(T6)}")

    current_key = T3
    step = d_avg
    found_t4 = None
    found_t5 = None

    # Bit length boundaries (2^67 to 2^69)
    BIT_68_MAX = (1 << 68) - 1
    BIT_69_MAX = (1 << 69) - 1

    while current_key <= T6 and (found_t4 is None or found_t5 is None):
        # Enforce bit length constraints
        if found_t4 is None and not (T3 <= current_key <= BIT_68_MAX):
            current_key = min(max(current_key, T3), BIT_68_MAX)
        elif found_t5 is None and not (found_t4 < current_key <= min(T6, BIT_69_MAX)):
            current_key = min(max(current_key, found_t4 + 1), min(T6, BIT_69_MAX))

        pubkey_bytes = private_to_public(current_key)
        hash160 = compute_hash160(pubkey_bytes)

        if hash160 == T4_hash160:
            print(f"T4 found: {hex(current_key)}")
            found_t4 = current_key
        elif hash160 == T5_hash160 and found_t4 is not None:
            print(f"T5 found: {hex(current_key)}")
            found_t5 = current_key
            break

        # Adjusted step handling with bit length awareness
        current_key += step
        if current_key > (BIT_68_MAX if found_t4 is None else BIT_69_MAX):
            print("Adjusting step for bit boundary...")
            step = max(1, step // 2)
            current_key = (T3 if found_t4 is None else found_t4 + 1)

    if found_t4 and found_t5:
        print(f"T4 = {hex(found_t4)}, T5 = {hex(found_t5)}")
        d3 = found_t4 - T3
        d4 = found_t5 - found_t4
        d5 = T6 - found_t5
        print(f"Increments: T4-T3={hex(d3)}, T5-T4={hex(d4)}, T6-T5={hex(d5)}")
        return found_t4, found_t5
    else:
        print("Could not find both T4 and T5.")
        return None, None

def main():
    print("Solving for T4 and T5 with hash160 targets...")
    t4, t5 = solve_missing_keys()
    if t4 and t5:
        print(f"Final solution: T4 = {hex(t4)}, T5 = {hex(t5)}")
        for key, expected_hash in [(t4, T4_hash160), (t5, T5_hash160)]:
            pubkey = private_to_public(key)
            assert compute_hash160(pubkey) == expected_hash, f"Hash mismatch for {hex(key)}"
            print(f"Verified: {hex(key)} matches hash160 {expected_hash.hex()}")

def is_valid_frame_marker(self, candidate, expected_marker):
    """Enhanced frame marker validation with position awareness"""
    # Convert marker to integer pattern
    marker_int = int.from_bytes(expected_marker, 'big')
    marker_bits = len(expected_marker) * 8
    
    # Check marker appears in first 8 bytes with proper alignment
    candidate_bytes = candidate.to_bytes(32, 'big')
    header = candidate_bytes[:8]
    
    # Create bitmask for marker position (first 4 bytes)
    mask = (1 << (len(expected_marker)*8)) - 1
    header_part = int.from_bytes(header, 'big') >> (64 - marker_bits)
    
    return (header_part & mask) == marker_int

def handle_policy_violation(self):
    """Enhanced handler for frame marker violations"""
    # Analyze current state bits to avoid bad patterns
    bad_bits = self.current_state & 0xFFFF
    self.current_state ^= bad_bits << 48  # XOR to break repeating patterns
    self.current_state += int(math.sqrt(self.current_state)) % 0xFF
    
def generate_candidate(self):
    """Modified candidate generation with marker preservation"""
    # Existing Fibonacci-prime logic...
    candidate = self.current_state + (self.deltas['d_avg'] * fib_step // prime_adjustment)
    
    # Enforce marker bits before applying constraints
    if not self.found_terms['T4']:
        marker = WS_FRAME_MARKERS[68]
        marker_int = int.from_bytes(marker, 'big')
        candidate = (candidate & ~0xFFFF) | marker_int
    elif not self.found_terms['T5']: 
        marker = WS_FRAME_MARKERS[69]
        marker_int = int.from_bytes(marker, 'big')
        candidate = (candidate & ~0x1FFFF) | (marker_int << 8)
    
    return self.apply_protocol_constraints(candidate)

def next_candidate(self, last_candidate):
    """Improved stepping to avoid oscillation patterns"""
    # Use triangular number stepping to prevent repeating intervals
    step_num = int(math.sqrt(2*last_candidate)) % 256
    step = (step_num * (step_num + 1)) // 2
    return last_candidate + (step if step % 2 else -step)

if __name__ == "__main__":
    main()