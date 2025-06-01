def get_set_positions(n):
    positions = []
    for i in range(256):
        if (n >> (255 - i)) & 1:
            positions.append(i)
    return positions

def format_hex(n):
    return f"{n:064x}"

def generate_sequence(max_length=67, max_hamming_weight=16):
    # Initialize with first value: bit 240 is set
    current = 1 << (255 - 240)
    sequence = [current]
    
    def has_consecutive_in_last_byte(n):
        last_byte_bits = [i for i in range(240, 256) if (n >> (255 - i)) & 1]
        for i in range(len(last_byte_bits) - 1):
            if last_byte_bits[i] - last_byte_bits[i+1] == 1:
                return True
        return False
    
    def clear_consecutive_and_set_next(n):
        last_byte_bits = [i for i in range(240, 256) if (n >> (255 - i)) & 1]
        if not last_byte_bits:
            return n
        # Find the lowest position in consecutive sequence
        sorted_bits = sorted(last_byte_bits)
        consecutive_found = False
        for i in range(1, len(sorted_bits)):
            if sorted_bits[i] - sorted_bits[i-1] == 1:
                consecutive_found = True
                break
        if not consecutive_found:
            return n
        # Clear consecutive bits
        for pos in sorted_bits:
            n &= ~(1 << (255 - pos))
        # Set next higher bit
        next_pos = sorted_bits[0] - 1
        if next_pos >= 240:
            n |= (1 << (255 - next_pos))
        else:
            # If cannot set higher, keep the lowest bit
            n |= (1 << (255 - sorted_bits[-1]))
        return n
    
    def set_neighbors(n):
        positions = get_set_positions(n)
        new_n = n
        for pos in positions:
            if pos > 0:
                new_n |= (1 << (255 - (pos - 1)))
            if pos < 255:
                new_n |= (1 << (255 - (pos + 1)))
        # Enforce maximum Hamming weight
        set_bits = get_set_positions(new_n)
        if len(set_bits) > max_hamming_weight:
            # Clear least significant bits until within limit
            set_bits_sorted = sorted(set_bits, key=lambda x: x, reverse=False)
            for bit in set_bits_sorted[max_hamming_weight:]:
                new_n &= ~(1 << (255 - bit))
        return new_n
    
    # Generate sequence
    while len(sequence) < max_length:
        current = sequence[-1]
        if has_consecutive_in_last_byte(current):
            current = clear_consecutive_and_set_next(current)
        else:
            current = set_neighbors(current)
        sequence.append(current)
    
    return sequence

# Generate and print sequence
sequence = generate_sequence()
for i, val in enumerate(sequence):
    hex_str = format_hex(val)
    positions = get_set_positions(val)
    print(f"Value {i+1}: {hex_str}")
    print(f"Positions: {positions}\n")