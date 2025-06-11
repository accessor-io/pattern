def get_significant_bits(position):
    if position <= 7:
        return position + 1
    else:
        return min(64, 8 + int(position * 1.5))

def generate_sequence(length=70):
    initial_values = [
        0x1, 0x3, 0x7, 0x8, 0x15, 0x31, 0x4c, 0xe0
    ]
    
    sequence = initial_values.copy()
    
    for position in range(8, length):
        prev_value = sequence[position - 1]
        sig_bits = get_significant_bits(position)
        mask = (1 << sig_bits) - 1
        
        if position % 5 != 0:
            # General transformation: left shift and XOR with position
            next_value = (prev_value << 1) ^ position
        else:
            # Special transformation at every 5th position: right shift and XOR with position-based mask
            shift_amount = position % 8  # Example shift based on position
            next_value = (prev_value >> shift_amount) ^ (position << 8)
        
        # Ensure the value fits within the significant bits
        next_value = next_value & mask
        sequence.append(next_value)
    
    # Convert to 64-character hexadecimal strings
    hex_sequence = [format(value, '064x') for value in sequence]
    
    return hex_sequence

# Generate and print the first 70 positions
sequence = generate_sequence(70)
for idx, value in enumerate(sequence[:70]):
    print(f"Index {idx}: {value}")