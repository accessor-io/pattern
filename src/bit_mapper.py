#!/usr/bin/python3

def read_hex_strings(filename):
    """Read and clean hex strings from file"""
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def validate_hex_string(hex_string):
    """Validate hex string is exactly 64 characters (32 bytes)"""
    if len(hex_string) > 64:
        raise ValueError(f"Hex string too long: {len(hex_string)} chars. Must be 64 chars.")
    return hex_string.zfill(64)  # Pad shorter strings to 64 chars

def hex_to_bits(hex_string):
    """Convert hex string to binary and return list of bit positions that are 1"""
    # Validate and pad to exactly 32 bytes (64 hex chars)
    hex_string = validate_hex_string(hex_string)
    
    # Convert to binary
    num = int(hex_string, 16)
    binary = format(num, '0256b')  # Ensure exactly 256 bits
    
    # Get positions of set bits (1's), counting from right to left
    set_bits = []
    for i, bit in enumerate(reversed(binary)):
        if bit == '1':
            set_bits.append(i)
    
    return {
        'binary': binary,
        'set_bits': set_bits,
        'total_bits': len(set_bits),
        'hex': hex_string
    }

def format_bit_chunks(binary, chunk_size, bits_per_line):
    """Format binary string into chunks of specified size"""
    chunks = []
    for i in range(0, 256, chunk_size):
        chunk = binary[i:i+chunk_size]
        chunk_num = i // chunk_size
        chunks.append(f"[{chunk_num:2d}] {i:3d}-{i+chunk_size-1:<3d}: {chunk}")
        if (i + chunk_size) % bits_per_line == 0:
            chunks.append("")  # Add blank line after each complete line group
    return chunks

def process_file(filename):
    try:
        print(f"Reading from: {filename}")
        hex_strings = read_hex_strings(filename)
        print(f"Processing {len(hex_strings)} hex strings")
        
        output_filename = 'bit_patterns.txt'
        with open(output_filename, 'w') as outfile:
            outfile.write("32-Byte (256-bit) Pattern Analysis\n")
            outfile.write("=" * 70 + "\n\n")
            
            for i, hex_string in enumerate(hex_strings, 1):
                try:
                    bit_data = hex_to_bits(hex_string)
                    binary = bit_data['binary']
                    
                    # Write detailed bit analysis
                    outfile.write(f"String {i}:\n")
                    outfile.write(f"Hex:   {bit_data['hex']}\n")
                    outfile.write(f"Bits:  {bit_data['total_bits']} bits set\n")
                    outfile.write(f"Index: {sorted(bit_data['set_bits'])}\n\n")
                    
                    # 8-bit chunks (bytes)
                    outfile.write("Byte view (8-bit chunks):\n")
                    byte_chunks = format_bit_chunks(binary, 8, 64)
                    outfile.write("\n".join(byte_chunks) + "\n\n")
                    
                    # 16-bit chunks
                    outfile.write("Word view (16-bit chunks):\n")
                    word_chunks = format_bit_chunks(binary, 16, 64)
                    outfile.write("\n".join(word_chunks) + "\n\n")
                    
                    # 32-bit chunks
                    outfile.write("Double word view (32-bit chunks):\n")
                    dword_chunks = format_bit_chunks(binary, 32, 128)
                    outfile.write("\n".join(dword_chunks) + "\n\n")
                    
                    # 64-bit chunks
                    outfile.write("Quad word view (64-bit chunks):\n")
                    qword_chunks = format_bit_chunks(binary, 64, 128)
                    outfile.write("\n".join(qword_chunks) + "\n\n")
                    
                    outfile.write("-" * 70 + "\n\n")
                
                except ValueError as ve:
                    outfile.write(f"Error in string {i}: {str(ve)}\n\n")
        
        print(f"Bit patterns saved to: {output_filename}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    process_file("32bHex.txt") 