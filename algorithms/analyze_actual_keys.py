#!/usr/bin/env python3
"""
🔍 ACTUAL BITCOIN PUZZLE KEY ANALYSIS
Analyzes the real known private keys to discover the true generation patterns
"""

import hashlib
import base58
import ecdsa
import math
from typing import Dict, List, Tuple, Optional

# Secp256k1 constants
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# ACTUAL KNOWN PUZZLE DATA (corrected from user's screenshot)
ACTUAL_PUZZLE_DATA = {
    64: {
        'range_start': 0x8000000000000000,
        'range_end': 0xffffffffffffffff, 
        'private_key': 0xf7051f27b09112d4,
        'address': '16jY7qLJnxb7CHZyqBP8qca9d51gAjyXQN'
    },
    65: {
        'range_start': 0x10000000000000000,
        'range_end': 0x1ffffffffffffffff,
        'private_key': 0x1a838b13505b26867,
        'address': '18ZMbwUFLMHoZBbfpCjUJQTCMCbktshgpe'
    },
    66: {
        'range_start': 0x20000000000000000,
        'range_end': 0x3ffffffffffffffff,
        'private_key': 0x2832ed74f2b5e35ee,
        'address': '13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so'
    },
    67: {
        'range_start': 0x40000000000000000,
        'range_end': 0x7ffffffffffffffff,
        'private_key': 0x730fc235c1942c1ae,
        'address': '1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9'
    },
    68: {
        'range_start': 0x80000000000000000,
        'range_end': 0xfffffffffffffffff,
        'private_key': 0xbebb3940cd0fc1491,
        'address': '1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ'
    },
    69: {
        'range_start': 0x100000000000000000,
        'range_end': 0x1ffffffffffffffff,
        'private_key': 0x101d832275fb2bc7e0c,  # This might be estimated/generated
        'address': '19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG'
    },
    70: {
        'range_start': 0x200000000000000000,
        'range_end': 0x3fffffffffffffffff,
        'private_key': 0x349b84b6431a6c4ef1,
        'address': '19YZECXj3SxEZMoUeJ1yiPsw8xANe7M7QR'
    },
    75: {
        'range_start': 0x400000000000000000000,
        'range_end': 0x7ffffffffffffffffff,
        'private_key': 0x4c5ce114686a1336e07,
        'address': '1J36UjUByGroXcCvmj13U6uwaVv9caEeAt'
    },
    80: {
        'range_start': 0x800000000000000000000,
        'range_end': 0xfffffffffffffffffffff,
        'private_key': 0xea1a5c66dcc11b5ad180,
        'address': '1BCf6rHUW6m3iH2ptsvnjgLruAiPQXePLe'
    },
    85: {
        'range_start': 0x1000000000000000000000,
        'range_end': 0x1fffffffffffffffffffff,
        'private_key': 0x11720c4f018d51b8cebba8,
        'address': '1Kh22PvXERd2xpTQK3ur6pPEqFeckCJfAr'
    },
    90: {
        'range_start': 0x20000000000000000000000,
        'range_end': 0x3ffffffffffffffffffffff,
        'private_key': 0x2ce00bb2136a445c71e85bf,
        'address': '1L12FHH2FHjvTviyanuiFVfmzCy46RRATU'
    },
    95: {
        'range_start': 0x400000000000000000000000,
        'range_end': 0x7fffffffffffffffffffffff,
        'private_key': 0x527a792b183c7f64a0e8b1f4,
        'address': '19eVSDuizydXxhohGh8Ki9WY9KsHdSwoQu'
    },
    100: {
        'range_start': 0x8000000000000000000000000,
        'range_end': 0xfffffffffffffffffffffffff,
        'private_key': 0xaf55fc59c335c8ec67ed24826,
        'address': '1KCgMv3fo2TPBpddVi9qmMmcne9USJNJ5e'
    },
    105: {
        'range_start': 0x10000000000000000000000000,
        'range_end': 0x1ffffffffffffffffffffffffff,
        'private_key': 0x16f14fc2054cd87ee6396b33df3,
        'address': '1CMjscKB3QW7SDyQ4c3C3DEUHiHRhiZVib'
    },
    110: {
        'range_start': 0x200000000000000000000000000,
        'range_end': 0x3ffffffffffffffffffffffffffffff,
        'private_key': 0x35c0d7234df7deb0f20cf7062444,
        'address': '12JzYkkN76xkwvcPT6AWKZtGX6w2LAgsJg'
    },
    115: {
        'range_start': 0x4000000000000000000000000000,
        'range_end': 0x7fffffffffffffffffffffffffffff,
        'private_key': 0x60f4d11574f5deee49961d9609ac6,
        'address': '1NLbHuJebVwUZ1XqDjsAyFTRUPwDQbemfv'
    },
    120: {
        'range_start': 0x80000000000000000000000000000,
        'range_end': 0xffffffffffffffffffffffffffffffffffff,
        'private_key': 0xb10f22572c497a836ea187f2e1fc23,
        'address': '17s2b9ksz5y7abUm92cHwG8jEPCzK3dLnT'
    },
    125: {
        'range_start': 0x1000000000000000000000000000000,
        'range_end': 0x1ffffffffffffffffffffffffffffff,
        'private_key': 0x1c533b6bb7f0804e09960225e44877ac,
        'address': '1PXAyUB8ZoH3WD8n5zoAthYjN15yN5CVq5'
    },
    130: {
        'range_start': 0x20000000000000000000000000000000,
        'range_end': 0x3fffffffffffffffffffffffffffff,
        'private_key': 0x33e7665705359f04f28b88cf897c603c9,
        'address': '1Fo65aKq8s8iquMt6weF1rku1moWVEd5Ua'
    }
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

def analyze_position_within_range(position: int, private_key: int, range_start: int, range_end: int):
    """Analyze where the private key falls within its designated range"""
    range_size = range_end - range_start + 1
    offset = private_key - range_start
    position_ratio = offset / range_size
    
    return {
        'range_size': range_size,
        'offset': offset,
        'position_ratio': position_ratio,
        'hex_offset': hex(offset),
        'percentage_into_range': position_ratio * 100
    }

def find_mathematical_relationships():
    """Find mathematical relationships in the actual puzzle keys"""
    
    print("🔍 ANALYZING ACTUAL BITCOIN PUZZLE KEYS")
    print("=" * 80)
    print("Discovering the real mathematical patterns from known solutions...")
    print()
    
    print("📊 DETAILED POSITION ANALYSIS:")
    print("-" * 80)
    print(f"{'Pos':>3} | {'Private Key':>26} | {'Range Position':>15} | {'% into Range':>12} | {'Pattern':>20}")
    print("-" * 80)
    
    position_patterns = {}
    ratios = []
    
    for pos in sorted(ACTUAL_PUZZLE_DATA.keys()):
        data = ACTUAL_PUZZLE_DATA[pos]
        private_key = data['private_key']
        range_start = data['range_start']
        range_end = data['range_end']
        
        analysis = analyze_position_within_range(pos, private_key, range_start, range_end)
        
        # Try to identify the pattern
        percentage = analysis['percentage_into_range']
        offset = analysis['offset']
        
        # Check for common mathematical patterns
        pattern_type = "Unknown"
        if 45 <= percentage <= 55:
            pattern_type = "~Middle (50%)"
        elif 60 <= percentage <= 70:
            pattern_type = "~Golden Ratio?"
        elif 30 <= percentage <= 40:
            pattern_type = "~1/3 point"
        elif 20 <= percentage <= 30:
            pattern_type = "~1/4 point"
        elif percentage < 10:
            pattern_type = "Near start"
        elif percentage > 90:
            pattern_type = "Near end"
        
        position_patterns[pos] = {
            'percentage': percentage,
            'pattern': pattern_type,
            'offset': offset
        }
        
        ratios.append(percentage)
        
        print(f"{pos:>3} | {private_key:>26x} | {analysis['hex_offset']:>15} | {percentage:>10.2f}% | {pattern_type:>20}")
    
    print("-" * 80)
    print()
    
    # Statistical analysis of positions within ranges
    print("📈 STATISTICAL ANALYSIS OF RANGE POSITIONS:")
    print("=" * 60)
    avg_ratio = sum(ratios) / len(ratios)
    print(f"Average position within range: {avg_ratio:.2f}%")
    print(f"Min position: {min(ratios):.2f}%")
    print(f"Max position: {max(ratios):.2f}%")
    print(f"Standard deviation: {(sum([(r - avg_ratio)**2 for r in ratios]) / len(ratios))**0.5:.2f}%")
    
    # Look for mathematical constants
    print(f"\n🔢 CHECKING FOR MATHEMATICAL CONSTANTS:")
    golden_ratio = (1 + 5**0.5) / 2  # ≈ 1.618
    golden_percentage = (golden_ratio - 1) * 100  # ≈ 61.8%
    
    golden_matches = [pos for pos, data in position_patterns.items() 
                     if abs(data['percentage'] - golden_percentage) < 5]
    
    if golden_matches:
        print(f"Golden ratio matches (~61.8%): {golden_matches}")
    
    # Check for other mathematical relationships
    print(f"\n🔍 PATTERN RECOGNITION:")
    pattern_counts = {}
    for pos, data in position_patterns.items():
        pattern = data['pattern']
        if pattern not in pattern_counts:
            pattern_counts[pattern] = []
        pattern_counts[pattern].append(pos)
    
    for pattern, positions in pattern_counts.items():
        print(f"{pattern}: {positions}")
    
    # Verify addresses
    print(f"\n✅ ADDRESS VERIFICATION:")
    print("-" * 50)
    correct_addresses = 0
    total_addresses = 0
    
    for pos in sorted(ACTUAL_PUZZLE_DATA.keys()):
        data = ACTUAL_PUZZLE_DATA[pos]
        private_key = data['private_key']
        expected_address = data['address']
        
        try:
            # Generate address from private key
            pubkey = privkey_to_pubkey(private_key, compressed=True)
            generated_address = pubkey_to_address(pubkey)
            
            match = "✅" if generated_address == expected_address else "❌"
            if generated_address == expected_address:
                correct_addresses += 1
            total_addresses += 1
            
            print(f"Pos {pos:>3}: {match} {generated_address}")
            
        except Exception as e:
            print(f"Pos {pos:>3}: ❌ Error generating address: {e}")
            total_addresses += 1
    
    print(f"\nAddress verification: {correct_addresses}/{total_addresses} correct")
    
    # Look for sequence patterns
    print(f"\n🔄 SEQUENCE ANALYSIS:")
    print("-" * 40)
    
    # Check ratios between consecutive keys
    positions = sorted(ACTUAL_PUZZLE_DATA.keys())
    for i in range(len(positions) - 1):
        pos1, pos2 = positions[i], positions[i + 1]
        key1 = ACTUAL_PUZZLE_DATA[pos1]['private_key']
        key2 = ACTUAL_PUZZLE_DATA[pos2]['private_key']
        
        ratio = key2 / key1
        expected_ratio = 2 ** (pos2 - pos1)  # If perfect power of 2 growth
        
        print(f"  {pos1}→{pos2}: ratio={ratio:.3f}, expected={expected_ratio:.1f}, deviation={abs(ratio-expected_ratio)/expected_ratio*100:.1f}%")
    
    # Predict unsolved puzzles
    print(f"\n🎯 PREDICTIONS FOR UNSOLVED PUZZLES:")
    print("=" * 50)
    
    # Use the average position percentage to predict
    unsolved_positions = [69, 71, 72, 73, 74, 76, 77, 78, 79]
    
    for pos in unsolved_positions[:5]:  # First 5 unsolved
        # Calculate the range for this position
        range_start = 1 << (pos - 1)  # 2^(n-1)
        range_end = (1 << pos) - 1    # 2^n - 1
        range_size = range_end - range_start + 1
        
        # Use average percentage to predict position within range
        predicted_offset = int(range_size * avg_ratio / 100)
        predicted_key = range_start + predicted_offset
        
        print(f"\nPosition {pos}:")
        print(f"  Range: 0x{range_start:x} to 0x{range_end:x}")
        print(f"  Predicted key: 0x{predicted_key:x}")
        print(f"  Using {avg_ratio:.1f}% position within range")
        
        # Generate address for prediction
        try:
            pubkey = privkey_to_pubkey(predicted_key, compressed=True)
            predicted_address = pubkey_to_address(pubkey)
            print(f"  Predicted address: {predicted_address}")
        except:
            print(f"  Could not generate address")

if __name__ == "__main__":
    find_mathematical_relationships() 