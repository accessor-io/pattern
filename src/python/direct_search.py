import sys
from puzzle_solver_160 import privkey_to_address, validate_private_key, geometric_segment

TARGET_ADDR = " 1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"

# Add missing definitions for a65 and a70 from puzzle context
a65 = 0x1A838B13505B26867  # Index 65 value
a70 = 0x349B84B6431A6C4EF1  # Index 70 value

def test_geometric_progression():
    """Test geometric progression hypothesis with 1-byte transformations"""
    print("Testing geometric progression candidates...")
    keys = geometric_segment(a65, a70, 65, 70)
    
    for idx, key in keys.items():
        # Test original key
        addr = privkey_to_address(key)
        if addr == TARGET_ADDR:
            print(f"Direct match found at index {idx}: {hex(key)}")
            return
        
        # Test 1-byte XOR variations
        for byte in range(0x100):
            modified_key = key ^ (byte << 248)  # XOR first byte
            if validate_private_key(modified_key):
                modified_addr = privkey_to_address(modified_key)
                if modified_addr == TARGET_ADDR:
                    print(f"Match found via XOR 0x{byte:02x} at index {idx}:")
                    print(f"Original: {hex(key)}")
                    print(f"Modified: {hex(modified_key)}")
                    return

    print("No geometric progression solution found with 1-byte transformations")

def direct_brute_force(start, end):
    for candidate in range(start, end+1):
        if not validate_private_key(candidate):
            continue
        addr = privkey_to_address(candidate)
        if addr == TARGET_ADDR:
            return candidate
    return None

if __name__ == "__main__":
    test_geometric_progression()
    print("Fallback to brute force search...")
    
    # Brute-force near the suspected key
    result = direct_brute_force(0x69374BC6A7EF2E4B8 - 0x1000, 0x69374BC6A7EF2E4B8 + 0x1000)
    if result:
        print(f"Found nearby key: {hex(result)} -> {TARGET_ADDR}")
    else:
        print("Exhausted search without success") 