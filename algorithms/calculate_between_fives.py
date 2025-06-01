#!/usr/bin/env python3
"""
Calculate Bitcoin puzzle keys for positions between known 5/0 positions.
We know: 70, 75, 80, 85, 90, 95, 100, 110, 115, 120, 125, 130
We need: 71-74, 76-79, 81-84, 86-89, 91-94, 96-99, 101-109, 111-114, 116-119, 121-124, 126-129
"""

import hashlib
import ecdsa

# Bitcoin elliptic curve parameters
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

# Expected Bitcoin addresses for verification (positions 70-130)
EXPECTED_ADDRESSES = {
    70: "19YZECXj3SxEZMoUeJ1yiPsw8xANe7M7QR",
    71: "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU",
    72: "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR",
    73: "12VVRNPi4SJqUTsp6FmqDqY5sGosDtysn4",
    74: "1FWGcVDK3JGzCC3WtkYetULPszMaK2Jksv",
    75: "1J36UjUByGroXcCvmj13U6uwaVv9caEeAt",
    76: "1DJh2eHFYQfACPmrvpyWc8MSTYKh7w9eRF",
    77: "1Bxk4CQdqL9p22JEtDfdXMsng1XacifUtE",
    78: "15qF6X51huDjqTmF9BJgxXdt1xcj46Jmhb",
    79: "1ARk8HWJMn8js8tQmGUJeQHjSE7KRkn2t8",
    80: "1BCf6rHUW6m3iH2ptsvnjgLruAiPQQepLe",
    81: "15qsCm78whspNQFydGJQk5rexzxTQopnHZ",
    82: "13zYrYhhJxp6Ui1VV7pqa5WDhNWM45ARAC",
    83: "14MdEb4eFcT3MVG5sPFG4jGLuHJSnt1Dk2",
    84: "1CMq3SvFcVEcpLMuuH8PUcNiqsK1oicG2D",
    85: "1Kh22PvXERd2xpTQk3ur6pPEqFeckCJfAr",
    86: "1K3x5L6G57Y494fDqBfrojD28UJv4s5JcK",
    87: "1PxH3K1Shdjb7gSEoTX7UPDZ6SH4qGPrvq",
    88: "16AbnZjZZipwHMkYKBSfswGWKDmXHjEpSf",
    89: "19QciEHbGVNY4hrhfKXmcBBCrJSBZ6TaVt",
    90: "1L12FHH2FHjvTviyanuiFVfmzCy46RRATU",
    91: "1EzVHtmbN4fs4MiNk3ppEnKKhsmXYJ4s74",
    92: "1AE8NzzgKE7Yhz7BWtAcAAxiFMbPo82NB5",
    93: "17Q7tuG2JwFFU9rXVj3uZqRtioH3mx2Jad",
    94: "1K6xGMUbs6ZTXBnhw1pippqwK6wjBWtNpL",
    95: "19eVSDuizydXxhohGh8Ki9WY9KsHdSwoQC",
    96: "15ANYzzCp5BFHcCnVFzXqyibpzgPLWaD8b",
    97: "18ywPwj39nGjqBrQJSzZVq2izR12MDpDr8",
    98: "1CaBVPrwUxbQYYswu32w7Mj4HR4maNoJSX",
    99: "1JWnE6p6UN7ZJBN7TtcbNDoRcjFtuDWoNL",
    100: "1KCgMv8fo2TPBpddVi9jqmMmcne9uSNJ5F",
    101: "1CKCVdbDJasYmhswB6HKZHEAnNaDpK7W4n",
    102: "1PXv28YxmYMaB8zxrKeZBW8dt2HK7RkRPX",
    103: "1AcAmB6jmtU6AiEcXkmiNE9TNVPsj9DULf",
    104: "1EQJvpsmhazYCcKX5Au6AZmZKRnzarMVZu",
    105: "1CMjscKB3QW7SDyQ4c3C3DEUHiHRhiZVib",
    106: "18KsfuHuzQaBTNLASyj15hy4LuqPUo1FNB",
    107: "15EJFC5ZTs9nhsdvSUeBXjLAuYq3SWaxTc",
    108: "1HB1iKUqeffnVsvQsbpC6dNi1XKbyNuqao",
    109: "1GvgAXVCbA8FBjXfWiAms4ytFeJcKsoyhL",
    110: "12JzYkkN76xkwvcPT6AWKZtGX6w2LAgsJg",
    111: "1824ZJQ7nKJ9QFTRBqn7z7dHV5EGpzUpH3",
    112: "18A7NA9FTsnJxWgkoFfPAFbQzuQxpRtCos",
    113: "1NeGn21dUDDeqFQ63xb2SpgUuXuBLA4WT4",
    114: "174SNxfqpdMGYy5YQcfLbSTK3MRNZEePoy",
    115: "1NLbHuJebVwUZ1XqDjsAyfTRUPwDQbemfv",
    116: "1MnJ6hdhvK37VLmqcdEwqC3iFxyWH2PHUV",
    117: "1KNRfGWw7Q9Rmwsc6NT5zsdvEb9M2Wkj5Z",
    118: "1PJZPzvGX19a7twf5HyD2VvNiPdHLzm9F6",
    119: "1GuBBhf61rnvRe4K8zu8vdQB3kHzwFqSy7",
    120: "17s2b9ksz5y7abUm92cHwG8jEPCzK3dLnT",
    121: "1GDSuiThEV64c166LUFC9uDcVdGjqkxKyh",
    122: "1Me3ASYt5JCTAK2XaC32RMeH34PdprrfDx",
    123: "1CdufMQL892A69KXgv6UNBD17ywWqYpKut",
    124: "1BkkGsX9ZM6iwL3zbqs7HWBV7SvosR6m8N",
    125: "1PXAyUB8ZoH3WD8n5zoAthYjN15yN5CVq5",
    126: "1AWCLZAjKbV1P7AHvaPNCKiB7ZWVDMxFiz",
    127: "1G6EFyBRU86sThN3SSt3GrHu1sA7w7nzi4",
    128: "1MZ2L1gFrCtkkn6DnTT2e4PFUTHw9gNwaj",
    129: "1Hz3uv3nNZzBVMXLGadCucgjiCs5W9vaGz",
    130: "1Fo65aKq8s8iquMt6weF1rku1moWVEd5Ua",
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

def calculate_between_fives():
    """Calculate keys for positions between known 5/0 positions"""
    
    # Load verified keys from file
    verified_keys = {}
    try:
        with open('verified_bitcoin_sequence.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if not line or not line[0].isdigit():
                    continue
                parts = line.split('.', 1)
                if len(parts) != 2:
                    continue
                pos = int(parts[0])
                hex_and_status = parts[1].strip()
                if ' - ' in hex_and_status:
                    hex_key = hex_and_status.split(' - ')[0].strip()
                else:
                    hex_key = hex_and_status.strip()
                verified_keys[pos] = int(hex_key, 16)
    except Exception as e:
        print(f"Error loading verified keys: {e}")
        return
    
    print("=== CALCULATING BITCOIN PUZZLE KEYS BETWEEN KNOWN 5/0 POSITIONS ===")
    print("Known positions: 70, 75, 80, 85, 90, 95, 100, 110, 115, 120, 125, 130")
    print("Need to calculate: 71-74, 76-79, 81-84, 86-89, 91-94, 96-99, 101-109, 111-114, 116-119, 121-124, 126-129")
    print()
    
    # Define ranges to calculate
    ranges_to_calculate = [
        (71, 74),   # Between 70 and 75
        (76, 79),   # Between 75 and 80
        (81, 84),   # Between 80 and 85
        (86, 89),   # Between 85 and 90
        (91, 94),   # Between 90 and 95
        (96, 99),   # Between 95 and 100
        (101, 109), # Between 100 and 110
        (111, 114), # Between 110 and 115
        (116, 119), # Between 115 and 120
        (121, 124), # Between 120 and 125
        (126, 129), # Between 125 and 130
    ]
    
    results = {}
    
    for start_pos, end_pos in ranges_to_calculate:
        # Get boundary keys
        key_before = verified_keys.get(start_pos - 1)
        key_after = verified_keys.get(end_pos + 1)
        
        if key_before is None or key_after is None:
            print(f"Cannot calculate range {start_pos}-{end_pos}: missing boundary keys")
            continue
        
        print(f"\n=== Calculating positions {start_pos} to {end_pos} ===")
        print(f"Key at position {start_pos - 1}: 0x{key_before:064x}")
        print(f"Key at position {end_pos + 1}: 0x{key_after:064x}")
        
        # Calculate total difference
        total_diff = key_after - key_before
        num_steps = end_pos - start_pos + 2  # +2 because we include both boundaries
        
        print(f"Total difference: {total_diff:,}")
        print(f"Number of steps: {num_steps}")
        
        # Method 1: Linear interpolation
        print("\nMethod 1: Linear interpolation")
        step_size = total_diff // num_steps
        print(f"Average step size: {step_size:,}")
        
        for pos in range(start_pos, end_pos + 1):
            steps_from_start = pos - (start_pos - 1)
            predicted_key = key_before + (step_size * steps_from_start)
            predicted_address = privkey_to_address(predicted_key)
            
            results[pos] = {
                'key': predicted_key,
                'address': predicted_address,
                'method': 'linear'
            }
            
            # Verify against expected address
            expected_address = EXPECTED_ADDRESSES.get(pos)
            if expected_address:
                match = predicted_address == expected_address
                status = "✓ MATCH" if match else "✗ MISMATCH"
                print(f"  Position {pos}: {status}")
                print(f"    Key: 0x{predicted_key:064x}")
                print(f"    Address: {predicted_address}")
                if not match:
                    print(f"    Expected: {expected_address}")
        
        # Method 2: Check if differences follow a pattern
        print("\nMethod 2: Pattern-based (using k + constant)")
        
        # For positions 70-130, differences tend to grow exponentially
        # Let's check if the differences between consecutive positions follow a pattern
        
        # First, check what the actual differences should be based on our known pattern
        if start_pos >= 70:
            # For higher positions, growth is approximately exponential
            # Let's try to find the growth factor
            
            # Get some recent known differences to establish pattern
            recent_diffs = []
            for check_pos in range(max(2, start_pos - 20), start_pos):
                if check_pos in verified_keys and check_pos - 1 in verified_keys:
                    diff = verified_keys[check_pos] - verified_keys[check_pos - 1]
                    recent_diffs.append((check_pos, diff))
            
            if len(recent_diffs) >= 2:
                # Calculate average growth rate
                growth_rates = []
                for i in range(1, len(recent_diffs)):
                    if recent_diffs[i-1][1] > 0:
                        growth = recent_diffs[i][1] / recent_diffs[i-1][1]
                        growth_rates.append(growth)
                
                if growth_rates:
                    avg_growth = sum(growth_rates) / len(growth_rates)
                    print(f"  Average growth rate from recent positions: {avg_growth:.4f}")
                    
                    # Use geometric progression
                    last_known_pos = start_pos - 1
                    last_known_diff = recent_diffs[-1][1] if recent_diffs else step_size
                    
                    for pos in range(start_pos, end_pos + 1):
                        # Estimate difference for this position
                        steps_ahead = pos - recent_diffs[-1][0] if recent_diffs else 1
                        estimated_diff = int(last_known_diff * (avg_growth ** steps_ahead))
                        
                        # Calculate key
                        if pos - 1 in results:
                            # Use previously calculated key
                            predicted_key = results[pos - 1]['key'] + estimated_diff
                        else:
                            # Calculate from last known
                            predicted_key = key_before + estimated_diff
                        
                        predicted_address = privkey_to_address(predicted_key)
                        
                        # Check if this is better than linear
                        expected_address = EXPECTED_ADDRESSES.get(pos)
                        if expected_address and predicted_address == expected_address:
                            results[pos] = {
                                'key': predicted_key,
                                'address': predicted_address,
                                'method': 'geometric'
                            }
                            print(f"  Position {pos}: ✓ MATCH (geometric)")
                            print(f"    Key: 0x{predicted_key:064x}")
                            print(f"    Constant: {estimated_diff:,}")
    
    # Summary
    print("\n=== SUMMARY ===")
    correct_predictions = 0
    total_predictions = 0
    
    for pos, result in sorted(results.items()):
        expected = EXPECTED_ADDRESSES.get(pos)
        if expected:
            total_predictions += 1
            if result['address'] == expected:
                correct_predictions += 1
                print(f"✓ Position {pos}: CORRECT ({result['method']})")
            else:
                print(f"✗ Position {pos}: INCORRECT")
                print(f"  Predicted: {result['address']}")
                print(f"  Expected:  {expected}")
    
    if total_predictions > 0:
        accuracy = (correct_predictions / total_predictions) * 100
        print(f"\nAccuracy: {correct_predictions}/{total_predictions} ({accuracy:.1f}%)")
    
    # Output predicted keys for unknown positions
    print("\n=== PREDICTED KEYS ===")
    for pos in sorted(results.keys()):
        if pos not in verified_keys:
            result = results[pos]
            print(f"Position {pos}:")
            print(f"  Key: 0x{result['key']:064x}")
            print(f"  Address: {result['address']}")
            print(f"  Method: {result['method']}")

if __name__ == "__main__":
    calculate_between_fives() 