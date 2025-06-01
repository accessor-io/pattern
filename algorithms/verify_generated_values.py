#!/usr/bin/env python3
"""
Verify if the GENERATED values in verified_bitcoin_sequence.txt
produce the correct Bitcoin addresses.
"""

import hashlib
import ecdsa

# Bitcoin elliptic curve parameters
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

# Expected Bitcoin addresses
EXPECTED_ADDRESSES = {
    71: "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU",
    72: "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR",
    73: "12VVRNPi4SJqUTsp6FmqDqY5sGosDtysn4",
    74: "1FWGcVDK3JGzCC3WtkYetULPszMaK2Jksv",
    76: "1DJh2eHFYQfACPmrvpyWc8MSTYKh7w9eRF",
    77: "1Bxk4CQdqL9p22JEtDfdXMsng1XacifUtE",
    78: "15qF6X51huDjqTmF9BJgxXdt1xcj46Jmhb",
    79: "1ARk8HWJMn8js8tQmGUJeQHjSE7KRkn2t8",
}

# GENERATED values from the file
GENERATED_KEYS = {
    71: 0x6937096c8634d89de4,
    72: 0xd26e12d90c69b13bcb,
    73: 0x2774a388b253d13b361,
    74: 0x765dea9a16fb73b1a22,
    76: 0xe516a33d393e39a4a12,
    77: 0x2af43e9b7abbaacede32,
    78: 0x80dcbbd27033006c9a91,
    79: 0x18296337750990145cfad,
}

# Custom RIPEMD160 implementation
def rol(n, rotations, width=32):
    return ((n << rotations) | (n >> (width - rotations))) & ((1 << width) - 1)

def f(j, x, y, z):
    if j < 16: return x ^ y ^ z
    elif j < 32: return (x & y) | (~x & z)
    elif j < 48: return (x | ~y) ^ z
    elif j < 64: return (x & z) | (y & ~z)
    else: return x ^ (y | ~z)

def custom_ripemd160(data):
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
            word_idx = (j % 16)
            round_num = j // 16
            round_num_p = (79 - j) // 16
            
            T = rol(a + f(j, b, c, d) + w[word_idx] + k[round_num], s[j]) + e
            a, b, c, d, e = e, T, b, rol(c, 10), d

            def fp(j, x, y, z):
                jp = 79 - j
                if jp < 16: return x ^ y ^ z
                elif jp < 32: return (x & z) | (y & ~z)
                elif jp < 48: return (x | ~y) ^ z
                elif jp < 64: return (x & y) | (~x & z)
                else: return x ^ (y | ~z)

            word_idx_p = (j % 16) ^ ((79-j) // 16)
            Tp = rol(ap + fp(j, bp, cp, dp) + w[word_idx_p] + kp[round_num_p], s[79 - j]) + ep
            ap, bp, cp, dp, ep = ep, Tp, bp, rol(cp, 10), dp

        dh = [h[1], h[2], h[3], h[4], h[0]]
        h[0] = (dh[0] + c + dp) & 0xffffffff
        h[1] = (dh[1] + d + ep) & 0xffffffff
        h[2] = (dh[2] + e + ap) & 0xffffffff
        h[3] = (dh[3] + a + bp) & 0xffffffff
        h[4] = (dh[4] + b + cp) & 0xffffffff

    return bytes().join(x.to_bytes(4, "little") for x in h)

# Base58 encoding
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def base58_encode(b):
    n = int.from_bytes(b, 'big')
    if n == 0:
        return BASE58_ALPHABET[0] * len(b)
    res = []
    while n > 0:
        n, rem = divmod(n, 58)
        res.append(BASE58_ALPHABET[rem])
    res = "".join(reversed(res))
    czero = 0
    while czero < len(b) and b[czero] == 0:
        res = BASE58_ALPHABET[0] + res
        czero += 1
    return res

def base58_check_encode(version, payload):
    versioned = version + payload
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    return base58_encode(versioned + checksum)

# EC operations
def multiply(p, n):
    """Scalar multiplication of point p by integer n"""
    if n == 0 or p is None:
        return None
    if n < 0:
        return multiply(ecdsa.ellipticcurve.Point(CURVE, p.x(), (-p.y()) % P), -n)
    r = None
    m2 = p
    bit_length = n.bit_length()
    for i in range(bit_length):
        if n & (1 << i):
            if r is None:
                r = m2
            else:
                # Point addition
                if r.x() == m2.x():
                    if (r.y() + m2.y()) % P == 0:
                        r = None
                        continue
                    # Point doubling
                    numerator = (3 * r.x() * r.x()) % P
                    denominator = (2 * r.y()) % P
                    lam = (numerator * pow(denominator, P - 2, P)) % P
                else:
                    lam = ((m2.y() - r.y()) * pow(m2.x() - r.x(), P - 2, P)) % P
                x3 = (lam * lam - r.x() - m2.x()) % P
                y3 = (lam * (r.x() - x3) - r.y()) % P
                r = ecdsa.ellipticcurve.Point(CURVE, x3, y3)
        # Point doubling
        if m2 is not None:
            numerator = (3 * m2.x() * m2.x()) % P
            denominator = (2 * m2.y()) % P
            if denominator != 0:
                lam = (numerator * pow(denominator, P - 2, P)) % P
                x3 = (lam * lam - 2 * m2.x()) % P
                y3 = (lam * (m2.x() - x3) - m2.y()) % P
                m2 = ecdsa.ellipticcurve.Point(CURVE, x3, y3)
            else:
                m2 = None
    return r

# Create curve and generator
CURVE = ecdsa.ellipticcurve.CurveFp(P, 0, 7)
GENERATOR = ecdsa.ellipticcurve.Point(CURVE, Gx, Gy)

def privkey_to_address(privkey_int):
    """Convert private key to Bitcoin address"""
    # Get public key
    pubkey_point = multiply(GENERATOR, privkey_int)
    if pubkey_point is None:
        return None
    
    # Uncompressed public key
    pubkey_bytes = b'\x04' + pubkey_point.x().to_bytes(32, 'big') + pubkey_point.y().to_bytes(32, 'big')
    
    # Hash160 (SHA256 then RIPEMD160)
    sha256_hash = hashlib.sha256(pubkey_bytes).digest()
    ripemd160_hash = custom_ripemd160(sha256_hash)
    
    # Create address
    return base58_check_encode(b'\x00', ripemd160_hash)

print("=== VERIFYING GENERATED VALUES ===")
print()

all_correct = True

for pos in sorted(GENERATED_KEYS.keys()):
    privkey = GENERATED_KEYS[pos]
    expected_address = EXPECTED_ADDRESSES[pos]
    
    # Generate address from private key
    generated_address = privkey_to_address(privkey)
    
    # Check if it matches
    match = generated_address == expected_address
    status = "✓ CORRECT" if match else "✗ INCORRECT"
    
    print(f"Position {pos}:")
    print(f"  Private key: 0x{privkey:064x}")
    print(f"  Generated address: {generated_address}")
    print(f"  Expected address:  {expected_address}")
    print(f"  Status: {status}")
    
    if not match:
        all_correct = False
    
    # Also calculate the constant (difference from previous position)
    if pos > 1:
        # Get previous key from file
        prev_key = None
        if pos - 1 in GENERATED_KEYS:
            prev_key = GENERATED_KEYS[pos - 1]
        elif pos == 71:
            # Position 70 is known
            prev_key = 0x349b84b6431a6c4ef1
        elif pos == 76:
            # Position 75 is known
            prev_key = 0x4c5ce114686a1336e07
            
        if prev_key:
            constant = privkey - prev_key
            print(f"  Constant (diff from pos {pos-1}): {constant:,}")
    print()

if all_correct:
    print("✓ ALL GENERATED VALUES ARE CORRECT!")
else:
    print("✗ Some generated values are incorrect.")

# Output the constants for copying into the main script
print("\n=== CONSTANTS TO ADD TO large_constants LIST ===")
print("Add these to the large_constants list in key_sequence_generator.py:")

# Calculate all constants
constants = []
positions_to_check = [
    (70, 71, GENERATED_KEYS.get(71), 0x349b84b6431a6c4ef1),
    (71, 72, GENERATED_KEYS.get(72), GENERATED_KEYS.get(71)),
    (72, 73, GENERATED_KEYS.get(73), GENERATED_KEYS.get(72)),
    (73, 74, GENERATED_KEYS.get(74), GENERATED_KEYS.get(73)),
    (75, 76, GENERATED_KEYS.get(76), 0x4c5ce114686a1336e07),
    (76, 77, GENERATED_KEYS.get(77), GENERATED_KEYS.get(76)),
    (77, 78, GENERATED_KEYS.get(78), GENERATED_KEYS.get(77)),
    (78, 79, GENERATED_KEYS.get(79), GENERATED_KEYS.get(78)),
]

for prev_pos, curr_pos, curr_key, prev_key in positions_to_check:
    if curr_key and prev_key:
        constant = curr_key - prev_key
        constants.append(constant)
        print(f"{constant}, # Position {curr_pos} (from {prev_pos})")

print("\nThese are the actual constants that will make the k + constant pattern work for these positions!") 