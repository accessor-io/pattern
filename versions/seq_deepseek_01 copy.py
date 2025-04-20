def get_significant_bits(position):
    if position <= 7:
        return position + 1
    else:
        return min(64, 8 + int(position * 1.5))

def rotate_left(value, bits, rotation):
    return ((value << rotation) & ((1 << bits) - 1)) | (value >> (bits - rotation))

def apply_bit_permutation(position, value):
    if position < 8:
        return value
    else:
        preserved = value & ((1 << 8) - 1)
        higher_bits = value >> 8
        mixed = higher_bits ^ (position * 13)
        mixed = rotate_left(mixed, 56, position % 32)
        return (mixed << 8) | preserved

def apply_non_linear_transform(position, value):
    sig_bits = get_significant_bits(position)
    mask = (1 << sig_bits) - 1
    value = value ^ (value >> (position % 16))
    value = value & mask
    value = (value * (position + 1)) & mask
    return value

initial_values = [
    0x1, 0x3, 0x7, 0x8, 0x15, 0x31, 0x4c, 0xe0
]

sequence = initial_values.copy()

for position in range(8, 70):
    prev_value = sequence[position - 1]
    permuted = apply_bit_permutation(position, prev_value)
    transformed = apply_non_linear_transform(position, permuted)
    sequence.append(transformed)

# Convert to 64-character hexadecimal strings
hex_sequence = [format(value, '064x') for value in sequence]

# Print the first 70 positions
for idx, value in enumerate(hex_sequence[:70]):
    print(f"Index {idx}: {value}")