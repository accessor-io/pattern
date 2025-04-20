import hashlib
import base58
import ecdsa
import struct

# Constants
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
CURVE = ecdsa.ellipticcurve.CurveFp(P, 0, 7) # secp256k1 has a=0, b=7, but ecdsa lib uses a=3, b=7 for some reason? Let's use the standard params
# Correcting the curve parameters: a=0, b=7 for secp256k1
CURVE_correct = ecdsa.ellipticcurve.CurveFp(P, 0, 7)
GENERATOR = ecdsa.ellipticcurve.Point(CURVE_correct, Gx, Gy)

BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

EXPECTED_ADDRESSES = [
    "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH", # 1
    "1CUNEBjYrCn2y1SdiUMohaKUi4wpP326Lb", # 2
    "19dT9XKRkMAjCZyWpVu48pj1AknS1Yf3sC", # 3
    # ... add all 160 addresses here if needed
    "1PEr4gG45YhKPPu4E1DZ5Y1TNK1T7D7t4s", # 68
    # ...
    "1NfgFXmVkekdsXpjoHAfWzQMSw8JpME4LV" # 160
]

# The full 159-character Base58 string - assumed to encode transformations
FULL_STRING = "BC9EEPMMCLPDPEQBHGN4CLr5J28HLFPWBi4HE2CNE3NPFD2N5a7cAKMJHNgBPM9PK6zNCFJBDK5qG8H2JNG4zKrUD6RAbFQM58gCKEHGP28CNMAEyQ7K6C8s2G"

# Known Solutions (Example - Replace with actual if available)
KNOWN_SOLUTIONS = {
    1: 0x1, # Private key for the first address (0x1)
    2: 0x3,
    3: 0x7,
    4: 0x8,
    5: 0x15,
    6: 0x31,
    7: 0x4c,
    8: 0xe0,
    9: 0x1d3,
    10: 0x202,
    11: 0x483,
    12: 0xa7b,
    13: 0x1460,
    14: 0x2930,
    15: 0x68f3,
    16: 0xc936,
    17: 0x1764f,
    18: 0x3080d,
    19: 0x5749f,
    20: 0xd2c55,
    21: 0x1ba534,
    22: 0x2de40f,
    23: 0x556e52,
    24: 0xdc2a04,
    25: 0x1fa5ee5,
    26: 0x340326e,
    27: 0x6ac3875,
    28: 0xd916ce8,
    29: 0x17e2551e,
    30: 0x3d94cd64,
    31: 0x7d4fe747,
    32: 0xb862a62e,
    33: 0xa96ca8d8,
    34: 0x4a65911d,
    35: 0xaed21170,
    36: 0x9de820a7c,
    37: 0x1757756a93,
    38: 0x22382facd0,
    39: 0x4b5f8303e9,
    40: 0xe9ae4933d6,
    41: 0x153869acc5b,
    42: 0x2a221c58d8f,
    43: 0x6bd3b27c591,
    44: 0xe02b35a358f,
    45: 0x122fca143c05,
    46: 0x2ec18388d544,
    47: 0x6cd610b53cba,
    48: 0xade6d7ce3b9b,
    49: 0x174176b015f4d,
    50: 0x22bd43c2e9354,
    51: 0x75070a1a009d4,
    52: 0xefae164cb9e3c,
    53: 0x180788e47e326c,
    54: 0x236fb6d5ad1f43,
    55: 0x6abe1f9b67e114,
    56: 0x9d18b63ac4ffdf,
    57: 0x1eb25c90795d61c,
    58: 0x2c675b852189a21,
    59: 0x7496cbb87cab44f,
    60: 0xfc07a1825367bbe,
    61: 0x13c96a3742f64906,
    62: 0x363d541eb611abee,
    63: 0x7cce5efdaccf6808,
    64: 0xf7051f27b09112d4,
    65: 0xa838b13505b26867,
    66: 0x2832ed74f2b5e3ee
    # 68: 0x... found previously in term68_solution.txt needs adding
    # ...
    # 160: 0x...
}

# --- Elliptic Curve Math ---

def inv(n, q):
    # Modular inverse using Fermat's Little Theorem: n^(q-2) mod q
    return pow(n, q - 2, q)

def add(p1, p2):
    if p1 is None: return p2
    if p2 is None: return p1
    if p1.x() == p2.x() and p1.y() != p2.y(): return None # Point at infinity
    if p1 == p2: return double(p1)

    lam = ((p2.y() - p1.y()) * inv(p2.x() - p1.x(), P)) % P
    x3 = (lam * lam - p1.x() - p2.x()) % P
    y3 = (lam * (p1.x() - x3) - p1.y()) % P
    return ecdsa.ellipticcurve.Point(CURVE_correct, x3, y3)

def double(p):
    if p is None: return None
    lam = ((3 * p.x() * p.x() + CURVE_correct.a()) * inv(2 * p.y(), P)) % P
    x3 = (lam * lam - 2 * p.x()) % P
    y3 = (lam * (p.x() - x3) - p.y()) % P
    return ecdsa.ellipticcurve.Point(CURVE_correct, x3, y3)

def multiply(p, n):
    r = None
    m2 = p
    while n > 0:
        if n & 1:
            r = add(r, m2)
        m2 = double(m2)
        n >>= 1
    return r

def privkey_to_pubkey(privkey_int):
    """Derives the public key point from a private key integer."""
    pubkey_point = multiply(GENERATOR, privkey_int)
    return pubkey_point

def pubkey_point_to_bytes(point, compressed=False):
    """Converts a public key point to bytes (uncompressed or compressed)."""
    x = point.x()
    y = point.y()
    if compressed:
        prefix = b'' if y % 2 == 0 else b''
        return prefix + x.to_bytes(32, byteorder='big')
    else:
        return b'' + x.to_bytes(32, byteorder='big') + y.to_bytes(32, byteorder='big')

# --- Hashing ---

def sha256(data):
    return hashlib.sha256(data).digest()

def ripemd160_hashlib(data):
    """Standard RIPEMD160 using hashlib (if available)."""
    try:
        # Some systems might not have ripemd160 compiled in OpenSSL
        h = hashlib.new('ripemd160')
        h.update(data)
        return h.digest()
    except ValueError:
        print("WARN: hashlib.new('ripemd160') failed. Using custom implementation.")
        return custom_ripemd160(data) # Fallback

def hash160_custom_ripemd(pubkey_bytes):
    """Performs SHA256 and then custom RIPEMD160."""
    return custom_ripemd160(sha256(pubkey_bytes))

def hash160_hashlib_ripemd(pubkey_bytes):
    """Performs SHA256 and then hashlib RIPEMD160."""
    return ripemd160_hashlib(sha256(pubkey_bytes))

# --- Custom RIPEMD160 Implementation (from search results) ---
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
            # Corrected processing logic (based on standard implementation structure)
            word_index = j
            if j >= 16: word_index = (1 * j + 5) % 16 # Example permutation, adjust if needed based on specific RIPEMD-160 details
            if j >= 32: word_index = (3 * j + 3) % 16
            if j >= 48: word_index = (7 * j + 7) % 16
            if j >= 64: word_index = (11 * j + 1) % 16

            # Parallel rounds calculation
            round_num = j // 16
            round_num_p = (79 - j) // 16

            word_idx = (j % 16) # Original uses direct index, let's stick to simpler version first if needed
            word_idx_p = (j % 16) # Same for parallel round

            # Round 1 (Left line)
            T = rol(a + f(j, b, c, d) + w[word_idx] + k[round_num], s[j]) + e
            a, b, c, d, e = e, T, b, rol(c, 10), d

            # Round 1' (Right line) - using f' (mirrored logic), k', s'
            # Need the correct f' mapping for parallel rounds. Example:
            def fp(j, x, y, z):
                jp = 79 - j
                if jp < 16: return x ^ y ^ z  # F4' = F0
                elif jp < 32: return (x & z) | (y & ~z) # F3' = F3
                elif jp < 48: return (x | ~y) ^ z # F2' = F2
                elif jp < 64: return (x & y) | (~x & z) # F1' = F1
                else: return x ^ (y | ~z) # F0' = F4

            # Adjusting word selection for parallel rounds (using pi permutation or similar?)
            # The provided code used `(j % 16) ^ (79 - j) // 16]` - let's try that structure
            word_idx_p = (j % 16) ^ ((79-j) // 16) # Seems unusual, maybe from a specific variant? Let's test this.

            # Use `fp` function for parallel rounds
            Tp = rol(ap + fp(j, bp, cp, dp) + w[word_idx_p] + kp[round_num_p], s[79 - j]) + ep
            ap, bp, cp, dp, ep = ep, Tp, bp, rol(cp, 10), dp

        # Combine results (Original logic)
        h = [(h[i] + x + y) & 0xffffffff for i, (x, y) in enumerate(zip((a, b, c, d, e), (ap, bp, cp, dp, ep)))]
        # Fix: The combination step in RIPEMD-160 is different
        # h[0] = (h[1] + c + dp) & 0xffffffff
        # h[1] = (h[2] + d + ep) & 0xffffffff
        # h[2] = (h[3] + e + ap) & 0xffffffff
        # h[3] = (h[4] + a + bp) & 0xffffffff
        # h[4] = (h[0] + b + cp) & 0xffffffff
        # Let's retry with the standard final combination:
        dh = [h[1], h[2], h[3], h[4], h[0]] # Temp store old h
        h[0] = (dh[0] + c + dp) & 0xffffffff
        h[1] = (dh[1] + d + ep) & 0xffffffff
        h[2] = (dh[2] + e + ap) & 0xffffffff
        h[3] = (dh[3] + a + bp) & 0xffffffff
        h[4] = (dh[4] + b + cp) & 0xffffffff


    return bytes().join(x.to_bytes(4, "little") for x in h)


# --- Base58 Encoding/Decoding ---

def base58_encode(b):
    """Encode bytes to a base58 string."""
    n = int.from_bytes(b, 'big')
    if n == 0:
        return BASE58_ALPHABET[0] * len(b) # Encode leading zeros
    res = []
    while n > 0:
        n, rem = divmod(n, 58)
        res.append(BASE58_ALPHABET[rem])
    res = "".join(reversed(res))
    # Add '1' for each leading zero byte
    czero = 0
    while czero < len(b) and b[czero] == 0:
        res = BASE58_ALPHABET[0] + res
        czero += 1
    return res

def base58_decode_int(s):
    """Decode a base58 string to an integer."""
    n = 0
    for char in s:
        n = n * 58 + BASE58_ALPHABET.index(char)
    return n

def base58_decode_full(s):
    """Decode a base58 string to bytes, preserving leading zeros."""
    n = base58_decode_int(s)
    num_bytes = (n.bit_length() + 7) // 8
    res = n.to_bytes(num_bytes, 'big')
    # Add leading zeros
    pad = 0
    for char in s:
        if char == BASE58_ALPHABET[0]:
            pad += 1
        else:
            break
    # Correct length if leading zeros were added to non-zero value
    expected_len = pad + len(res)
    if len(res) < expected_len:
         res = b'\x00' * pad + res # Should handle most cases

    # A more robust way to handle leading zeros during decode
    n = 0
    for char in s:
        n = n * 58 + BASE58_ALPHABET.index(char)

    # Estimate the number of bytes required
    # log2(58) is approx 5.858, so len(s) * 5.858 / 8 gives rough byte count
    # Or just use a large enough buffer and trim later if needed?
    # Let's try converting directly and handling padding
    num_bytes_est = (len(s) * 733) // 1000 + 1 # Approximation log2(58) ~ 733/1000
    res_bytes = n.to_bytes(num_bytes_est, 'big')

    # Trim leading zeros introduced by the fixed-size conversion
    while len(res_bytes) > 1 and res_bytes[0] == 0:
        res_bytes = res_bytes[1:]

    # Add back the actual leading zeros based on '1' characters
    leading_zeros = 0
    for char in s:
        if char == '1':
            leading_zeros += 1
        else:
            break
    full_bytes = b'\x00' * leading_zeros + res_bytes

    return full_bytes


def base58_check_encode(version, payload):
    """Encode a version byte and payload into a Base58Check string."""
    versioned = version + payload
    checksum = sha256(sha256(versioned))[:4]
    return base58_encode(versioned + checksum)

def base58_check_decode(s):
    """Decode and verify a Base58Check string."""
    decoded = base58_decode_full(s)
    if len(decoded) < 5:
        raise ValueError("Invalid Base58Check string: too short")
    version = decoded[0:1]
    payload = decoded[1:-4]
    checksum = decoded[-4:]
    expected_checksum = sha256(sha256(version + payload))[:4]
    if checksum != expected_checksum:
        raise ValueError(f"Invalid Base58Check checksum: got {checksum.hex()}, expected {expected_checksum.hex()}")
    return version, payload


# --- Address Derivation ---

def pubkey_to_address(pubkey_bytes, version_byte=b'\x00'):
    """Converts public key bytes to a Bitcoin address using custom RIPEMD160."""
    hashed_pubkey = hash160_custom_ripemd(pubkey_bytes) # Use custom hash
    return base58_check_encode(version_byte, hashed_pubkey)

# --- Analysis Functions ---

def analyze_first_address_derivation():
    """Analyze the derivation of the first address 1BgG... using private key 0x1."""
    print("\n--- Analyzing Derivation of First Address ---")
    target_address = EXPECTED_ADDRESSES[0]
    private_key_int = KNOWN_SOLUTIONS.get(1)

    if private_key_int is None:
        print("Private key for address 1 (0x1) is not defined in KNOWN_SOLUTIONS.")
        return

    print(f"Target Address: {target_address}")
    print(f"Assumed Private Key (int): {private_key_int}")

    # 1. Decode the target address
    try:
        decoded_full = base58_decode_full(target_address)
        print(f"Decoded Full (Hex): {decoded_full.hex()}")
        if len(decoded_full) != 25:
             print(f"WARN: Decoded length is {len(decoded_full)}, expected 25 bytes (1 version + 20 hash + 4 checksum).")
             # Attempt to parse anyway
             target_version = decoded_full[0:1]
             target_hash160 = decoded_full[1:-4] if len(decoded_full) > 5 else b''
             target_checksum = decoded_full[-4:] if len(decoded_full) >= 4 else b''
        else:
            target_version = decoded_full[0:1]
            target_hash160 = decoded_full[1:21]
            target_checksum = decoded_full[21:25]

        print(f"  - Version Byte: {target_version.hex()}")
        print(f"  - Hash160 Payload: {target_hash160.hex()}")
        print(f"  - Checksum: {target_checksum.hex()}")

        # 2. Verify checksum
        expected_checksum = sha256(sha256(target_version + target_hash160))[:4]
        print(f"  - Calculated Checksum: {expected_checksum.hex()}")
        if target_checksum == expected_checksum:
            print("  - Checksum VERIFIED")
        else:
            print("  - Checksum MISMATCH")

    except Exception as e:
        print(f"Error decoding target address: {e}")
        return # Cannot proceed without decoding

    # 3. Derive Public Key(s) from Private Key 0x1
    pubkey_point = privkey_to_pubkey(private_key_int)
    pubkey_uncompressed_bytes = pubkey_point_to_bytes(pubkey_point, compressed=False)
    pubkey_compressed_bytes = pubkey_point_to_bytes(pubkey_point, compressed=True)

    print(f"Derived Uncompressed PubKey: {pubkey_uncompressed_bytes.hex()}")
    print(f"Derived Compressed PubKey:   {pubkey_compressed_bytes.hex()}")

    # 4. Calculate Hash160 for both public keys using CUSTOM RIPEMD160
    hash160_unc_custom = hash160_custom_ripemd(pubkey_uncompressed_bytes)
    hash160_com_custom = hash160_custom_ripemd(pubkey_compressed_bytes)
    print(f"Hash160 (Uncompressed, Custom RIPEMD): {hash160_unc_custom.hex()}")
    print(f"Hash160 (Compressed,   Custom RIPEMD): {hash160_com_custom.hex()}")

    # 5. Calculate Hash160 for both public keys using STANDARD hashlib RIPEMD160
    hash160_unc_std = hash160_hashlib_ripemd(pubkey_uncompressed_bytes)
    hash160_com_std = hash160_hashlib_ripemd(pubkey_compressed_bytes)
    print(f"Hash160 (Uncompressed, Stdlib RIPEMD): {hash160_unc_std.hex()}")
    print(f"Hash160 (Compressed,   Stdlib RIPEMD): {hash160_com_std.hex()}")

    # 6. Compare with target hash
    print(f"Target Hash160 Payload:               {target_hash160.hex()}")
    if target_hash160 == hash160_unc_custom:
        print("  MATCH with Uncompressed + Custom RIPEMD")
    elif target_hash160 == hash160_com_custom:
        print("  MATCH with Compressed + Custom RIPEMD")
    elif target_hash160 == hash160_unc_std:
        print("  MATCH with Uncompressed + Stdlib RIPEMD")
    elif target_hash160 == hash160_com_std:
        print("  MATCH with Compressed + Stdlib RIPEMD")
    else:
        print("  NO MATCH with derived hashes.")

    # 7. Try generating addresses with derived hashes + target version byte
    addr_unc_custom = base58_check_encode(target_version, hash160_unc_custom)
    addr_com_custom = base58_check_encode(target_version, hash160_com_custom)
    addr_unc_std = base58_check_encode(target_version, hash160_unc_std)
    addr_com_std = base58_check_encode(target_version, hash160_com_std)

    print(f"Generated Addr (Unc, Custom): {addr_unc_custom}")
    print(f"Generated Addr (Com, Custom): {addr_com_custom}")
    print(f"Generated Addr (Unc, Stdlib): {addr_unc_std}")
    print(f"Generated Addr (Com, Stdlib): {addr_com_std}")
    print(f"Target Address:               {target_address}")


def generate_keys_and_addresses(start_key_hex, count):
    """Generates a sequence of keys and addresses based on a simple rule (example)."""
    # This is a placeholder. The actual generation logic is complex and TBD.
    # For now, just demonstrate deriving from the first known key.
    print("\n--- Generating Keys/Addresses (Placeholder) ---")
    if 1 in KNOWN_SOLUTIONS:
        key_int = KNOWN_SOLUTIONS[1]
        print(f"Using known private key for #1: {hex(key_int)}")
        try:
            pub_point = privkey_to_pubkey(key_int)
            pub_bytes_unc = pubkey_point_to_bytes(pub_point, compressed=False)
            pub_bytes_comp = pubkey_point_to_bytes(pub_point, compressed=True)

            addr_unc = pubkey_to_address(pub_bytes_unc)
            addr_comp = pubkey_to_address(pub_bytes_comp, version_byte=b'\x00') # Assume same version

            print(f"  Address (Uncompressed Key): {addr_unc}")
            print(f"  Address (Compressed Key):   {addr_comp}")

            if addr_unc == EXPECTED_ADDRESSES[0]:
                print("  Matches expected address #1 (using uncompressed key)")
            elif addr_comp == EXPECTED_ADDRESSES[0]:
                 print("  Matches expected address #1 (using compressed key)")
            else:
                 print("  Does NOT match expected address #1")

        except Exception as e:
            print(f"  Error deriving address for key {hex(key_int)}: {e}")
    else:
        print("No known key for #1 to start generation.")


def analyze_known_transitions():
    """Analyzes transitions between known keys and correlates with FULL_STRING."""
    print("\n--- Analyzing Known Key Transitions ---")
    sorted_indices = sorted(KNOWN_SOLUTIONS.keys())

    if len(FULL_STRING) < len(sorted_indices) - 1:
        print(f"WARN: FULL_STRING length ({len(FULL_STRING)}) is less than required for transitions ({len(sorted_indices) - 1}).")

    for i in range(len(sorted_indices) - 1):
        idx_n = sorted_indices[i]
        idx_n_plus_1 = sorted_indices[i+1]

        # Ensure we are looking at consecutive keys (index n and n+1)
        if idx_n_plus_1 != idx_n + 1:
            print(f"Skipping non-consecutive transition from index {idx_n} to {idx_n_plus_1}")
            continue

        key_n = KNOWN_SOLUTIONS[idx_n]
        key_n_plus_1 = KNOWN_SOLUTIONS[idx_n_plus_1]

        diff = key_n_plus_1 - key_n
        ratio = "N/A" if key_n == 0 else key_n_plus_1 / key_n

        # Get corresponding char from FULL_STRING (0-indexed)
        str_idx = idx_n - 1 # Transition from n to n+1 uses char at n-1
        transition_char = "N/A"
        if 0 <= str_idx < len(FULL_STRING):
            transition_char = FULL_STRING[str_idx]
        else:
            print(f"WARN: Index {str_idx} out of bounds for FULL_STRING (len {len(FULL_STRING)}) for transition {idx_n}->{idx_n_plus_1}")


        print(f"Transition {idx_n: >2} -> {idx_n_plus_1: >2} (Char: {transition_char}):")
        print(f"  Key[{idx_n: >2}] = {hex(key_n)}")
        print(f"  Key[{idx_n_plus_1: >2}] = {hex(key_n_plus_1)}")
        print(f"  Difference: {hex(diff)} ({diff})")
        print(f"  Ratio: {ratio:.4f}" if isinstance(ratio, (float, int)) else f"  Ratio: {ratio}")
        # Add more analysis here (bitwise ops, simple rule checks) if needed
        print("---")


# --- Main Execution ---
if __name__ == "__main__":
    # Analyze the derivation of the first known address
    # analyze_first_address_derivation()

    # Analyze the transitions between known keys
    analyze_known_transitions()

    # Placeholder for generating the sequence (replace with actual logic later)
    # generate_keys_and_addresses("...", 160)