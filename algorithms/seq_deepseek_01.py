def get_significant_bits(position):
    if position <= 7:
        return position + 1
    else:
        return min(64, 8 + int(position * 1.5))

def apply_bit_permutation(position, value):
    if position < 8:
        return value
    else:
        preserved = value & 0xFF  # Preserve the first 8 bits
        mixed = (value >> 8) ^ (position * 11)  # Mix higher bits with a prime-based function
        return (mixed << 8) | preserved

def apply_non_linear_transform(position, value):
    shifted = (value << 3) & 0xFFFFFFFFFFFFFFFF  # 64-bit mask
    xor_result = shifted ^ value
    final = (xor_result + position) & ((1 << get_significant_bits(position)) - 1)
    return final

initial_values = [
    0x1, 0x3, 0x7, 0x8, 0x15, 0x31, 0x4c, 0xe0
]

sequence = initial_values.copy()

for position in range(8, 70):
    prev_value = sequence[position - 1]
    permuted = apply_bit_permutation(position, prev_value)
    transformed = apply_non_linear_transform(position, permuted)
    significant_bits = get_significant_bits(position)
    next_value = transformed & ((1 << significant_bits) - 1)
    sequence.append(next_value)

# Convert to 64-character hexadecimal strings
hex_sequence = [format(value, '064x') for value in sequence]

# Print the first 70 positions
for idx, value in enumerate(hex_sequence[:70]):
    print(f"Index {idx}: {value}")