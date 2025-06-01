#!/usr/bin/env python3
"""
Extract private keys from the spending transaction of positions 161-256.
When the creator spent these addresses, the signatures and public keys were exposed.
We need to test different patterns to find how these keys were generated.
"""

import hashlib
import ecdsa
from ecdsa import SigningKey, SECP256k1
from ecdsa.util import sigdecode_der

# Sample signature data from positions 161-165 (from our investigation)
SPENDING_DATA = {
    161: {
        'address': '1JkqBQcC4tHcb1JfdCH6nrWYwTPGznHANh',
        'pubkey': '031dcf49b480cee5f1a7200ea94795a1c7f69e144f11f031123c14c65077823dcb',
        'signature': '304402200473b7961976340ba4afde84fadba20dcb268aac37221330d4f36f102ee05c2b0220107e185e9360154aae8e94a5550b87b28559e2d2a262f967ff21702ff7625778',
        'position': 161
    },
    162: {
        'address': '17DTUTXUcUYEgrr5GhivxYei4Lrs1xMnS2',
        'pubkey': '03294d33f5e7b98c885ff540fd3f747010999f640d8fdb021f5a13ef3d06c36a58',
        'signature': '3044022040d5ec7eb54900e560cac0912b5a08f339636a9cba2bf778a7ff8c780abae5220220263c238cfba6144c824307f3662827e2b3b620cbfabf0a0152ad7ba8de73eb8c',
        'position': 162
    },
    163: {
        'address': '1H6e7SLxv6ZUbuAaZpeUdVNfh3cKBWJRmx',
        'pubkey': '02ee740ba74efc08bf39d01ccb7e34f50afe2f4677a9e09755e7fe3808e0cbbac9',
        'signature': '3044022076ab54efee7cd6e8c56f9cfc73cac629e455360551602180f8355687d50ba5c002203632491dfb2d36fd324beae3a3270479c973e8c008e3c3ddce64b129abaa1864',
        'position': 163
    },
    164: {
        'address': '1LjQKurNtEDgMdqeCoWRFhHp1FPnLU77Q4',
        'pubkey': '0312163c60548244d6e565bd877b98808b73830c537efde357c8b5f8c623fb2028',
        'signature': '3045022100e6a730c91eb9b369f33032272934019e75860a78e9ed9571de3884a87c524c2b022068af961d221f56d40a2d4790d8e97d3ae2e3ca521141be1e4c6c077cdf513989',
        'position': 164
    },
    165: {
        'address': '1F7ZjibYug9bLW3YvkkwBZLrhfLtNjgYrX',
        'pubkey': '037c6fcde6a2e0fd57ce21bb4352f7bb38859d2af5388b27ebfed107907e060c5c',
        'signature': '3044022064b32ae968ddb8b4d0346e3f1b66f7ae3f9d5de9660e498a341415e9ddda562602201d81608b0f86a61432a0f5a6df6bc5a11dfefa1324916d6569c78cb01829bd91',
        'position': 165
    }
}

def test_private_key_candidate(candidate_key, pubkey_hex):
    """
    Test if a candidate private key generates the given public key
    """
    try:
        # Generate public key from candidate private key
        sk = SigningKey.from_secret_exponent(candidate_key, curve=SECP256k1)
        vk = sk.get_verifying_key()
        
        # Get compressed public key
        point = vk.pubkey.point
        x = point.x()
        y = point.y()
        
        # Determine if y is even or odd for compression
        if y % 2 == 0:
            compressed_pubkey = '02' + format(x, '064x')
        else:
            compressed_pubkey = '03' + format(x, '064x')
        
        return compressed_pubkey == pubkey_hex
        
    except Exception as e:
        return False

def test_bitcoin_puzzle_patterns(position, pubkey_hex):
    """
    Test various Bitcoin puzzle generation patterns for the upper positions
    """
    # Pattern 1: Simple position
    candidate = position
    if test_private_key_candidate(candidate, pubkey_hex):
        return candidate, "position"
    
    # Pattern 2: Position in specific bit range (2^n to 2^(n+1)-1)
    # For position 161, bit range would be around 8 bits (161 = 0xa1)
    bit_length = position.bit_length()
    range_start = 2**(bit_length-1)
    range_offset = position - 161  # Offset from start of this range
    candidate = range_start + range_offset
    if test_private_key_candidate(candidate, pubkey_hex):
        return candidate, f"bit_range_{bit_length}bit + offset"
    
    # Pattern 3: Powers of 2 related
    for power in range(7, 12):  # Test 2^7 to 2^11
        candidate = 2**power + (position - 161)
        if test_private_key_candidate(candidate, pubkey_hex):
            return candidate, f"2^{power} + (pos-161)"
    
    # Pattern 4: Some multiple of the position
    for mult in [1, 2, 3, 4, 5, 10, 16, 32, 64, 128, 256]:
        candidate = position * mult
        if test_private_key_candidate(candidate, pubkey_hex):
            return candidate, f"position * {mult}"
    
    # Pattern 5: Position shifted by some constant
    for shift in [100, 128, 160, 200, 256, 512, 1000, 1024]:
        candidate = position + shift
        if test_private_key_candidate(candidate, pubkey_hex):
            return candidate, f"position + {shift}"
        
        candidate = position - shift
        if candidate > 0 and test_private_key_candidate(candidate, pubkey_hex):
            return candidate, f"position - {shift}"
    
    # Pattern 6: Bitwise operations
    for shift_bits in range(1, 8):
        candidate = position << shift_bits
        if test_private_key_candidate(candidate, pubkey_hex):
            return candidate, f"position << {shift_bits}"
        
        candidate = position >> shift_bits
        if candidate > 0 and test_private_key_candidate(candidate, pubkey_hex):
            return candidate, f"position >> {shift_bits}"
    
    # Pattern 7: XOR with constants
    for xor_val in [0xFF, 0x100, 0x200, 0x400, 0x800, 0x1000]:
        candidate = position ^ xor_val
        if test_private_key_candidate(candidate, pubkey_hex):
            return candidate, f"position XOR 0x{xor_val:x}"
    
    # Pattern 8: Known Bitcoin puzzle bit ranges
    # Position 161 would be in range for ~8-bit keys
    # Try the actual bit range patterns
    for bit_range in range(7, 12):
        range_start = 2**bit_range
        range_end = 2**(bit_range + 1) - 1
        
        # Try position within this bit range
        if range_start <= position <= range_end:
            candidate = position
            if test_private_key_candidate(candidate, pubkey_hex):
                return candidate, f"{bit_range+1}-bit range: position"
    
    # Pattern 9: Try sequential values around expected ranges
    # If positions 161-256 use 8-bit range (128-255), try that
    if 161 <= position <= 256:
        # Map to 8-bit range
        candidate = 128 + (position - 161)  # Maps 161->128, 162->129, etc.
        if test_private_key_candidate(candidate, pubkey_hex):
            return candidate, f"8-bit mapping: 128 + (pos-161)"
    
    # Pattern 10: Fibonacci-like or additive sequences
    # This is harder without knowing the starting point
    
    return None, "not found"

def brute_force_private_key(pubkey_hex, max_attempts=100000):
    """
    Brute force search for private key in reasonable ranges
    """
    print(f"  Brute forcing private key (max {max_attempts} attempts)...")
    
    # Try common ranges first
    ranges_to_try = [
        (1, 1000),          # Very small keys
        (128, 256),         # 8-bit range
        (256, 512),         # 9-bit range  
        (512, 1024),        # 10-bit range
        (1024, 2048),       # 11-bit range
        (2048, 4096),       # 12-bit range
        (160, 260),         # Around the position numbers
        (2**7, 2**8),       # Exactly 8-bit
        (2**8, 2**9),       # Exactly 9-bit
    ]
    
    total_tested = 0
    
    for start, end in ranges_to_try:
        if total_tested >= max_attempts:
            break
            
        print(f"    Testing range {start}-{end}...")
        
        for candidate in range(start, min(end + 1, start + max_attempts - total_tested)):
            if test_private_key_candidate(candidate, pubkey_hex):
                return candidate, f"brute_force_range_{start}_{end}"
            
            total_tested += 1
            
            if total_tested >= max_attempts:
                break
    
    return None, f"brute_force_failed_after_{total_tested}"

def analyze_private_key_pattern():
    """
    Analyze the pattern in private keys for positions 161-165
    """
    print("=== ANALYZING PRIVATE KEY PATTERN FOR POSITIONS 161-165 ===\n")
    
    private_keys = {}
    patterns = {}
    
    for pos, data in SPENDING_DATA.items():
        print(f"Position {pos}:")
        print(f"  Address: {data['address']}")
        print(f"  Public Key: {data['pubkey']}")
        
        # Try different patterns
        private_key, pattern = test_bitcoin_puzzle_patterns(pos, data['pubkey'])
        
        if private_key:
            private_keys[pos] = private_key
            patterns[pos] = pattern
            print(f"  ✓ FOUND: Private Key = 0x{private_key:x} ({private_key})")
            print(f"  ✓ Pattern: {pattern}")
        else:
            # Try brute force as last resort
            print(f"  No pattern match found, trying brute force...")
            private_key, pattern = brute_force_private_key(data['pubkey'], max_attempts=10000)
            
            if private_key:
                private_keys[pos] = private_key
                patterns[pos] = pattern
                print(f"  ✓ FOUND: Private Key = 0x{private_key:x} ({private_key})")
                print(f"  ✓ Pattern: {pattern}")
            else:
                print(f"  ✗ Could not find private key")
        
        print()
    
    if private_keys:
        print("=== PATTERN ANALYSIS ===")
        print("Found private keys:")
        for pos in sorted(private_keys.keys()):
            print(f"  Position {pos}: private_key = 0x{private_keys[pos]:x} ({private_keys[pos]}) - {patterns[pos]}")
        
        # Look for relationships between the private keys
        if len(private_keys) >= 2:
            sorted_positions = sorted(private_keys.keys())
            print(f"\nAnalyzing relationships:")
            
            for i in range(len(sorted_positions)):
                pos = sorted_positions[i]
                key = private_keys[pos]
                
                # Check relationship to position
                print(f"  Position {pos}: key={key}, key-pos={key-pos}, key/pos={key/pos:.2f}")
                
                # Check differences
                if i > 0:
                    prev_pos = sorted_positions[i-1]
                    prev_key = private_keys[prev_pos]
                    diff = key - prev_key
                    pos_diff = pos - prev_pos
                    print(f"    Difference from previous: {diff} (position diff: {pos_diff})")
    
    return private_keys

def main():
    print("=== EXTRACTING PRIVATE KEYS FROM SPENDING TRANSACTION ===")
    print("Transaction: 5d45587cfd1d5b0fb826805541da7d94c61fe432259e68ee26f4a04544384164")
    print("This transaction spent positions 161-256, exposing their cryptographic data.\n")
    
    # Analyze the pattern
    private_keys = analyze_private_key_pattern()
    
    if private_keys:
        print("\n=== SUCCESS! ===")
        print("We found private keys for the upper positions!")
        print("This confirms that these positions were indeed spent by the creator.")
        print("\nNext steps:")
        print("1. Extract all 96 private keys from the transaction")
        print("2. Analyze the complete pattern")
        print("3. Apply this knowledge to predict missing positions 69, 71-74, etc.")
    else:
        print("\nPrivate keys not found with current methods.")
        print("The pattern may be more complex or require additional analysis.")

if __name__ == "__main__":
    main() 