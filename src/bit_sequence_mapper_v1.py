#!/usr/bin/python3

def read_hex_strings(filename):
    """Read and clean hex strings from file"""
    with open(filename, 'r') as file:
        # Remove whitespace and filter empty lines
        return [line.strip() for line in file if line.strip()]

def byte_to_bits(byte):
    """Convert a byte to its bit representation"""
    return [1 if byte & (1 << i) else 0 for i in range(7, -1, -1)]

def map_hex_to_bytes_and_bits(hex_string):
    """Map each hex string to its byte and bit representation"""
    # Pad the hex string to ensure it's 64 characters (32 bytes)
    hex_string = hex_string.zfill(64)
    
    # Convert hex string to bytes
    byte_array = bytes.fromhex(hex_string)
    
    # Create mapping of byte positions to their values and bits
    mapping = {}
    for i, byte in enumerate(byte_array):
        bits = byte_to_bits(byte)
        mapping[i] = {
            'byte': byte,
            'bits': bits,
            'bit_str': ''.join(map(str, bits))
        }
    
    return mapping

def process_file(filename):
    try:
        print(f"Reading from: {filename}")
        hex_strings = read_hex_strings(filename)
        print(f"Processing {len(hex_strings)} hex strings")
        
        output_filename = 'byte_and_bit_mappings.txt'
        with open(output_filename, 'w') as outfile:
            for i, hex_string in enumerate(hex_strings, 1):
                mapping = map_hex_to_bytes_and_bits(hex_string)
                
                # Write original hex and its mappings
                outfile.write(f"\nHex String {i}: {hex_string}\n")
                outfile.write("Byte and Bit Mapping:\n")
                for pos, data in mapping.items():
                    outfile.write(f"Byte {pos:2d}: 0x{data['byte']:02x} | Bits: {data['bit_str']} | Positions: ")
                    # Write bit positions that are set to 1
                    set_bits = [str(pos * 8 + (7-j)) for j, bit in enumerate(data['bits']) if bit == 1]
                    outfile.write(f"[{', '.join(set_bits)}]\n")
                outfile.write("-" * 70 + "\n")
        
        print(f"Byte and bit mappings saved to: {output_filename}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    process_file("32bHex.txt") 