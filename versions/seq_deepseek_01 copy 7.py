def generate_sequence(length=70):
    sequence = []
    for position in range(length):
        n = position + 1  # Number of significant bits
        n = min(64, n)    # Cap n at 64
        # Binary representation of position+1, padded to n bits
        bin_str = bin(position + 1)[2:].zfill(n)
        # Reverse the significant bits
        reversed_bin_str = bin_str[::-1]
        # Convert reversed binary string to integer
        value = int(reversed_bin_str, 2)
        # Ensure the value fits within n bits
        value = value & ((1 << n) - 1)
        # Extend to 64 bits by shifting left
        value = value << (64 - n)
        # Convert to 64-character hexadecimal string
        hex_str = format(value, '064x')
        sequence.append(hex_str)
    return sequence

# Generate and print the first 70 positions
sequence = generate_sequence(70)
for idx, value in enumerate(sequence[:70]):
    print(f"Index {idx}: {value}")