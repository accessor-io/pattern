def generate_sequence(length=70):
    initial_values = [0x1, 0x3, 0x7, 0x8, 0x15, 0x31, 0x4c, 0xe0]
    sequence = initial_values.copy()
    
    for position in range(8, length):
        prev_value = sequence[position - 1]
        n = position + 1  # Number of significant bits for the next position
        
        if (position + 1) % 5 == 0:
            # Special transformation: reverse the bits of the previous value
            bits = bin(prev_value)[2:].zfill(n)
            reversed_bits = bits[::-1]
            next_value = int(reversed_bits, 2)
        else:
            # Standard transformation: increment the previous value
            next_value = prev_value + 1
        
        # Ensure only n bits are significant
        next_value = next_value & ((1 << n) - 1)
        sequence.append(next_value)
    
    return sequence

# Generate the sequence up to the 70th position
sequence = generate_sequence(70)

# Convert to hexadecimal strings with leading zeros to match 64 characters
hex_sequence = [format(value, '064x') for value in sequence]

# Print the first 70 positions
for idx, value in enumerate(hex_sequence[:70]):
    print(f"Index {idx}: {value}")