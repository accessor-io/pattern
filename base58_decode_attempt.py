import hashlib


def base58_decode_int(s):
    BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    n = 0
    for char in s:
        n = n * 58 + BASE58_ALPHABET.index(char)
    return n

def analyze_modified_string():
    # Original string with 'l'
    original = "KwgpK6VwravTrH6yCAuaRRLhs4P36CdlAttvryUZVMJZuGqjdFZSt3roegDP7mRct25cKypgSA"
    
    # Modified string with '1'
    modified = "KwgpK6VwravTrH6yCAuaRRLhs4P36Cd1AttvryUZVMJZuGqjdFZSt3roegDP7mRct25cKypgSA"
    
    print("String Analysis:")
    print(f"Original: {original}")
    print(f"Modified: {modified}")
    print(f"Length: {len(modified)}")
    
    # Position of the change
    change_pos = original.index('l')
    print(f"\nChange position: {change_pos}")
    print(f"Context: {original[change_pos-5:change_pos+6]}")
    
    try:
        # Try Base58 decoding
        decoded_int = base58_decode_int(modified)
        print(f"\nDecoded as integer: {decoded_int}")
        
        # Convert to bytes
        byte_length = (decoded_int.bit_length() + 7) // 8
        decoded_bytes = decoded_int.to_bytes(byte_length, 'big')
        print(f"Decoded bytes (hex): {decoded_bytes.hex()}")
        
        # Check if result could be a Bitcoin private key (32 bytes)
        if len(decoded_bytes) == 32:
            print("Could be a private key!")
        
        # Check if result could be a public key (33 or 65 bytes)
        if len(decoded_bytes) in [33, 65]:
            print("Could be a public key!")
            
        # Look for patterns in the bytes
        print("\nByte patterns:")
        for i in range(0, len(decoded_bytes), 4):
            chunk = decoded_bytes[i:i+4]
            print(f"Bytes {i:2d}-{i+3:2d}: {chunk.hex()} ({int.from_bytes(chunk, 'big')})")
            
    except Exception as e:
        print(f"Error decoding: {str(e)}")

analyze_modified_string() 