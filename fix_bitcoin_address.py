#!/usr/bin/env python3

import hashlib
import base58
import binascii
import itertools
import string

# The Bitcoin address we discovered (with invalid checksum)
invalid_address = "1CZqucvN1wZ4Gwq95dsNgj1xVjUcG9rEiQ"

def verify_address(address):
    """Verify if a Bitcoin address has valid checksum"""
    try:
        decoded = base58.b58decode(address)
        if len(decoded) != 25:
            return False
        
        # Get components
        version = decoded[0]
        hash160 = decoded[1:21]
        checksum = decoded[21:25]
        
        # Calculate checksum
        calculated_checksum = hashlib.sha256(hashlib.sha256(decoded[0:21]).digest()).digest()[:4]
        return calculated_checksum == checksum
    except:
        return False

def calculate_correct_address(decoded_bytes):
    """Calculate a correct Bitcoin address from the decoded bytes (fixing checksum)"""
    version_and_hash = decoded_bytes[:21]  # First 21 bytes (version + hash160)
    correct_checksum = hashlib.sha256(hashlib.sha256(version_and_hash).digest()).digest()[:4]
    correct_bytes = version_and_hash + correct_checksum
    correct_address = base58.b58encode(correct_bytes).decode('utf-8')
    return correct_address

def generate_similar_addresses(invalid_address):
    """Generate addresses by changing one character at a time"""
    valid_found = []
    
    # First, check if fixing the checksum creates a valid address
    try:
        decoded = base58.b58decode(invalid_address)
        version_and_hash = decoded[:21]  # First 21 bytes
        fixed_address = calculate_correct_address(version_and_hash)
        
        print(f"Original invalid address: {invalid_address}")
        print(f"Address with corrected checksum: {fixed_address}")
        print(f"Is valid: {verify_address(fixed_address)}")
        valid_found.append(("corrected_checksum", fixed_address))
    except Exception as e:
        print(f"Error fixing checksum: {e}")
    
    # Try changing each character one at a time
    print("\nTrying single character substitutions...")
    
    base58_chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    
    for i in range(len(invalid_address)):
        original_char = invalid_address[i]
        for new_char in base58_chars:
            if new_char == original_char:
                continue
                
            modified = invalid_address[:i] + new_char + invalid_address[i+1:]
            if verify_address(modified):
                print(f"Found valid address by changing position {i} from '{original_char}' to '{new_char}':")
                print(f"  {modified}")
                valid_found.append((f"change_pos_{i}_{original_char}_to_{new_char}", modified))
    
    return valid_found

# Main execution
print(f"Analyzing invalid Bitcoin address: {invalid_address}")
print(f"Is valid: {verify_address(invalid_address)}")

valid_addresses = generate_similar_addresses(invalid_address)

# If we found valid addresses, try to decode their meaning
if valid_addresses:
    print("\n=== Found valid addresses ===")
    for method, address in valid_addresses:
        print(f"Method: {method}")
        print(f"Address: {address}")
        
        # Decode and check properties
        decoded = base58.b58decode(address)
        version = decoded[0]
        hash160 = decoded[1:21]
        
        print(f"Version: {version} (0x{version:02x})")
        print(f"Hash160: {hash160.hex()}")
        
        # Check if hash160 has meaning as ASCII
        hash160_ascii = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in hash160)
        print(f"Hash160 as ASCII: {hash160_ascii}")
        print()
else:
    print("No valid addresses found with single character changes.")
    
print("\nNext steps could include:")
print("1. Try multiple character changes")
print("2. Look for different patterns in the original key sequence")
print("3. Consider that the invalid address itself might be the intended message") 