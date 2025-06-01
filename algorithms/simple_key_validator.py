#!/usr/bin/env python3
"""
SIMPLE BITCOIN KEY VALIDATOR
============================

Simple validation of Bitcoin puzzle private keys without external dependencies.
Uses basic elliptic curve math to generate addresses.
"""

import hashlib

# secp256k1 parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8

# Real position 69 value provided by user
REAL_POSITION_69 = 0x101d83275fb2bc7e0c
EXPECTED_ADDRESS_69 = "19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG"

def base58_encode(data):
    """Manual Base58 encoding implementation."""
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    
    # Convert bytes to integer
    num = int.from_bytes(data, 'big')
    
    # Encode in base58
    encoded = ""
    while num > 0:
        num, remainder = divmod(num, 58)
        encoded = alphabet[remainder] + encoded
    
    # Handle leading zeros
    for byte in data:
        if byte == 0:
            encoded = "1" + encoded
        else:
            break
    
    return encoded

def mod_inverse(a, m):
    """Calculate modular inverse using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    
    # Extended Euclidean Algorithm
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
            # Point doubling
            s = (3 * x1 * x1 * mod_inverse(2 * y1, P)) % P
        else:
            return None  # Point at infinity
    else:
        # Point addition
        s = ((y2 - y1) * mod_inverse(x2 - x1, P)) % P
    
    x3 = (s * s - x1 - x2) % P
    y3 = (s * (x1 - x3) - y1) % P
    
    return (x3, y3)

def point_multiply(k, point):
    """Multiply point by scalar k using double-and-add."""
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

def private_key_to_public_key(private_key):
    """Convert private key to public key point."""
    return point_multiply(private_key, (Gx, Gy))

def public_key_to_address(public_key, compressed=True):
    """Convert public key point to Bitcoin address."""
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
    
    # Calculate checksum properly - ensure we're working with bytes
    checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
    address_bytes = versioned_payload + checksum
    
    return base58_encode(address_bytes)

def validate_position_69():
    """Validate the real position 69 private key."""
    print("🔍 VALIDATING REAL POSITION 69 PRIVATE KEY")
    print("="*60)
    
    private_key = REAL_POSITION_69
    print(f"Private Key: 0x{private_key:x}")
    print(f"Decimal: {private_key}")
    print(f"Bit length: {private_key.bit_length()}")
    
    # Check range
    min_expected = 1 << 68
    max_expected = (1 << 69) - 1
    in_range = min_expected <= private_key <= max_expected
    print(f"In expected range: {in_range}")
    
    try:
        # Generate public key
        print("\n🔑 Generating public key...")
        public_key = private_key_to_public_key(private_key)
        
        if public_key:
            x, y = public_key
            print(f"Public Key X: 0x{x:x}")
            print(f"Public Key Y: 0x{y:x}")
            
            # Generate addresses
            print("\n🏠 Generating Bitcoin addresses...")
            compressed_addr = public_key_to_address(public_key, compressed=True)
            uncompressed_addr = public_key_to_address(public_key, compressed=False)
            
            print(f"Compressed address:   {compressed_addr}")
            print(f"Uncompressed address: {uncompressed_addr}")
            print(f"Expected address:     {EXPECTED_ADDRESS_69}")
            
            # Check for matches
            if compressed_addr == EXPECTED_ADDRESS_69:
                print(f"\n✅ PERFECT MATCH (Compressed)!")
                print(f"🎉 Position 69 private key is CONFIRMED CORRECT!")
                return True
            elif uncompressed_addr == EXPECTED_ADDRESS_69:
                print(f"\n✅ PERFECT MATCH (Uncompressed)!")
                print(f"🎉 Position 69 private key is CONFIRMED CORRECT!")
                return True
            else:
                print(f"\n❌ No exact match found")
                
                # Check similarity
                if compressed_addr:
                    diff_compressed = sum(1 for a, b in zip(compressed_addr, EXPECTED_ADDRESS_69) if a != b)
                    print(f"Compressed difference: {diff_compressed} characters")
                
                if uncompressed_addr:
                    diff_uncompressed = sum(1 for a, b in zip(uncompressed_addr, EXPECTED_ADDRESS_69) if a != b)
                    print(f"Uncompressed difference: {diff_uncompressed} characters")
                
                return False
        else:
            print("❌ Failed to generate public key")
            return False
            
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main validation function."""
    print("🚨 SIMPLE BITCOIN PUZZLE KEY VALIDATION")
    print("="*60)
    print("Testing the REAL position 69 value provided by user...\n")
    
    success = validate_position_69()
    
    if success:
        print(f"\n🎯 VALIDATION SUCCESS!")
        print(f"The position 69 private key is mathematically correct!")
        print(f"This proves the validation methodology works!")
    else:
        print(f"\n⚠️  VALIDATION INCONCLUSIVE")
        print(f"Either the key is incorrect or there's an implementation issue")
    
    return success

if __name__ == "__main__":
    main() 