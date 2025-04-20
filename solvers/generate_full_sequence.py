#!/usr/bin/env python3
import os

def generate_next_key(current_key, position):
    """Generate the next key based on position-dependent bit transformations"""
    # Get significant bits based on position
    if position <= 7:
        significant_bits = position + 1
    else:
        significant_bits = min(67, 8 + int(position * 1.5))
    
    # Create bit mask for significant bits
    mask = (1 << significant_bits) - 1
    
    # First 8 keys are generated with a specific algorithm
    if position < 8:
        # Use a deterministic algorithm for the first 8 keys
        seed = (position + 1) * 0x73a4b67c9
        result = (seed ^ (seed >> 13)) & mask
        return result
    
    # For positions >= 8, perform position-based bit operations
    # Use primes for mixing
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    prime_idx = position % len(primes)
    prime = primes[prime_idx]
    
    # Combine position-based transformations
    # Preserve some bits from current key, mix with position-dependent factor
    preserved_bits = current_key & ((1 << 8) - 1)  # Preserve first 8 bits
    new_bits = (current_key << prime_idx) ^ (position * prime)
    
    # Apply position-specific transformations
    if position % 3 == 0:
        new_bits = new_bits ^ (current_key >> 2)
    elif position % 3 == 1:
        new_bits = new_bits ^ (current_key << 3) 
    else:
        new_bits = new_bits ^ (current_key * prime) & mask
    
    # Combine preserved and new bits
    result = (preserved_bits | (new_bits & ~((1 << 8) - 1))) & mask
    
    # Ensure we meet minimum bit requirements
    min_bits = max(3, significant_bits // 2)
    if bin(result).count('1') < min_bits:
        result |= (1 << (significant_bits // 3))
    
    return result

def generate_full_sequence(max_key=160):
    """Generate the full sequence up to max_key"""
    sequence = {}
    
    # Generate first key
    sequence[1] = 0x1
    
    # Generate remaining keys
    for i in range(2, max_key + 1):
        sequence[i] = generate_next_key(sequence[i-1], i-1)
    
    return sequence

def save_sequence(sequence, filename="generated_sequence_full.txt"):
    """Save the sequence to a text file"""
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
    
    with open(filename, 'w') as f:
        for i in sorted(sequence.keys()):
            f.write(f"{format(sequence[i], '064x')}\n")
    
    print(f"Sequence saved to {filename}")

def analyze_sequence(sequence):
    """Analyze the generated sequence"""
    print("\nSequence Analysis:")
    print("------------------")
    
    # Show first 8 keys
    print("First 8 keys:")
    for i in range(1, 9):
        print(f"Key {i}: {hex(sequence[i])}")
    
    # Show last 3 keys
    print("\nLast 3 keys:")
    for i in range(max(sequence.keys()) - 2, max(sequence.keys()) + 1):
        print(f"Key {i}: {hex(sequence[i])}")
    
    # Show some XOR differences
    print("\nSample XOR differences:")
    for i in range(1, 6):
        diff = sequence[i+1] ^ sequence[i]
        print(f"D({i+1}) = Key({i+1}) XOR Key({i}) = {hex(diff)}")

if __name__ == "__main__":
    # Generate the sequence
    print("Generating sequence up to key 160...")
    sequence = generate_full_sequence(160)
    
    # Analyze the sequence
    analyze_sequence(sequence)
    
    # Save the sequence
    save_sequence(sequence, "generated_sequence_160.txt") 