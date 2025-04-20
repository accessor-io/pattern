import hashlib
from collections import defaultdict
import math

def analyze_crypto_patterns():
    # Read sequence
    with open('organized/data/32bHex.txt') as f:
        numbers = [int(line.strip(), 16) for line in f]
    
    print("Cryptographic Pattern Analysis")
    print("=" * 50)
    
    # 1. Avalanche effect analysis
    print("\n1. Avalanche Effect Analysis:")
    for i in range(1, min(10, len(numbers))):
        prev = bin(numbers[i-1])[2:].zfill(256)
        curr = bin(numbers[i])[2:].zfill(256)
        bit_changes = sum(p != c for p, c in zip(prev, curr))
        print(f"Position {i-1}->{i}: {bit_changes} bits changed ({bit_changes/len(prev)*100:.2f}%)")
    
    # 2. Entropy analysis
    print("\n2. Entropy Analysis:")
    def calculate_entropy(data):
        freq = defaultdict(int)
        for byte in data:
            freq[byte] += 1
        entropy = 0
        for count in freq.values():
            p = count / len(data)
            entropy -= p * math.log2(p)
        return entropy

    for i in range(min(10, len(numbers))):
        num_bytes = numbers[i].to_bytes((numbers[i].bit_length() + 7) // 8, byteorder='big')
        entropy = calculate_entropy(num_bytes)
        print(f"Position {i} entropy: {entropy:.4f} bits/byte")
    
    # 3. Hash chain analysis
    print("\n3. Hash Chain Analysis:")
    def hash_number(n):
        return int(hashlib.sha256(hex(n)[2:].encode()).hexdigest(), 16)
    
    for i in range(min(5, len(numbers)-1)):
        hashed = hash_number(numbers[i])
        next_actual = numbers[i+1]
        hash_similarity = bin(hashed ^ next_actual).count('1')  # XOR difference
        print(f"\nPosition {i}->({i+1}):")
        print(f"Current number: {hex(numbers[i])}")
        print(f"Hash: {hex(hashed)}")
        print(f"Next number: {hex(next_actual)}")
        print(f"Bit differences: {hash_similarity}")
    
    # 4. Linear complexity analysis
    print("\n4. Linear Complexity Analysis:")
    def get_lfsr_length(sequence, max_length=32):
        for length in range(1, max_length + 1):
            failed = False
            # Try to predict next value using last 'length' values
            for i in range(length, len(sequence)):
                predicted = sum(sequence[i-j] for j in range(1, length+1)) % 2
                if predicted != sequence[i]:
                    failed = True
                    break
            if not failed:
                return length
        return None

    # Convert first few numbers to bit sequences
    bit_sequences = []
    for i in range(min(5, len(numbers))):
        bits = [int(b) for b in bin(numbers[i])[2:]]
        complexity = get_lfsr_length(bits)
        print(f"Position {i} LFSR complexity: {complexity if complexity else 'Above 32'}")
    
    # 5. Modular pattern analysis
    print("\n5. Modular Pattern Analysis:")
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    for prime in primes[:5]:  # First few primes
        print(f"\nModulo {prime} sequence:")
        pattern = [numbers[i] % prime for i in range(min(10, len(numbers)))]
        print(f"Pattern: {pattern}")
        # Check for cycles
        for length in range(2, len(pattern)):
            if all(pattern[i] == pattern[i-length] for i in range(length, len(pattern))):
                print(f"Found cycle of length {length}")
                break

if __name__ == '__main__':
    analyze_crypto_patterns() 