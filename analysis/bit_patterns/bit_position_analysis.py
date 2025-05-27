def count_bits(hex_str):
    # Remove leading zeros and '0x'
    hex_str = hex_str.strip()
    # Convert to binary and count 1's
    return bin(int(hex_str, 16)).count('1')

with open('data/32bHex.txt', 'r') as f:
    lines = f.readlines()
    
for idx, line in enumerate(lines):
    bits = count_bits(line)
    if bits == idx:
        print(f"Match at position {idx}: {line.strip()} has {bits} bits") 