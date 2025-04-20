def count_significant_bits(hex_str):
    # Convert to binary and strip leading/trailing zeros
    bin_str = bin(int(hex_str, 16))[2:].rstrip('0')
    return len(bin_str)

with open('data/32bHex.txt', 'r') as f:
    for i, line in enumerate(f):
        hex_val = line.strip()
        bits = count_significant_bits(hex_val)
        if 66 <= bits <= 68:  # Look around 67
            print(f"\nPosition {i}:")
            print(f"Hex: {hex_val}")
            print(f"Significant bits: {bits}")
            print(f"Decimal: {int(hex_val, 16)}") 