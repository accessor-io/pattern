lol duhdef get_significant_bits_length(hex_str):
    # Convert hex to binary, strip leading zeros and '0b'
    binary = bin(int(hex_str, 16))[2:].rstrip('0')
    return len(binary)

def analyze_sequence():
    with open('data/32bHex.txt', 'r') as f:
        sequence = [line.strip() for line in f]
    
    print("Sequence Analysis:")
    for idx, hex_val in enumerate(sequence):
        sig_bits = get_significant_bits_length(hex_val)
        if sig_bits >= 65 and sig_bits <= 69:  # Look around 67
            print(f"Position {idx}: {hex_val}")
            print(f"Significant bits: {sig_bits}")
            print(f"Value: {int(hex_val, 16)}")
            print()

if __name__ == "__main__":
    analyze_sequence() 