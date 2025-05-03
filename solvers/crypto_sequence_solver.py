import hmac
import hashlib
import argparse

def hex_key_to_ascii(hex_key: str) -> str:
    """Convert hex key to ASCII using same logic as JavaScript version"""
    key_bytes = bytes.fromhex(hex_key.lstrip('0x'))
    result = []
    for byte in reversed(key_bytes):  # Process from MSB to LSB
        char = chr(byte) if 0x20 <= byte <= 0x7E else '.'
        result.append(char)
    return ''.join(result)

def generate_next_key(prev_key_hex: str, index: int) -> str:
    """Generate next key with index in MSB and zeroed LSB"""
    # Generate base HMAC
    salt = f"salt-{index}".encode()
    prev_key_bytes = bytes.fromhex(prev_key_hex.lstrip('0x').zfill(64))
    hmac_digest = hmac.new(salt, prev_key_bytes, hashlib.sha256).digest()
    
    # Convert index to 8-byte header
    index_header = index.to_bytes(8, 'big')
    
    # Create 32-byte key: [8-byte index][16-byte HMAC][8-byte zeros]
    masked_key = (
        index_header +
        hmac_digest[:16] +
        bytes(24)
    )
    
    return f"0x{masked_key.hex()}"

def validate_67():
    # Validate against known index 67 key
    key_66 = "2832ed74f2b5e35ee"  # Previous key
    result = generate_next_key(key_66, 66)
    assert result == "0x00000000000000000000000000000000000000000000000730fc235c1942c1ae"

def main():
    parser = argparse.ArgumentParser(description='Cryptographic Sequence Solver')
    parser.add_argument('--start-key', required=True, help='Initial hex key (e.g. 0x2832ed74f2b5e35ee)')
    parser.add_argument('--start-index', type=int, required=True, help='Starting index number')
    parser.add_argument('--count', type=int, default=5, help='Number of terms to generate')
    
    args = parser.parse_args()
    
    current_key = args.start_key
    for i in range(args.count):
        current_index = args.start_index + i
        current_key = generate_next_key(current_key, current_index)
        ascii_str = hex_key_to_ascii(current_key)
        
        print(f"Index: {current_index + 1}")
        print(f"Key:   {current_key}")
        print(f"ASCII: {ascii_str}")
        print("-" * 50)

if __name__ == "__main__":
    main() 