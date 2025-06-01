#!/usr/bin/env python3
"""
Analyze bit patterns in the Bitcoin puzzle sequence
"""

# Known private keys
KNOWN_KEYS = {
    64: 0x18e186a0b4c7594d,
    65: 0x13a52c20c7e93900,
    66: 0x1368d75b7a31a9b9,
    67: 0x1b728d02d6dfe00d,
    68: 0x1f685e68d87bb9fb,
    69: 0x101d83275fb2bc7e0c
}

def analyze_bit_patterns():
    """Analyze bit patterns in detail"""
    print("\nDetailed Bit Pattern Analysis")
    print("===========================")
    
    # Convert all keys to binary and analyze patterns
    binary_keys = {}
    for pos, key in sorted(KNOWN_KEYS.items()):
        binary = bin(key)[2:].zfill(64)  # 64-bit representation
        binary_keys[pos] = binary
        print(f"\nPosition {pos}:")
        print(f"Key: 0x{key:x}")
        print(f"Binary: {binary}")
        print(f"Length: {len(binary)} bits")
        print(f"1's count: {binary.count('1')}")
        print(f"Leading zeros: {len(binary) - len(binary.lstrip('0'))}")
        
        # Analyze byte patterns
        bytes_list = [binary[i:i+8] for i in range(0, len(binary), 8)]
        print("Byte patterns:")
        for i, byte in enumerate(bytes_list):
            print(f"  Byte {i}: {byte} (0x{int(byte,2):02x})")
    
    # Analyze transitions
    print("\nTransition Analysis:")
    for i in range(len(binary_keys)-1):
        pos1 = sorted(binary_keys.keys())[i]
        pos2 = sorted(binary_keys.keys())[i+1]
        bin1 = binary_keys[pos1]
        bin2 = binary_keys[pos2]
        
        print(f"\nTransition {pos1} → {pos2}:")
        
        # XOR pattern
        xor = int(bin1, 2) ^ int(bin2, 2)
        xor_bin = bin(xor)[2:].zfill(64)
        print(f"XOR pattern: {xor_bin}")
        print(f"XOR 1's count: {xor_bin.count('1')}")
        
        # Analyze bit flips
        flips = []
        for j, (b1, b2) in enumerate(zip(bin1, bin2)):
            if b1 != b2:
                flips.append(j)
        print(f"Bit flip positions: {flips}")
        
        # Look for repeating patterns
        if len(flips) > 1:
            diffs = [flips[j+1] - flips[j] for j in range(len(flips)-1)]
            print(f"Distances between flips: {diffs}")
            
            # Check for arithmetic sequences
            is_arithmetic = all(d == diffs[0] for d in diffs)
            if is_arithmetic:
                print(f"Found arithmetic sequence with difference {diffs[0]}")
        
        # Analyze byte-level changes
        bytes1 = [bin1[i:i+8] for i in range(0, len(bin1), 8)]
        bytes2 = [bin2[i:i+8] for i in range(0, len(bin2), 8)]
        print("\nByte-level changes:")
        for j, (b1, b2) in enumerate(zip(bytes1, bytes2)):
            if b1 != b2:
                print(f"  Byte {j}: {b1} → {b2}")
    
    # Try to predict patterns for position 71
    if 69 in KNOWN_KEYS:
        print("\nPredicting patterns for position 71:")
        last_key = binary_keys[69]
        
        # Method 1: Continue the last XOR pattern
        last_xor = int(binary_keys[68], 2) ^ int(binary_keys[69], 2)
        pred1 = int(binary_keys[69], 2) ^ last_xor
        print(f"\nMethod 1 (Continue XOR):")
        print(f"Predicted key: 0x{pred1:x}")
        
        # Method 2: Apply the most common bit flip pattern
        most_common_flips = []
        for i in range(64):
            flip_count = sum(1 for pos in range(len(binary_keys)-1)
                           if binary_keys[sorted(binary_keys.keys())[pos]][i] != 
                              binary_keys[sorted(binary_keys.keys())[pos+1]][i])
            if flip_count > len(binary_keys) // 2:
                most_common_flips.append(i)
        
        pred2 = int(last_key, 2)
        for pos in most_common_flips:
            pred2 ^= (1 << (63 - pos))
        print(f"\nMethod 2 (Common Flips):")
        print(f"Predicted key: 0x{pred2:x}")
        
        # Method 3: Byte pattern continuation
        last_bytes = [last_key[i:i+8] for i in range(0, len(last_key), 8)]
        new_bytes = []
        for i, byte in enumerate(last_bytes):
            # Simple transformation: rotate each byte left by position
            rotated = byte[i % 8:] + byte[:i % 8]
            new_bytes.append(rotated)
        pred3 = int(''.join(new_bytes), 2)
        print(f"\nMethod 3 (Byte Rotation):")
        print(f"Predicted key: 0x{pred3:x}")

def main():
    print("Bitcoin Puzzle Sequence Bit Pattern Analysis")
    print("==========================================")
    analyze_bit_patterns()

if __name__ == "__main__":
    main() 