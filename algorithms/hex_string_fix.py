#!/usr/bin/env python3

import binascii
import hashlib
import base64

def test_all_positions(hex_string):
    """Test inserting each hex character at each position in the hex string."""
    print(f"Original string: {hex_string}")
    print(f"Length: {len(hex_string)} characters")
    
    # Double-check for any non-hex characters that might be causing issues
    non_hex = [c for c in hex_string if c not in '0123456789abcdefABCDEF']
    if non_hex:
        print(f"Warning: Found non-hex characters: {non_hex}")
        # Remove non-hex characters
        hex_string = ''.join(c for c in hex_string if c in '0123456789abcdefABCDEF')
        print(f"Cleaned string: {hex_string}")
        print(f"New length: {len(hex_string)} characters")
    
    # Check if it's already valid by trying to convert to bytes
    try:
        data = bytes.fromhex(hex_string)
        print(f"Successfully converted to {len(data)} bytes.")
        print(f"This is a valid hex string of even length.")
    except ValueError as e:
        print(f"Error converting to bytes: {e}")
    
    # Force the 128-character conversion even if the string is already valid
    print("\nForcing conversion to 128 characters (64 bytes)...")
    
    # If we need to add 2 characters to reach 128
    if len(hex_string) == 126:
        print("Adding 2 characters to reach 128 characters (64 bytes)...")
    # If we need to add 1 character to reach 127, then 1 more to reach 128
    elif len(hex_string) == 127:
        print("Adding 1 character to reach 128 characters (64 bytes)...")
    # If we're at some other length, adjust accordingly
    else:
        chars_needed = 128 - len(hex_string)
        print(f"Need to add {chars_needed} characters to reach 128 characters (64 bytes)...")
    
    valid_insertions = []
    hex_digits = "0123456789abcdef"
    
    # Try inserting at each position
    for pos in range(len(hex_string) + 1):
        for digit in hex_digits:
            test_string = hex_string[:pos] + digit + hex_string[pos:]
            
            # Ensure the test string is 128 characters (adding a character to a 126-char string)
            if len(test_string) == 127:
                # Try each possible ending character too
                for end_digit in hex_digits:
                    final_test = test_string + end_digit
                    try:
                        # Check if valid hex
                        bytes.fromhex(final_test)
                        valid_insertions.append((pos, digit, end_digit, final_test))
                    except ValueError:
                        continue
            elif len(test_string) == 128:
                try:
                    # Check if valid hex
                    bytes.fromhex(test_string)
                    valid_insertions.append((pos, digit, "", test_string))
                except ValueError:
                    continue
    
    if valid_insertions:
        print(f"Found {len(valid_insertions)} valid ways to convert the string to 128 characters.")
        
        for idx, (pos, digit, end_digit, fixed_string) in enumerate(valid_insertions[:10]):  # Show first 10
            if end_digit:
                print(f"Option {idx+1}: Insert '{digit}' at position {pos} and append '{end_digit}'")
            else:
                print(f"Option {idx+1}: Insert '{digit}' at position {pos}")
        
        if len(valid_insertions) > 10:
            print(f"... and {len(valid_insertions) - 10} more options.")
        
        return valid_insertions[0][3]  # Return the first valid option
    else:
        print("No valid insertions found to reach 128 characters.")
        return hex_string

def xor_with_key(data, key):
    """XOR the data with a key."""
    if isinstance(key, str):
        key = key.encode('utf-8')
    
    return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))

def display_printable(data):
    """Filter and display only printable ASCII characters."""
    if isinstance(data, bytes):
        try:
            data = data.decode('utf-8', errors='ignore')
        except:
            data = data.decode('latin-1', errors='ignore')
    
    return ''.join(c if 32 <= ord(c) < 127 else '.' for c in data)

def check_bitcoin_patterns(hex_string):
    """Check if the hex string might represent common Bitcoin-related data."""
    print("\n=== CHECKING BITCOIN PATTERNS ===")
    
    # Convert to bytes
    try:
        data = bytes.fromhex(hex_string)
    except ValueError:
        print("Invalid hex string.")
        return
    
    # Check if it might be a BIP39 seed (16, 20, 24, 28, or 32 bytes)
    bytes_len = len(data)
    if bytes_len in [16, 20, 24, 28, 32]:
        print(f"Length ({bytes_len} bytes) matches a valid BIP39 seed.")
    
    # Check if it could be an EC private key (32 bytes)
    if bytes_len == 32:
        print("Length matches a Bitcoin EC private key (32 bytes).")
        
        # Calculate the SHA-256 hash (often used with private keys)
        sha256 = hashlib.sha256(data).hexdigest()
        print(f"SHA-256 hash: {sha256}")
    
    # Check if it could be a SHA-256 hash result (32 bytes)
    if bytes_len == 32:
        print("Length matches a SHA-256 hash (32 bytes).")
    
    # Check if it could be a RIPEMD-160 hash (20 bytes)
    if bytes_len == 20:
        print("Length matches a RIPEMD-160 hash (20 bytes).")
    
    # Check for double-length SHA-256 + RIPEMD-160 (40 bytes)
    if bytes_len == 40:
        print("Length matches a double hash (SHA-256 + RIPEMD-160) result (40 bytes).")
    
    # Check for standard Bitcoin transaction structure patterns
    if bytes_len > 10:
        print("\nChecking for transaction structure...")
        
        # Check if first 4 bytes could be a version
        version = int.from_bytes(data[:4], byteorder='little')
        print(f"If first 4 bytes represent version: {version}")
        
        # Check if last 4 bytes could be a locktime
        locktime = int.from_bytes(data[-4:], byteorder='little')
        print(f"If last 4 bytes represent locktime: {locktime}")
    
    # Calculate various Bitcoin-specific hashes
    print("\nCalculating Bitcoin-relevant hashes...")
    double_sha256 = hashlib.sha256(hashlib.sha256(data).digest()).hexdigest()
    try:
        ripemd160 = hashlib.new('ripemd160', data).hexdigest()
        print(f"RIPEMD-160: {ripemd160}")
    except Exception as e:
        print(f"RIPEMD-160 calculation failed: {e}")
    
    print(f"Double SHA-256: {double_sha256}")
    
    # Try to decode as various Bitcoin encodings
    try:
        # Try XOR with common Bitcoin-related keys
        print("\nTrying XOR with Bitcoin-related keys...")
        keys = ["bitcoin", "satoshi", "nakamoto", "key", "address", "wallet", "block", "transaction"]
        for key in keys:
            xor_result = xor_with_key(data, key)
            result_printable = display_printable(xor_result)
            print(f"XOR with '{key}': {result_printable}")
    except Exception as e:
        print(f"XOR decoding failed: {e}")

def try_multiple_combinations(original_hex, num_combinations=10):
    """Try multiple combinations of creating a 128-character hex string."""
    print(f"\n=== TRYING {num_combinations} DIFFERENT 128-CHARACTER COMBINATIONS ===")
    
    valid_insertions = []
    hex_digits = "0123456789abcdef"
    
    # Try inserting the same digit at different positions
    for digit in hex_digits:
        valid_insertions.append((0, digit, digit, f"{digit}{original_hex}{digit}"))
    
    # Try adding pairs of digits (0-0, 1-1, etc.) at beginning and end
    print("Trying pairs of hex digits...")
    for digit1 in hex_digits:
        for digit2 in hex_digits:
            valid_insertions.append((0, digit1, digit2, f"{digit1}{original_hex}{digit2}"))
    
    # Try only a select few combinations for efficiency
    selected_combinations = valid_insertions[:num_combinations]
    
    print(f"Testing {len(selected_combinations)} combinations...")
    
    results = []
    for i, (pos, digit1, digit2, fixed_string) in enumerate(selected_combinations):
        # Check for Bitcoin patterns in each combination
        print(f"\n--- Combination {i+1}: {digit1} at start, {digit2} at end ---")
        print(f"Fixed string: {fixed_string}")
        
        # Convert to bytes
        try:
            data = bytes.fromhex(fixed_string)
            results.append({
                "combination": (digit1, digit2),
                "fixed_string": fixed_string,
                "data": data
            })
            
            # Check some basic Bitcoin properties
            if len(data) == 64:  # 64 bytes = 128 hex characters
                # Calculate a SHA-256 hash for this variant
                sha256 = hashlib.sha256(data).hexdigest()
                print(f"SHA-256 hash: {sha256}")
                
                # Try XOR with 'bitcoin' as a simple test
                try:
                    xor_result = xor_with_key(data, "bitcoin")
                    printable = display_printable(xor_result)
                    printable_ratio = sum(1 for c in printable if c != '.') / len(printable)
                    print(f"XOR with 'bitcoin' (printable: {printable_ratio:.1%}): {printable}")
                except Exception as e:
                    print(f"XOR error: {e}")
        except ValueError as e:
            print(f"Error converting to bytes: {e}")
    
    # Return all results
    return results

if __name__ == "__main__":
    # The original problematic hex string
    original_hex = "925f94cd6e13cb4fa50400050664458b371cc56a324b4d1e38e27305badbef1582c32d061820081b6f1172c9937f4eafd7cb7d2f2e4b2f95e23beafd2197e0"
    
    # Test all possible insertions to reach 128 characters (64 bytes)
    fixed_hex = test_all_positions(original_hex)
    
    # Try multiple combinations
    results = try_multiple_combinations(original_hex, 20)
    
    # Check for Bitcoin-related patterns in one of the fixed strings
    if results:
        # Use the most promising result (for now, just the first one)
        best_result = results[0]
        print(f"\n=== DETAILED ANALYSIS OF COMBINATION {best_result['combination']} ===")
        check_bitcoin_patterns(best_result['fixed_string'])
    else:
        print("\nNo valid 128-character combinations found.") 