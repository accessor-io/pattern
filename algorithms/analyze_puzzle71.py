#!/usr/bin/env python3
"""
Analyze Bitcoin Puzzle #71 Sequence
=================================
Using functions from key_sequence_generator.py to analyze the sequence
"""

import hashlib
import base58
from ecdsa import SigningKey, SECP256k1
from key_sequence_generator import (
    analyze_transitions,
    analyze_sequence_transformations,
    analyze_special_operations,
    analyze_differences_between_known_keys,
    analyze_control_characters,
    get_prime_factors
)

# Known addresses around position 71
SEQUENCE = {
    69: "19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG",
    70: "19YZECXj3SxEZMoUeJ1yiPsw8xANe7M7QR",
    71: "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU",  # Target
    72: "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR",
    73: "12VVRNPi4SJqUTsp6FmqDqY5sGosDtysn4"
}

# Known private keys
KNOWN_KEYS = {
    64: 0x18e186a0b4c7594d,
    65: 0x13a52c20c7e93900,
    66: 0x1368d75b7a31a9b9,
    67: 0x1b728d02d6dfe00d,
    68: 0x1f685e68d87bb9fb,
    69: 0x101d83275fb2bc7e0c,
    70: 0x349b84b6431a6c4ef1
}

def analyze_sequence():
    """Analyze the sequence pattern"""
    print("\nAnalyzing Sequence Pattern:")
    print("=========================")
    
    # Analyze mathematical relationships
    print("\nMathematical Relationship Analysis:")
    for pos in sorted(KNOWN_KEYS.keys()):
        key = KNOWN_KEYS[pos]
        
        print(f"\nPosition {pos}:")
        print(f"Key: 0x{key:x}")
        
        # Calculate key/position ratio
        ratio = key / pos
        print(f"Key/Position: {ratio:.2f}")
        
        # Calculate key modulo position
        mod = key % pos
        print(f"Key%Position: {mod}")
        
        # Check for special mathematical properties
        # 1. Perfect squares/cubes
        sqrt = int(key ** 0.5)
        if sqrt * sqrt == key:
            print("Key is a perfect square!")
        
        cbrt = int(key ** (1/3))
        if cbrt ** 3 == key:
            print("Key is a perfect cube!")
        
        # 2. Prime factorization
        factors = []
        n = key
        for i in range(2, int(n ** 0.5) + 1):
            while n % i == 0:
                factors.append(i)
                n //= i
        if n > 1:
            factors.append(n)
        print(f"Prime factors: {factors[:10]}...")  # Show first 10 factors
        
        # 3. Binary properties
        key_bin = bin(key)[2:]
        ones = key_bin.count('1')
        zeros = len(key_bin) - ones
        print(f"Binary 1s: {ones}")
        print(f"Binary 0s: {zeros}")
        print(f"1s/0s ratio: {ones/zeros:.2f}")
    
    # Try to predict position 71's key
    print("\nPredicting position 71:")
    predictions = []
    
    # Method 1: Ratio trend
    ratios = [KNOWN_KEYS[pos] / pos for pos in sorted(KNOWN_KEYS.keys())]
    ratio_diffs = [ratios[i+1] - ratios[i] for i in range(len(ratios)-1)]
    avg_ratio_diff = sum(ratio_diffs) / len(ratio_diffs)
    pred_ratio = ratios[-1] + avg_ratio_diff
    pred1 = int(pred_ratio * 71)
    predictions.append(("Ratio Trend", pred1))
    
    # Method 2: Position bits
    pos_71_bin = bin(71)[2:].zfill(8)  # 01000111
    key_70 = KNOWN_KEYS[70]
    key_70_bin = bin(key_70)[2:].zfill(80)
    # Use position bits to modify key_70
    pred2_bin = list(key_70_bin)
    for i, bit in enumerate(pos_71_bin):
        if bit == '1':
            # Set corresponding bits in the key
            pred2_bin[i+19] = '1'  # Most keys have 19 leading zeros
    pred2 = int(''.join(pred2_bin), 2)
    predictions.append(("Position Bits", pred2))
    
    # Method 3: Modulo pattern
    mods = [KNOWN_KEYS[pos] % pos for pos in sorted(KNOWN_KEYS.keys())]
    mod_diffs = [mods[i+1] - mods[i] for i in range(len(mods)-1)]
    avg_mod_diff = sum(mod_diffs) / len(mod_diffs)
    pred_mod = mods[-1] + avg_mod_diff
    base = (key_70 // 70) * 71
    pred3 = base + int(pred_mod)
    predictions.append(("Modulo Pattern", pred3))
    
    # Method 4: Position transform
    pos_70_bin = bin(70)[2:].zfill(8)
    pos_71_bin = bin(71)[2:].zfill(8)
    # Find the transformation between positions
    pos_xor = int(pos_70_bin, 2) ^ int(pos_71_bin, 2)
    # Apply similar transformation to key
    pred4 = key_70 ^ (pos_xor << (len(bin(key_70)[2:]) - 8))
    predictions.append(("Position Transform", pred4))
    
    # Method 5: Difference pattern
    diffs = [KNOWN_KEYS[pos] - KNOWN_KEYS[pos-1] for pos in sorted(KNOWN_KEYS.keys())[1:]]
    diff_ratios = [diffs[i+1]/diffs[i] for i in range(len(diffs)-1)]
    avg_diff_ratio = sum(diff_ratios) / len(diff_ratios)
    pred_diff = int(diffs[-1] * avg_diff_ratio)
    pred5 = key_70 + pred_diff
    predictions.append(("Difference Pattern", pred5))
    
    # Method 6: New Sequence Pattern Analysis
    new_sequence = [
        0x5749f,   # 357,279
        0xd2c55,   # 863,829
        0x1ba534,  # 1,790,260
        0x2de40f,  # 3,002,895
        0x556e52,  # 5,597,010
        0xdc2a04,  # 14,415,108
        0x1fa5ee5  # 33,201,509
    ]
    
    # Calculate growth ratios
    ratios = [new_sequence[i+1]/new_sequence[i] for i in range(len(new_sequence)-1)]
    print("\nNew Sequence Analysis:")
    print("Growth ratios:", [f"{r:.2f}" for r in ratios])
    
    # Calculate differences
    diffs = [new_sequence[i+1] - new_sequence[i] for i in range(len(new_sequence)-1)]
    print("Differences:", diffs)
    
    # Try to predict next value using average growth
    avg_growth = sum(ratios) / len(ratios)
    pred6 = int(new_sequence[-1] * avg_growth)
    predictions.append(("New Sequence Pattern", pred6))
    
    # Analyze bit patterns in new sequence
    print("\nBit Pattern Analysis:")
    for i, val in enumerate(new_sequence):
        bin_val = bin(val)[2:]
        print(f"Value {i+1}: {len(bin_val)} bits, leading zeros: {64 - len(bin_val)}")
        if i > 0:
            prev_bin = bin(new_sequence[i-1])[2:]
            xor_val = val ^ new_sequence[i-1]
            print(f"XOR with previous: 0x{xor_val:x}")
            
    # Try prediction based on bit patterns
    last_val = new_sequence[-1]
    last_bin = bin(last_val)[2:]
    # Predict next value using bit pattern transformation
    pred7 = last_val + (last_val >> 4) + (1 << len(last_bin))
    predictions.append(("Bit Pattern Transform", pred7))
    
    # Analyze prime factorization patterns
    print("\nPrime Factorization Analysis:")
    def get_prime_factors(n):
        factors = []
        d = 2
        while n > 1:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
            if d * d > n:
                if n > 1:
                    factors.append(n)
                break
        return factors

    common_small_factors = set()
    first = True
    for val in new_sequence:
        factors = get_prime_factors(val)
        if first:
            common_small_factors = set(f for f in factors if f < 100)
            first = False
        else:
            common_small_factors &= set(f for f in factors if f < 100)
        print(f"0x{val:x}: {factors}")
    
    print(f"Common small factors across all numbers: {sorted(list(common_small_factors))}")
    
    # Try prediction based on prime factorization pattern
    last_factors = get_prime_factors(new_sequence[-1])
    # Predict maintaining the common factor of 3 and scaling the largest prime
    pred8 = 3 * (last_factors[-1] * 2 + 1)  # Multiply largest prime by 2 and ensure odd
    predictions.append(("Prime Factorization Pattern", pred8))
    
    # Analyze patterns in powers of 2 and largest primes
    print("\nDetailed Prime Pattern Analysis:")
    last_powers_of_2 = []
    largest_primes = []
    
    for val in new_sequence:
        factors = get_prime_factors(val)
        power_of_2 = len([f for f in factors if f == 2])
        last_powers_of_2.append(power_of_2)
        largest_prime = max(factors)
        largest_primes.append(largest_prime)
        print(f"0x{val:x}: 2^{power_of_2} × {' × '.join(str(f) for f in sorted(set(factors)) if f != 2)}")
    
    print("\nPowers of 2 pattern:", last_powers_of_2)
    print("Largest prime ratios:", [f"{largest_primes[i]/largest_primes[i-1]:.2f}" for i in range(1, len(largest_primes))])
    
    # Predict next value based on combined pattern
    # If the pattern of 2's powers continues: none -> 2² -> none -> 2¹ -> 2² -> none -> ?
    # And largest prime grows by approximately factor of 9-10
    last_largest_prime = largest_primes[-1]
    predicted_largest_prime = int(last_largest_prime * 9.5)  # Using average of recent growth
    # No power of 2 expected in next number based on pattern
    pred9 = 3 * predicted_largest_prime  # Base prediction on 3 × largest_prime pattern
    predictions.append(("Refined Prime Pattern", pred9))
    
    # Method 7: Analyze using key_sequence_generator functions
    print("\nKey Sequence Generator Analysis for Position 71:")
    
    # Target address for position 71
    TARGET_71 = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"
    
    # Known sequence around position 71
    SEQUENCE_AROUND_71 = {
        69: "19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG",
        70: "19YZECXj3SxEZMoUeJ1yiPsw8xANe7M7QR",
        71: TARGET_71,
        72: "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR",
        73: "12VVRNPi4SJqUTsp6FmqDqY5sGosDtysn4"
    }
    
    # Run specialized analysis
    print("\nAnalyzing transitions around position 71...")
    analyze_transitions(analysis_range=5)
    
    print("\nAnalyzing sequence transformations...")
    analyze_sequence_transformations(max_positions=71, verbose=True)
    
    print("\nAnalyzing special operations...")
    analyze_special_operations(analysis_range=5, verbose=True)
    
    print("\nAnalyzing differences between known keys...")
    analyze_differences_between_known_keys(analysis_range=5)
    
    print("\nAnalyzing control characters...")
    analyze_control_characters(analysis_range=5)
    
    # Try prediction based on combined analysis
    pred10 = analyze_special_operations(analysis_range=5, verbose=False)  # Get prediction from special ops
    if pred10:
        predictions.append(("Special Operations Pattern", pred10))
    
    print("\nTesting predictions:")
    for method, predicted_key in predictions:
        print(f"\n{method}:")
        print(f"Predicted key: 0x{predicted_key:x}")
        if verify_key(predicted_key):
            print("✅ VALID KEY FOUND!")
            return predicted_key
        print("❌ Invalid key")
    
    return None

def verify_key(private_key: int) -> bool:
    """Verify if a private key generates the target address"""
    try:
        # Convert to public key
        privkey_hex = format(private_key, '064x')
        privkey_bytes = bytes.fromhex(privkey_hex)
        sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()
        x = vk.pubkey.point.x()
        y = vk.pubkey.point.y()
        
        # Compressed public key
        if y % 2 == 0:
            pubkey_bytes = b'\x02' + x.to_bytes(32, 'big')
        else:
            pubkey_bytes = b'\x03' + x.to_bytes(32, 'big')
        
        # Hash160 (SHA256 + RIPEMD160)
        sha256_hash = hashlib.sha256(pubkey_bytes).digest()
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
        
        # Add version byte and checksum
        versioned_payload = b'\x00' + ripemd160_hash
        checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
        address_bytes = versioned_payload + checksum
        
        # Base58 encode
        address = base58.b58encode(address_bytes).decode()
        return address == SEQUENCE[71]
    except Exception:
        return False

def main():
    print("Bitcoin Puzzle #71 Sequence Analysis")
    print("===================================")
    
    predicted_key = analyze_sequence()
    
    if predicted_key:
        print("\n✅ SUCCESS! Found the correct private key!")
        print(f"Private Key (hex): 0x{predicted_key:x}")
    else:
        print("\n❌ No valid key found through sequence analysis.")

if __name__ == "__main__":
    main() 