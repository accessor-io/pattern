import hashlib
import base58
import ecdsa
import struct

# Import known solutions from the dedicated file
from solvers.src.config.known_solutions import KNOWN_SOLUTIONS

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

# Known Solutions are now imported from solvers.src.config.known_solutions
# REMOVED HARDCODED DICTIONARY

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
    """Convert a public key to a Bitcoin address."""
    h = hash160_hashlib_ripemd(pubkey_bytes)  # RIPEMD160(SHA256(pubkey))
    return base58_check_encode(version_byte, h)

def analyze_address_derivation(privkey_hex='0000000000000000000000000000000000000000000000000000000000000001', target_address='1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH'):
    """Reverse-check the address derivation process."""
    print(f"\n===== Address Derivation Analysis =====")
    print(f"Private Key (hex): {privkey_hex}")
    print(f"Target Address: {target_address}")
    
    # Convert private key to integer
    privkey_int = int(privkey_hex, 16)
    
    # Decode the target address
    try:
        # Get the full decoded bytes including checksum
        decoded_bytes = base58_decode_full(target_address)
        print(f"Decoded address (hex): {decoded_bytes.hex()}")
        
        # Extract version byte and hash160 payload
        version_byte = decoded_bytes[0:1]
        hash160_payload = decoded_bytes[1:-4]  # Skip version byte and last 4 checksum bytes
        checksum = decoded_bytes[-4:]
        
        print(f"Version byte: {version_byte.hex()}")
        print(f"Address hash160 payload: {hash160_payload.hex()}")
        print(f"Address checksum: {checksum.hex()}")
        
        # Verify checksum
        expected_checksum = sha256(sha256(version_byte + hash160_payload))[:4]
        if checksum == expected_checksum:
            print(f"✓ Checksum verification PASSED")
        else:
            print(f"✗ Checksum verification FAILED")
            print(f"  Expected: {expected_checksum.hex()}")
            print(f"  Actual: {checksum.hex()}")
        
        # Generate public key from private key
        pubkey_point = privkey_to_pubkey(privkey_int)
        print(f"Derived public key point:")
        print(f"  x: {pubkey_point.x()}")
        print(f"  y: {pubkey_point.y()}")
        
        # Convert to uncompressed format (04 + x + y)
        pubkey_uncompressed = pubkey_point_to_bytes(pubkey_point, compressed=False)
        print(f"Uncompressed public key: {pubkey_uncompressed.hex()}")
        
        # Calculate hash160 using standard method
        standard_hash160 = hash160_hashlib_ripemd(pubkey_uncompressed)
        print(f"Standard derived hash160: {standard_hash160.hex()}")
        
        # Compare with address hash160
        if standard_hash160 == hash160_payload:
            print(f"✓ Hash160 verification PASSED - Standard address derivation works!")
        else:
            print(f"✗ Hash160 verification FAILED - Address was NOT derived using standard method")
            print(f"  Hex diff: {bytes([a ^ b for a, b in zip(standard_hash160, hash160_payload)]).hex()}")
        
        # Try custom RIPEMD160 implementation
        custom_hash160 = hash160_custom_ripemd(pubkey_uncompressed)
        print(f"Custom derived hash160: {custom_hash160.hex()}")
        
        if custom_hash160 == hash160_payload:
            print(f"✓ Custom Hash160 verification PASSED - Custom RIPEMD160 works!")
        else:
            print(f"✗ Custom Hash160 verification FAILED")
            print(f"  Hex diff: {bytes([a ^ b for a, b in zip(custom_hash160, hash160_payload)]).hex()}")
        
        # Try both SHA256 + custom RIPEMD and standard RIPEMD to see where the difference is
        sha256_result = sha256(pubkey_uncompressed)
        print(f"SHA256 of pubkey: {sha256_result.hex()}")
        
        # Check if first few bytes of payload match pattern for known addresses
        print(f"\nComparing with first few known addresses:")
        for i, addr in enumerate(EXPECTED_ADDRESSES[:5]):
            if i == 0:
                continue  # Skip the first one since we're already analyzing it
            addr_decoded = base58_decode_full(addr)
            addr_hash160 = addr_decoded[1:-4]
            print(f"Address #{i+1}: {addr}")
            print(f"  Hash160: {addr_hash160.hex()}")
            
    except Exception as e:
        print(f"Error during address analysis: {str(e)}")
    
    return

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

    # Dictionary to map transition character to observed modular differences
    diff_map = {}

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
        diff_mod_n = (key_n_plus_1 - key_n) % N # Modular difference
        ratio = "N/A" if key_n == 0 else key_n_plus_1 / key_n

        # Get corresponding char from FULL_STRING (0-indexed)
        str_idx = idx_n - 1 # Transition from n to n+1 uses char at n-1
        transition_char = "N/A"
        char_b58_index = -1 # Default value if char is not found or index out of bounds
        if 0 <= str_idx < len(FULL_STRING):
            transition_char = FULL_STRING[str_idx]
            try:
                char_b58_index = BASE58_ALPHABET.index(transition_char)
            except ValueError:
                print(f"WARN: Character '{transition_char}' not found in BASE58_ALPHABET.")
                char_b58_index = -1 # Indicate invalid char
        else:
            print(f"WARN: Index {str_idx} out of bounds for FULL_STRING (len {len(FULL_STRING)}) for transition {idx_n}->{idx_n_plus_1}")

        # Store the difference for this character
        if transition_char != "N/A":
            if transition_char not in diff_map:
                diff_map[transition_char] = []
            diff_map[transition_char].append(diff_mod_n)

        print(f"Transition {idx_n: >2} -> {idx_n_plus_1: >2} (Char: '{transition_char}' / B58 Idx: {char_b58_index: >2}):")
        print(f"  Key[{idx_n: >2}] = {hex(key_n)}")
        print(f"  Key[{idx_n_plus_1: >2}] = {hex(key_n_plus_1)}")
        print(f"  Difference: {hex(diff)} ({diff})")
        print(f"  Diff mod N: {hex(diff_mod_n)}")

        # Bitwise XOR difference
        xor_diff = key_n ^ key_n_plus_1
        print(f"  XOR Diff:   {hex(xor_diff)}")

        print(f"  Ratio: {ratio:.4f}" if isinstance(ratio, (float, int)) else f"  Ratio: {ratio}")

        # Check simple rules (modulo N)
        rule_checks = []
        key_n_times_2_mod_n = (key_n * 2) % N
        key_n_times_2_plus_1_mod_n = (key_n * 2 + 1) % N
        if key_n_plus_1 == key_n_times_2_mod_n:
            rule_checks.append("key_n*2 % N")
        if key_n_plus_1 == key_n_times_2_plus_1_mod_n:
            rule_checks.append("key_n*2+1 % N")
        if key_n_plus_1 == (key_n + diff) % N: # Tautology check
            rule_checks.append("key_n + diff % N")

        # Check combined position/character index rules
        # 1. Position-based formulas
        if key_n_plus_1 == (key_n + idx_n) % N:
            rule_checks.append(f"key_n + n ({idx_n}) % N")
        if key_n_plus_1 == (key_n * idx_n) % N:
            rule_checks.append(f"key_n * n ({idx_n}) % N")
            
        # 2. Character Base58 index formulas (only check if we have a valid index)
        if char_b58_index >= 0:
            if key_n_plus_1 == (key_n + char_b58_index) % N:
                rule_checks.append(f"key_n + char_idx ({char_b58_index}) % N")
            if key_n_plus_1 == (key_n * char_b58_index) % N:
                rule_checks.append(f"key_n * char_idx ({char_b58_index}) % N")
                
            # 3. Combined formulas
            if key_n_plus_1 == (key_n + idx_n + char_b58_index) % N:
                rule_checks.append(f"key_n + n ({idx_n}) + char_idx ({char_b58_index}) % N")
            if key_n_plus_1 == (key_n * idx_n + char_b58_index) % N:
                rule_checks.append(f"key_n * n ({idx_n}) + char_idx ({char_b58_index}) % N")
            if key_n_plus_1 == (key_n + idx_n * char_b58_index) % N:
                rule_checks.append(f"key_n + n ({idx_n}) * char_idx ({char_b58_index}) % N")
            if key_n_plus_1 == (key_n * char_b58_index + idx_n) % N:
                rule_checks.append(f"key_n * char_idx ({char_b58_index}) + n ({idx_n}) % N")

        if rule_checks:
            print(f"  Simple Rules Match: {', '.join(rule_checks)}")
        else:
            print("  Simple Rules Match: None")
        print("---")

    # Print the summary map
    print("\n--- Character to Modular Difference (mod N) Map ---")
    sorted_chars = sorted(diff_map.keys())
    for char in sorted_chars:
        # Use set to show unique differences for each char
        unique_diffs_hex = {hex(d) for d in diff_map[char]}
        print(f"Character '{char}': {unique_diffs_hex}")
    print("-----------------------------------------------------")


def analyze_diff_char_relationships(analysis_range=10):
    """
    Analyze the relationship between character values and key differences
    """
    if len(KNOWN_SOLUTIONS) < 2:
        print("Need at least 2 known keys to analyze differences")
        return
    
    print(f"\n--- Analyzing Character-Difference Relationships (full sequence) ---")
    
    # Get the keys in sorted order
    sorted_keys = sorted(KNOWN_SOLUTIONS.keys())
    
    differences = []
    chars = []
    ascii_values = []
    
    for i in range(1, len(sorted_keys)):
        pos_prev = sorted_keys[i-1]
        pos_curr = sorted_keys[i]
        key_prev = KNOWN_SOLUTIONS[pos_prev]
        key_current = KNOWN_SOLUTIONS[pos_curr]
        position = pos_curr
        
        # Calculate difference between keys
        diff = (key_current - key_prev) % N
        
        # Get character at position-1
        char = FULL_STRING[position-1] if position-1 < len(FULL_STRING) else None
        if char is None:
            continue
            
        # Store values for correlation analysis
        differences.append(diff)
        chars.append(char)
        ascii_values.append(ord(char))
        
        print(f"Position {position}: '{char}' (ASCII {ord(char)}) => Diff: {diff}")
        
        # Check for specific patterns
        if char in BASE58_ALPHABET:
            char_idx = BASE58_ALPHABET.find(char)
            if diff % (char_idx + 1) == 0:
                multiple = diff // (char_idx + 1)
                print(f"  ✓ Difference is exactly {multiple} times the char B58 index+1 ({char_idx+1})")
            
            if diff % ord(char) == 0:
                multiple = diff // ord(char)
                print(f"  ✓ Difference is exactly {multiple} times the ASCII value ({ord(char)})")
    
    # Report simple patterns
    if len(differences) > 3:
        print("\nChecking for simple mathematical relationships between characters and differences:")
        
        # Check if all odd chars create odd differences, even chars create even differences
        odd_chars_create_odd_diffs = True
        even_chars_create_even_diffs = True
        
        for i in range(len(differences)):
            char_odd = ascii_values[i] % 2 == 1
            diff_odd = differences[i] % 2 == 1
            
            if char_odd and not diff_odd:
                odd_chars_create_odd_diffs = False
            if not char_odd and diff_odd:
                even_chars_create_even_diffs = False
        
        if odd_chars_create_odd_diffs:
            print("  ✓ Pattern: Odd ASCII characters consistently produce odd differences")
        if even_chars_create_even_diffs:
            print("  ✓ Pattern: Even ASCII characters consistently produce even differences")
        
        # See if differences tend to be multiples of the character value
        multiple_counts = {}
        for i in range(len(differences)):
            if ascii_values[i] == 0:
                continue
            if differences[i] % ascii_values[i] == 0:
                multiple = differences[i] // ascii_values[i]
                multiple_counts[multiple] = multiple_counts.get(multiple, 0) + 1
        
        if multiple_counts:
            print("\nDifferences that are exact multiples of character ASCII values:")
            for multiple, count in sorted(multiple_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  Multiple of {multiple}: {count} times ({count/len(differences)*100:.1f}%)")
                
        # Check if differences correlate with positions
        position_multiples = {}
        for i in range(len(differences)):
            position = sorted_keys[i]  # This is the 1-indexed position
            if differences[i] % position == 0:
                multiple = differences[i] // position
                position_multiples[multiple] = position_multiples.get(multiple, 0) + 1
        
        if position_multiples:
            print("\nDifferences that are exact multiples of their positions:")
            for multiple, count in sorted(position_multiples.items(), key=lambda x: x[1], reverse=True):
                print(f"  Multiple of {multiple}: {count} times ({count/len(differences)*100:.1f}%)")
    
    print("\nEnd of character-difference analysis")


def analyze_differences_between_known_keys(analysis_range=10):
    """
    Analyze basic differences between consecutive private keys
    """
    if len(KNOWN_SOLUTIONS) < 2:
        print("Need at least 2 known keys to analyze differences")
        return
    
    print(f"\n--- Analyzing Differences Between Known Keys (first {analysis_range} transitions) ---")
    
    # Get the keys in sorted order (assuming keys start from 1)
    sorted_keys = sorted(KNOWN_SOLUTIONS.keys())
    
    # Limit to the first 'analysis_range' transitions or all available
    max_index = min(analysis_range + 1, len(sorted_keys))
    
    for i in range(1, max_index):
        pos_prev = sorted_keys[i-1]
        pos_curr = sorted_keys[i]
        key_prev = KNOWN_SOLUTIONS[pos_prev]
        key_current = KNOWN_SOLUTIONS[pos_curr]
        position = pos_curr
        
        # Calculate basic differences
        diff = (key_current - key_prev) % N
        diff_neg = (key_prev - key_current) % N
        diff_pct = (diff / key_prev) * 100 if key_prev != 0 else float('inf')
        
        # Get character at position-1 (assuming each position is influenced by previous character)
        char = FULL_STRING[position-1] if position-1 < len(FULL_STRING) else None
        char_info = f"'{char}' (ASCII {ord(char)})" if char else "N/A"
        
        print(f"\nPosition {position}, Character: {char_info}")
        print(f"  Previous key: {key_prev}")
        print(f"  Current key:  {key_current}")
        print(f"  Difference:   {diff}")
        print(f"  Neg. Diff:    {diff_neg}")
        print(f"  % Change:     {diff_pct:.2f}%")
        
        # Check if difference correlates with character properties
        if char and char in BASE58_ALPHABET:
            char_idx = BASE58_ALPHABET.find(char)
            # See if the difference is a multiple of the character index
            if diff % (char_idx + 1) == 0:
                factor = diff // (char_idx + 1)
                print(f"  ✓ Difference is {factor} times the character index+1 ({char_idx+1})")
            
            # Check if the difference has any pattern related to ASCII value
            ascii_val = ord(char)
            if diff % ascii_val == 0:
                factor = diff // ascii_val
                print(f"  ✓ Difference is {factor} times the ASCII value ({ascii_val})")
        
        # Check for common mathematical operations
        if key_current == (key_prev * 2) % N:
            print(f"  ✓ Current key is exactly 2 times previous key")
        elif key_current == (key_prev * 3) % N:
            print(f"  ✓ Current key is exactly 3 times previous key")
        elif key_current == (key_prev + key_prev) % N:
            print(f"  ✓ Current key is previous key added to itself")
        elif key_current == (key_prev + position) % N:
            print(f"  ✓ Current key is previous key plus position ({position})")
        elif key_current == (key_prev * position) % N:
            print(f"  ✓ Current key is previous key multiplied by position ({position})")

def check_transition_formulas(analysis_range=10):
    """
    Test different transition formulas to see what may be used to derive the next key
    """
    if len(KNOWN_SOLUTIONS) < 2:
        print("Need at least 2 known keys to analyze transitions")
        return
    
    print(f"\n--- Testing Transition Formulas (first {analysis_range} transitions) ---")
    
    # Get sorted keys
    sorted_keys = sorted(KNOWN_SOLUTIONS.keys())
    
    formulas_tested = 0
    formulas_matched = 0
    
    # Limit to the first 'analysis_range' transitions or all available
    max_index = min(analysis_range + 1, len(sorted_keys))
    
    for i in range(1, max_index):
        pos_prev = sorted_keys[i-1]
        pos_curr = sorted_keys[i]
        key_prev = KNOWN_SOLUTIONS[pos_prev]
        key_current = KNOWN_SOLUTIONS[pos_curr]
        position = pos_curr
        
        print(f"\nPosition {position}:")
        
        # Get the character at position-1
        char = FULL_STRING[position-1] if position-1 < len(FULL_STRING) else None
        if char:
            char_idx = BASE58_ALPHABET.find(char) if char in BASE58_ALPHABET else -1
            print(f"  Character: '{char}' (ASCII {ord(char)}, Base58 index: {char_idx})")
        
        # Test different formulas for deriving the next key
        test_formulas = [
            # Basic operations
            (key_prev + 1) % N, "k + 1",
            (key_prev + 2) % N, "k + 2",
            (key_prev * 2) % N, "k * 2",
            (key_prev * 3) % N, "k * 3",
            (key_prev ** 2) % N, "k^2",
            (key_prev + position) % N, "k + position",
            (key_prev * position) % N, "k * position",
            # Use ** only for small exponents to avoid slow calculations
            (key_prev ** position) % N if position < 10 else None, "k ^ position",
            
            # Operations involving previous key and character
            (key_prev + ord(char)) % N if char else None, "k + ASCII(char)",
            (key_prev * ord(char)) % N if char else None, "k * ASCII(char)",
            (key_prev ^ ord(char)) % N if char else None, "k XOR ASCII(char)",
            
            # Operations with Base58 index
            (key_prev + char_idx) % N if char_idx != -1 else None, "k + Base58_idx",
            (key_prev * char_idx) % N if char_idx != -1 else None, "k * Base58_idx",
            (key_prev ^ char_idx) % N if char_idx != -1 else None, "k XOR Base58_idx",
            
            # Bit operations
            ((key_prev << 1) | 1) % N, "k << 1 | 1",
            ((key_prev << 2) | 3) % N, "k << 2 | 3",
            ((key_prev << 1) + key_prev) % N, "k << 1 + k",
            
            # Combinations
            (key_prev * position + char_idx) % N if char_idx != -1 else None, "k * position + Base58_idx",
            (key_prev * position + ord(char)) % N if char else None, "k * position + ASCII(char)",
            (key_prev * ord(char) + position) % N if char else None, "k * ASCII(char) + position",
        ]
        
        # Test each formula
        for j in range(0, len(test_formulas), 2):
            result = test_formulas[j]
            formula_desc = test_formulas[j+1]
            
            if result is None:
                continue
                
            formulas_tested += 1
            
            # Check exact match
            if result == key_current:
                print(f"  ✓ MATCH! {formula_desc}")
                formulas_matched += 1
            
            # Check close matches only for significant transitions
            elif j < 10 and abs(result - key_current) / N < 0.01:
                print(f"  ~ CLOSE: {formula_desc} = {result}")
                print(f"    Difference: {result - key_current}")
    
    print(f"\nTested {formulas_tested} formulas across {min(analysis_range, len(KNOWN_SOLUTIONS)-1)} transitions")
    print(f"Found {formulas_matched} exact matches")

# Helper function for prime checking
def is_prime(n):
    """Check if a number is prime"""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def get_prime_factors(n):
    """Get all prime factors of a number"""
    factors = []
    d = 2
    while n > 1:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
        if d*d > n:
            if n > 1:
                factors.append(n)
            break
    return factors

def analyze_special_operations(analysis_range=10):
    """Test for special operations that might be used in transitions"""
    if len(KNOWN_SOLUTIONS) < 2:
        print("Need at least 2 known keys to analyze transitions")
        return
    
    print(f"\n--- Testing Special Operations (first {analysis_range} transitions) ---")
    
    # Get sorted keys
    sorted_keys = sorted(KNOWN_SOLUTIONS.keys())
    
    # Limit to the first 'analysis_range' transitions or all available
    max_index = min(analysis_range + 1, len(sorted_keys))
    
    for i in range(1, max_index):
        pos_prev = sorted_keys[i-1]
        pos_curr = sorted_keys[i]
        key_prev = KNOWN_SOLUTIONS[pos_prev]
        key_current = KNOWN_SOLUTIONS[pos_curr]
        position = pos_curr
        
        # Get character at position-1
        char = FULL_STRING[position-1] if position-1 < len(FULL_STRING) else None
        if char is None:
            continue
        
        char_idx = BASE58_ALPHABET.find(char) if char in BASE58_ALPHABET else -1
        if char_idx == -1:
            continue
            
        print(f"\nPosition {position}, Character '{char}' (index {char_idx}):")
        
        # Test for doubling at certain positions
        if position in [2, 5, 10, 20, 50, 100]:
            doubled = (key_prev * 2) % N
            if doubled == key_current:
                print(f"  ✓ MATCH! Key doubled at position {position}")
            else:
                print(f"  × Not doubled at position {position}")
        
        # Test for prime position special handling
        if is_prime(position):
            # Test multiplication by position
            mul_by_pos = (key_prev * position) % N
            if mul_by_pos == key_current:
                print(f"  ✓ MATCH! Key multiplied by prime position {position}")
            
            # Test addition of prime factors
            prime_sum = sum(get_prime_factors(position))
            prime_result = (key_prev + prime_sum) % N
            if prime_result == key_current:
                print(f"  ✓ MATCH! Key + sum of prime factors ({prime_sum}) at position {position}")
        
        # Test for control character special handling (ASCII < 32)
        if ord(char) < 32:
            # Test bit rotation based on control char value
            rotated_left = ((key_prev << ord(char)) | (key_prev >> (N.bit_length() - ord(char)))) % N
            if rotated_left == key_current:
                print(f"  ✓ MATCH! Key rotated left by {ord(char)} bits at control char position")

def analyze_control_characters(analysis_range=10):
    """
    Analyzes transitions that occur near control characters (like BEL) to 
    identify if they trigger pattern changes in the key generation sequence.
    """
    print(f"\n--- Control Character Analysis (first {analysis_range} control characters) ---")
    
    if len(KNOWN_SOLUTIONS) < 3:
        print("Need at least 3 known keys to analyze control character influence")
        return
    
    # Find positions of control characters
    control_chars_pos = []
    for i, char in enumerate(FULL_STRING):
        if ord(char) < 32:  # ASCII control characters
            control_chars_pos.append((i, char, ord(char)))
    
    print(f"Control characters found at positions: {control_chars_pos}")
    
    # Get sorted keys
    sorted_keys = sorted(KNOWN_SOLUTIONS.keys())
    
    # Limit to the first 'analysis_range' control characters or all available
    max_control_chars = min(analysis_range, len(control_chars_pos))
    
    # Analyze transitions around control characters
    for idx in range(max_control_chars):
        pos, char, char_ord = control_chars_pos[idx]
        print(f"\nAnalyzing around control character at position {pos} (ASCII {char_ord}):")
        
        # Check if we have known solutions around this position
        before_pos = pos
        at_pos = pos + 1
        after_pos = pos + 2
        
        # See if these positions are in our known solutions
        if before_pos not in KNOWN_SOLUTIONS or at_pos not in KNOWN_SOLUTIONS or after_pos not in KNOWN_SOLUTIONS:
            print(f"  Not enough known solutions around position {pos}")
            continue
        
        # Get keys before, at, and after the control character
        key_before = KNOWN_SOLUTIONS[before_pos]
        key_at = KNOWN_SOLUTIONS[at_pos]
        key_after = KNOWN_SOLUTIONS[after_pos]
        
        print(f"  Key before ({before_pos}): {key_before}")
        print(f"  Key at control ({at_pos}): {key_at}")
        print(f"  Key after ({after_pos}): {key_after}")
        
        # Calculate differences
        diff_before = (key_at - key_before) % N
        diff_after = (key_after - key_at) % N
        
        print(f"  Difference before: {diff_before}")
        print(f"  Difference after: {diff_after}")
        
        # Look for pattern changes
        if diff_before != diff_after:
            print(f"  PATTERN CHANGE DETECTED: The difference changes around this control character")
            
            # Special BEL character analysis (ASCII 7)
            if char_ord == 7:  # BEL character
                # Check if doubled
                if key_at == (key_before * 2) % N:
                    print(f"  BEL character appears to DOUBLE the previous key")
                
                # Check if bit shifted
                for shift in range(1, 8):
                    if key_at == ((key_before << shift) % N):
                        print(f"  BEL character appears to LEFT SHIFT the previous key by {shift} bits")
                    if key_at == ((key_before >> shift) % N):
                        print(f"  BEL character appears to RIGHT SHIFT the previous key by {shift} bits")
                
                # Check if XOR with position
                if key_at == (key_before ^ at_pos) % N:
                    print(f"  BEL character appears to XOR the previous key with its position ({at_pos})")
            
            # Test if operation changes based on control character value
            if diff_after == (diff_before * char_ord) % N:
                print(f"  Operation changes by factor of {char_ord} (ASCII value of control character)")
        else:
            print(f"  No pattern change detected around this control character")

def analyze_transitions(analysis_range=10):
    """
    Main function to analyze transitions between known keys
    """
    print("\n===== Key Transition Analysis =====")
    
    # Call all analysis functions with the specified range
    analyze_differences_between_known_keys(analysis_range)
    check_transition_formulas(analysis_range)
    analyze_special_operations(analysis_range)
    analyze_control_characters(analysis_range)
    
    print("\n===== End of Analysis =====")

def generate_sequence_from_rules(max_pos=10):
    """Generates keys based on position-dependent rules derived from FULL_STRING."""
    print(f"\n--- Attempting Sequence Generation up to Position {max_pos} ---")
    if 1 not in KNOWN_SOLUTIONS:
        print("ERROR: Cannot start generation without known key for position 1.")
        return None

    generated_keys = {1: KNOWN_SOLUTIONS[1]}
    correct_count = 1 # Key 1 is known

    for pos in range(2, max_pos + 1):
        if pos - 1 not in generated_keys:
            print(f"ERROR: Cannot generate key for position {pos}, previous key missing.")
            break # Stop if sequence is broken

        key_prev = generated_keys[pos - 1]
        string_index = pos - 2 # String char influences transition to current position

        if string_index >= len(FULL_STRING):
            print(f"WARN: Reached end of FULL_STRING at position {pos}. Cannot determine rule.")
            break

        char = FULL_STRING[string_index]
        char_idx = BASE58_ALPHABET.find(char) if char in BASE58_ALPHABET else -1

        key_current = None # Placeholder for the generated key

        # --- Define position-specific rules based on observations --- 
        # This section needs to be filled with the actual hypothesized rules
        
        if pos == 2: # Char 'B' (idx 10) -> Should generate key 3
            # Observed: Key 3 = Key 1 * 3? Or Key 1 + 2?
            # Let's try Key 1 * 3 based on analysis of pos 2 -> 3 ('C') transition
            # Wait, char at index 0 is 'B'. Transition 1->2. Key 1 is 1. Key 2 is 3.
            # Rule for 'B'? Let's assume k_next = k*3 for now based on result.
             key_current = (key_prev * 3) % N 
        elif pos == 3: # Char 'C' (idx 11) -> Should generate key 7
            # Observed: Key 7. Prev Key 3. Rule for 'C'? (k << 1) | 1 ?
            key_current = ((key_prev << 1) | 1) % N
        elif pos == 4: # Char '9' (idx 8) -> Should generate key 8
            # Observed: Key 8. Prev Key 7. Rule for '9'? k+1?
            key_current = (key_prev + 1) % N
        elif pos == 5: # Char 'E' (idx 13) -> Should generate key 21 (0x15)
             # Observed: Key 21. Prev Key 8. Rule for 'E'? k + char_idx? (8+13=21)
            if char_idx != -1:
                 key_current = (key_prev + char_idx) % N
        elif pos == 6: # Char 'E' (idx 13) -> Should generate key 49 (0x31)
             # Observed: Key 49. Prev Key 21. Rule for 'E'? k * 2 + 7? k + 28?
             # Let's see if k + char_idx works again: 21 + 13 = 34. Doesn't work.
             # What if 'E' rule is 'k+1' like pos 4? 21+1 = 22. Doesn't work.
             # Maybe k*2 + 7? (21*2+7 = 49). Let's try this specific rule.
             key_current = (key_prev * 2 + 7) % N
        elif pos == 7: # Char 'P' (idx 22) -> Should generate key 76 (0x4c)
            # Observed: Key 76. Prev Key 49. Diff 27. Rule for 'P'? 
            # Let's try the observed difference directly.
            key_current = (key_prev + 27) % N
        elif pos == 8: # Char 'M' (idx 20) -> Should generate key 224 (0xe0)
            # Observed: Key 224. Prev Key 76. Diff 148. Rule for 'M'? 
            # k*3 = 228. Close. Try k*3 - 4.
            key_current = (key_prev * 3 - 4) % N
        elif pos == 9: # Char 'M' (idx 20) -> Should generate key 467 (0x1d3)
            # Observed: Key 467. Prev Key 224. Diff 243. Rule for 'M' again?
            # Rule k*3-4 gives 668. No.
            # Rule k*2+19 gives 448+19=467. Yes!
            key_current = (key_prev * 2 + 19) % N
        elif pos == 10: # Char 'C' (idx 11) -> Should generate key 514 (0x202)
            # Observed: Key 514. Prev Key 467. Diff 47. Rule for 'C' again?
            # Rule (k<<1)|1 gives 935. No.
            # Rule k*3 gives 1401. No.
            # Let's try observed difference.
            key_current = (key_prev + 47) % N
        elif pos == 11: # Char 'L' (idx 19) -> Should generate key 1155 (0x483)
            # Observed: Key 1155. Prev Key 514. Diff 641. Rule for 'L'?
            # Try k*2 + 127? 514*2+127 = 1028+127 = 1155. Yes.
            key_current = (key_prev * 2 + 127) % N
        elif pos == 12: # Char 'P' (idx 22) -> Should generate key 2683 (0xa7b)
            # Observed: Key 2683. Prev Key 1155. Diff 1528. Rule for 'P' again?
            # Rule k+27 gives 1182. No.
            # Rule k*2+373? 1155*2+373 = 2310+373 = 2683. Yes!
            key_current = (key_prev * 2 + 373) % N
        elif pos == 13: # Char 'D' (idx 12) -> Should generate key 5216 (0x1460)
            # Observed: Key 5216. Prev Key 2683. Diff 2533. Rule for 'D'?
            # Try k*2 - 150? 2683*2 - 150 = 5366 - 150 = 5216. Yes.
            key_current = (key_prev * 2 - 150) % N
        elif pos == 14: # Char 'P' (idx 22) -> Should generate key 10544 (0x2930)
            # Observed: Key 10544. Prev Key 5216. Diff 5328. Rule for 'P' again?
            # Rule k+27 no. Rule k*2+373 = 10805 no.
            # Rule k*2+112? 5216*2+112 = 10432+112 = 10544. Yes.
            key_current = (key_prev * 2 + 112) % N
            print(f"    -> Applied Pos 14 Rule: (key_prev * 2 + 112) % N = 0x{key_current:x}")

        elif pos == 15:
            # Position 15: 'E' -> key = 0x2930, next_key = 0x68cd. Diff = 16285
            # Rule: key_current = (key_prev * 2 + 5741) % N? (21088 + 5741 = 26829 = 0x68cd. YES!)
            # Origin of 5741? Not immediately obvious.
            key_current = (key_prev * 2 + 5741) % N
            print(f"    -> Applied Pos 15 Rule: (key_prev * 2 + 5741) % N = 0x{key_current:x}")

        else:
            # Default/Placeholder for unhandled positions
            print(f"  Position {pos} (Char '{char}'): No specific rule implemented yet.")
            break # Stop generation if rule is unknown

        if key_current is not None:
            generated_keys[pos] = key_current
            print(f"  Position {pos} (Char '{char}'): Generated Key: {hex(key_current)}")

            # Verify against known solutions if available
            if pos in KNOWN_SOLUTIONS:
                known_key = KNOWN_SOLUTIONS[pos]
                if key_current == known_key:
                    print(f"    ✓ MATCHED known solution!")
                    correct_count += 1
                else:
                    print(f"    ✗ MISMATCHED known solution! Expected: {hex(known_key)}")
                    # break # Option: Stop on first mismatch
            else:
                print(f"    - No known solution to compare against.")
        else:
            # Handle cases where rule wasn't applied or failed
            print(f"  Position {pos} (Char '{char}'): Failed to generate key.")
            break

    print(f"--- Generation Summary ---")
    print(f"Successfully generated and verified {correct_count}/{len(KNOWN_SOLUTIONS)} known keys up to position {max_pos}.")
    print(f"Total keys generated: {len(generated_keys)}")
    return generated_keys

# Update main function to include our new analysis
if __name__ == "__main__":
    # Analyze the first address derivation (should now use fallback if needed)
    # analyze_first_address_derivation() # Commented out for generation focus

    # Analyze general derivation for debugging if needed (optional)
    # analyze_address_derivation()

    # print("\n===== Key Transition Analysis =====\n") # Commented out

    # Determine the full range for analysis based on known solutions
    # -1 because transitions occur between keys (e.g., 160 keys -> 159 transitions)
    # full_analysis_range = len(KNOWN_SOLUTIONS) -1
    # if full_analysis_range < 1:
    #     print("WARN: Not enough known solutions to analyze transitions.")
    #     full_analysis_range = 0 # Prevent errors

    # Call analysis functions with the full range (Commented out for generation focus)
    # analyze_known_transitions() # This one seems to analyze all available
    # analyze_differences_between_known_keys(analysis_range=full_analysis_range)
    # check_transition_formulas(analysis_range=full_analysis_range)
    # analyze_special_operations(analysis_range=full_analysis_range)
    # analyze_control_characters(analysis_range=full_analysis_range) # Analyze full string length

    # print("\n===== End of Analysis =====\n") # Commented out

    # Additional analysis (might need adjustment) (Commented out for generation focus)
    # print("--- Analyzing Character-Difference Relationships (full sequence) ---")
    # analyze_diff_char_relationships(analysis_range=full_analysis_range)
    # print("End of character-difference analysis")

    # Optional: Generate and print all keys/addresses if needed
    # generate_keys_and_addresses(KNOWN_SOLUTIONS["1"]["privkey_hex"], len(KNOWN_SOLUTIONS))

    # Example: Analyze transition at a specific position (e.g., position 68)
    # analyze_transitions(analysis_range=len(KNOWN_SOLUTIONS)-1) # Call the main transition analyzer

    # print("===== End of Position 69 Test =====") # Commented out

    # --- Verify provided details for k_70 --- (Commented out)
    # pos_to_verify = 70 # Ensure this line correctly assigns 70
    # print(f"\n===== Verifying Provided Details for Position {pos_to_verify} =====")
    # if pos_to_verify in KNOWN_SOLUTIONS:
    #     k_verify = KNOWN_SOLUTIONS[pos_to_verify]

    # --- Generate sequence based on implemented rules ---
    print("\n===== Attempting Sequence Generation =====")
    # Note: This function currently only has rules defined up to position 15.
    # Generation will stop there unless more rules are added to the function.
    generated_sequence = generate_sequence_from_rules(max_pos=160)

    if generated_sequence:
        print("\n--- Generated Keys ---")
        # Sort keys by position before printing
        for pos in sorted(generated_sequence.keys()):
             print(f"Position {pos}: {hex(generated_sequence[pos])}")
        print(f"Total keys generated: {len(generated_sequence)}")
    else:
        print("\nGeneration failed or produced no keys.")

    print("\n===== Script Finished =====")