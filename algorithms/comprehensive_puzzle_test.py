#!/usr/bin/env python3
"""Comprehensive test of multiple pattern types for Bitcoin puzzle positions 69+"""

import hashlib
import base58
import ecdsa
import math

# Secp256k1 constants
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

# Known puzzle addresses (unsolved puzzles 69+)
PUZZLE_ADDRESSES = {
    69: "19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG",
    70: "19YZECXj3SxEZMoUeJ1yiPsw8xANe7M7QR", 
    71: "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU",
    72: "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR",
    73: "12VVRNPi4SJqUTsp6FmqDqY5sGosDtysn4",
    74: "1FWGcVDK3JGzCC3WtkYetULPszMaK2Jksv",
    75: "1J36UjUByGroXcCvmj13U6uwaVv9caEeAt",
}

def sha256(data):
    return hashlib.sha256(data).digest()

def ripemd160(data):
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()

def hash160(data):
    return ripemd160(sha256(data))

def base58_encode(data):
    versioned = b'\x00' + data
    checksum = sha256(sha256(versioned))[:4]
    return base58.b58encode(versioned + checksum).decode()

def privkey_to_pubkey(privkey_int, compressed=True):
    sk = ecdsa.SigningKey.from_secret_exponent(privkey_int, curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    point = vk.pubkey.point
    
    if compressed:
        x = point.x()
        y = point.y()
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        return prefix + x.to_bytes(32, 'big')
    else:
        x = point.x()
        y = point.y()
        return b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')

def pubkey_to_address(pubkey_bytes):
    h160 = hash160(pubkey_bytes)
    return base58_encode(h160)

def test_pattern_type(pattern_name, key_generator, base_key, target_address, max_iterations=1000):
    """Test a specific pattern type"""
    print(f"  Testing {pattern_name}...")
    
    for i in range(max_iterations):
        try:
            predicted_key = key_generator(base_key, i)
            if predicted_key <= 0 or predicted_key >= N:
                continue
                
            pubkey_compressed = privkey_to_pubkey(predicted_key, compressed=True)
            predicted_address = pubkey_to_address(pubkey_compressed)
            
            if predicted_address == target_address:
                return predicted_key, i
                
        except Exception:
            continue
    
    return None, None

def comprehensive_puzzle_test():
    """Test multiple pattern types comprehensively"""
    
    print("🔍 COMPREHENSIVE BITCOIN PUZZLE TESTING")
    print("=" * 60)
    print("Testing multiple pattern types with wider search spaces...")
    print()
    
    # Load the last verified key (assuming position 68 is the last verified)
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
                
                # Only load positions up to 68 as verified
                if pos <= 68 and 'KNOWN' in hex_and_status:
                    verified_keys[pos] = int(hex_key, 16)
                    
        print(f"✓ Loaded {len(verified_keys)} verified keys")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    # Get base key (position 68)
    base_key = verified_keys[68]
    print(f"Base key (pos 68): 0x{base_key:x}")
    print()
    
    # Test different positions
    for target_pos in [69, 70, 71]:  # Start with first few
        if target_pos not in PUZZLE_ADDRESSES:
            continue
            
        target_address = PUZZLE_ADDRESSES[target_pos]
        print(f"--- Testing Position {target_pos} ---")
        print(f"Target: {target_address}")
        
        patterns_to_test = []
        
        # Pattern 1: Powers of 2 with adjustments (refined)
        for shift in range(64, 70):
            base_power = 1 << shift
            patterns_to_test.append((
                f"k + 2^{shift}",
                lambda k, i, bp=base_power: (k + bp) % N
            ))
            # With small adjustments
            for adj in [1, -1, 2, -2, 3, -3, 5, -5, 7, -7, 11, -11]:
                patterns_to_test.append((
                    f"k + 2^{shift} + {adj}",
                    lambda k, i, bp=base_power, a=adj: (k + bp + a) % N
                ))
        
        # Pattern 2: Multiplicative patterns
        for mult in range(2, 20):
            patterns_to_test.append((
                f"k * {mult}",
                lambda k, i, m=mult: (k * m) % N
            ))
        
        # Pattern 3: Position-based patterns
        patterns_to_test.append((
            "k + pos^2",
            lambda k, i: (k + target_pos * target_pos) % N
        ))
        patterns_to_test.append((
            "k * pos",
            lambda k, i: (k * target_pos) % N
        ))
        patterns_to_test.append((
            "k + pos!",
            lambda k, i: (k + math.factorial(target_pos % 10)) % N  # Limit factorial
        ))
        
        # Pattern 4: Fibonacci-like
        patterns_to_test.append((
            "k + k (doubling)",
            lambda k, i: (k + k) % N
        ))
        
        # Pattern 5: Hash-like transformations
        for mult in [31, 37, 41, 97, 101]:
            patterns_to_test.append((
                f"k * {mult} + pos",
                lambda k, i, m=mult: (k * m + target_pos) % N
            ))
        
        # Pattern 6: Bitwise operations
        for shift in range(1, 10):
            patterns_to_test.append((
                f"k << {shift}",
                lambda k, i, s=shift: (k << s) % N
            ))
            patterns_to_test.append((
                f"k >> {shift}",
                lambda k, i, s=shift: (k >> s) % N
            ))
        
        # Pattern 7: XOR patterns
        for xor_val in [target_pos, target_pos * 2, target_pos * target_pos]:
            patterns_to_test.append((
                f"k XOR {xor_val}",
                lambda k, i, x=xor_val: (k ^ x) % N
            ))
        
        # Pattern 8: Prime-based
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        for prime in primes:
            patterns_to_test.append((
                f"k + {prime}^target_pos",
                lambda k, i, p=prime: (k + pow(p, target_pos % 10, N)) % N  # Limit exponent
            ))
        
        # Pattern 9: Iterative search around powers of 2
        for shift in range(65, 69):
            base_power = 1 << shift
            patterns_to_test.append((
                f"k + 2^{shift} + i",
                lambda k, i, bp=base_power: (k + bp + i) % N
            ))
            patterns_to_test.append((
                f"k + 2^{shift} - i",
                lambda k, i, bp=base_power: (k + bp - i) % N
            ))
        
        # Pattern 10: Square and cube patterns
        patterns_to_test.append((
            "k^2 + pos",
            lambda k, i: (pow(k, 2, N) + target_pos) % N
        ))
        patterns_to_test.append((
            "k + pos^3",
            lambda k, i: (k + pow(target_pos, 3)) % N
        ))
        
        print(f"  Testing {len(patterns_to_test)} different patterns...")
        
        # Test each pattern
        found_match = False
        for pattern_name, key_generator in patterns_to_test:
            result_key, iteration = test_pattern_type(
                pattern_name, key_generator, base_key, target_address, max_iterations=10000
            )
            
            if result_key is not None:
                print(f"🎉 MATCH FOUND!")
                print(f"   Pattern: {pattern_name}")
                if 'i' in pattern_name:
                    print(f"   Formula: {pattern_name.replace('i', str(iteration))}")
                print(f"   Key: 0x{result_key:x}")
                print(f"   Address: {target_address}")
                found_match = True
                break
        
        if not found_match:
            print(f"❌ No match found for position {target_pos}")
            # Show closest attempts for the main power of 2 pattern
            print(f"   Closest attempts (2^66):")
            base_power = 1 << 66
            for adj in [0, 1000, -1000, 10000, -10000]:
                test_key = (base_key + base_power + adj) % N
                try:
                    pubkey_compressed = privkey_to_pubkey(test_key, compressed=True)
                    test_address = pubkey_to_address(pubkey_compressed)
                    print(f"     k + 2^66 + {adj:,} -> {test_address}")
                except:
                    continue
        
        print()
    
    print("=" * 60)
    print("🏁 COMPREHENSIVE TEST COMPLETE")
    print()
    print("💡 INSIGHTS:")
    print("- If no matches found, the pattern may be much more complex")
    print("- Real Bitcoin puzzles use sophisticated key generation")
    print("- Pattern might involve cryptographic operations not tested here")
    print("- Consider that puzzles 69+ might use entirely different generation methods")

if __name__ == "__main__":
    comprehensive_puzzle_test() 