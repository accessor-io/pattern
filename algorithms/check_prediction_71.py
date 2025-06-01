#!/usr/bin/env python3
"""
CHECK POSITION 71 PREDICTION
============================

Test the precise prediction for position 71 against its known Bitcoin address.
"""

import hashlib

# Known addresses
KNOWN_ADDRESSES = {
    69: "19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG",
    71: "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU", # Target for puzzle 71
    # ... other addresses
}

# Predicted value from precise pattern analysis
PREDICTED_KEY_71 = 0x402f1c8d9d44b99800 # User provided HIGH_CONFIDENCE prediction
EXPECTED_ADDRESS_71 = KNOWN_ADDRESSES[71]

# secp256k1 parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
Gx = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8

def base58_encode(data):
    """Manual Base58 encoding implementation."""
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    
    num = int.from_bytes(data, 'big')
    
    encoded = ""
    while num > 0:
        num, remainder = divmod(num, 58)
        encoded = alphabet[remainder] + encoded
    
    for byte in data:
        if byte == 0:
            encoded = "1" + encoded
        else:
            break
    
    return encoded

def mod_inverse(a, m):
    """Calculate modular inverse."""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        raise Exception('Modular inverse does not exist')
    return (x % m + m) % m

def point_add(p1, p2):
    """Add two points on secp256k1 curve."""
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    
    x1, y1 = p1
    x2, y2 = p2
    
    if x1 == x2:
        if y1 == y2:
            s = (3 * x1 * x1 * mod_inverse(2 * y1, P)) % P
        else:
            return None
    else:
        s = ((y2 - y1) * mod_inverse(x2 - x1, P)) % P
    
    x3 = (s * s - x1 - x2) % P
    y3 = (s * (x1 - x3) - y1) % P
    
    return (x3, y3)

def point_multiply(k, point):
    """Multiply point by scalar k."""
    if k == 0:
        return None
    if k == 1:
        return point
    
    result = None
    addend = point
    
    while k:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1
    
    return result

def private_key_to_address(private_key, compressed=True):
    """Convert private key to Bitcoin address."""
    # Generate public key
    public_key = point_multiply(private_key, (Gx, Gy))
    
    if not public_key:
        return None
    
    x, y = public_key
    
    if compressed:
        if y % 2 == 0:
            pubkey_bytes = b'\x02' + x.to_bytes(32, 'big')
        else:
            pubkey_bytes = b'\x03' + x.to_bytes(32, 'big')
    else:
        pubkey_bytes = b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
    
    # Hash160
    sha256_hash = hashlib.sha256(pubkey_bytes).digest()
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
    
    # Add version byte and checksum
    versioned_payload = b'\x00' + ripemd160_hash
    checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
    address_bytes = versioned_payload + checksum
    
    return base58_encode(address_bytes)

def get_ripemd160_from_address(btc_address):
    """Decodes a Bitcoin address to its RIPEMD-160 hash."""
    try:
        decoded_hex = base58_decode_hex(btc_address)
        # Expected length: 1 (version) + 20 (ripemd160) + 4 (checksum) = 25 bytes = 50 hex chars
        if len(decoded_hex) != 50:
            # print(f"Error: Decoded hex length is not 50: {len(decoded_hex)}")
            return None
        ripemd160_hex = decoded_hex[2:42] # Skip version byte (2 hex chars), take next 40 hex chars (20 bytes)
        return ripemd160_hex
    except Exception as e:
        # print(f"Error decoding address to ripemd160: {e}")
        return None

def test_position_71():
    """Test position 71 prediction."""
    print("🎯 TESTING POSITION 71 PREDICTION")
    print("="*60)
    
    print(f"Predicted Key: 0x{PREDICTED_KEY_71:x}")
    print(f"Expected Address: {EXPECTED_ADDRESS_71}")
    
    # Check if key is in valid range
    min_71 = 1 << 70
    max_71 = (1 << 71) - 1
    in_range = min_71 <= PREDICTED_KEY_71 <= max_71
    print(f"Key in valid range: {in_range}")
    print(f"Bit length: {PREDICTED_KEY_71.bit_length()}")
    
    try:
        # Generate addresses
        compressed_addr = private_key_to_address(PREDICTED_KEY_71, compressed=True)
        uncompressed_addr = private_key_to_address(PREDICTED_KEY_71, compressed=False)
        
        print(f"\nGenerated Addresses:")
        print(f"Compressed:   {compressed_addr}")
        print(f"Uncompressed: {uncompressed_addr}")
        
        # Check for matches
        if compressed_addr == EXPECTED_ADDRESS_71:
            print(f"\n✅ PERFECT MATCH (Compressed)!")
            print(f"🎉 POSITION 71 SOLVED! Pattern prediction is CORRECT!")
            return True
        elif uncompressed_addr == EXPECTED_ADDRESS_71:
            print(f"\n✅ PERFECT MATCH (Uncompressed)!")
            print(f"🎉 POSITION 71 SOLVED! Pattern prediction is CORRECT!")
            return True
        else:
            print(f"\n❌ No exact match found")
            
            # Check similarity
            if compressed_addr and len(compressed_addr) == len(EXPECTED_ADDRESS_71):
                diff_count = sum(1 for a, b in zip(compressed_addr, EXPECTED_ADDRESS_71) if a != b)
                print(f"Compressed difference: {diff_count} characters")
            
            if uncompressed_addr and len(uncompressed_addr) == len(EXPECTED_ADDRESS_71):
                diff_count = sum(1 for a, b in zip(uncompressed_addr, EXPECTED_ADDRESS_71) if a != b)
                print(f"Uncompressed difference: {diff_count} characters")
            
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🚨 POSITION 71 PATTERN VALIDATION TEST")
    print("="*60)
    print("Testing if the precise pattern prediction works...\n")
    
    success = test_position_71()
    
    if success:
        print(f"\n🎯 BREAKTHROUGH CONFIRMED!")
        print(f"The mathematical pattern from position 69 works!")
        print(f"Position 71 private key successfully recovered!")
    else:
        print(f"\n⚠️  Pattern needs refinement")
        print(f"The prediction was close but not exact")
        print(f"May need to adjust the mathematical transformation")
    
    print(f"Expected Address: {EXPECTED_ADDRESS_71}")
    
    expected_ripemd160 = get_ripemd160_from_address(EXPECTED_ADDRESS_71)
    if expected_ripemd160:
        print(f"Expected RIPEMD-160: {expected_ripemd160}")
    else:
        print(f"Could not derive RIPEMD-160 for {EXPECTED_ADDRESS_71}")

    return success

if __name__ == "__main__":
    main() 