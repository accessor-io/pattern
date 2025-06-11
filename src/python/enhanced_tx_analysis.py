#!/usr/bin/env python3
import json
import os
import binascii
import hashlib
import base64
import itertools
import math
import re
import hmac

def hex_to_bytes(hex_string):
    """Convert a hex string to bytes, handling non-hex characters."""
    try:
        return bytes.fromhex(hex_string)
    except ValueError as e:
        # Find the invalid character
        for i, c in enumerate(hex_string):
            if c not in '0123456789abcdefABCDEF':
                print(f"Invalid hex character '{c}' at position {i}")
        return None

def display_printable(data):
    """Filter and display only printable ASCII characters."""
    if isinstance(data, bytes):
        try:
            data = data.decode('utf-8', errors='ignore')
        except:
            data = data.decode('latin-1', errors='ignore')
    
    return ''.join(c if 32 <= ord(c) < 127 else '.' for c in data)

def calculate_entropy(data):
    """Calculate the entropy of the data (in bits per byte)."""
    if not data:
        return 0
    
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    # Count occurrences of each byte
    byte_counts = {}
    for byte in data:
        byte_counts[byte] = byte_counts.get(byte, 0) + 1
    
    # Calculate Shannon entropy
    entropy = 0
    for count in byte_counts.values():
        probability = count / len(data)
        if probability > 0:  # Avoid log(0)
            entropy -= probability * math.log2(probability)
    
    return entropy

def xor_with_key(data, key):
    """XOR the data with a key."""
    if isinstance(key, str):
        key = key.encode('utf-8')
    
    return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))

def vigenere_decrypt(text, key):
    """Apply Vigenère cipher decryption."""
    if isinstance(text, bytes):
        text = text.decode('latin-1', errors='ignore')
    
    result = []
    key_length = len(key)
    key_as_int = [ord(i) for i in key]
    
    for i, char in enumerate(text):
        char_code = ord(char)
        # Only apply to printable ASCII characters to avoid corrupting other bytes
        if 32 <= char_code <= 126:
            # Apply the Vigenère decryption formula
            decrypted_code = (char_code - key_as_int[i % key_length]) % 95 + 32
            result.append(chr(decrypted_code))
        else:
            # Keep non-printable characters as is
            result.append(char)
    
    return ''.join(result)

def find_text_patterns(result_string):
    """Look for patterns in the decoded result that might indicate hidden text."""
    # Common pattern indicators
    patterns = [
        r'bitcoin', r'btc', r'satoshi', r'nakamoto', r'wallet', r'key', r'address', r'priv',
        r'block', r'transaction', r'http[s]?://', r'www\.', r'\.com', r'\.org', r'term',
        r'puzzle', r'clue', r'hint', r'secret', r'hidden', r'find', r'congrat', r'next',
        r'password', r'passphrase', r'encrypt', r'decrypt', r'cipher', r'private', r'p2p',
        r'public', r'message', r'rick', r'roll', r'never', r'gonna', r'xmr', r'eth', 'reward',
        r'dogecoin', r'smart', r'contract', r'script', r'hash', r'sha256', r'nonce',
        r'1[a-km-zA-HJ-NP-Z1-9]{25,34}' # Bitcoin address pattern
    ]
    
    # Prepare regex patterns
    regex_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    # Search for patterns
    found_patterns = []
    for i, regex in enumerate(regex_patterns):
        matches = regex.findall(result_string)
        if matches:
            found_patterns.append((patterns[i], matches))
    
    return found_patterns

def rotate_bytes(data, n=1):
    """Rotate bytes by n positions."""
    if not data:
        return data
    n = n % len(data)
    return data[n:] + data[:n]

def try_tx_data_combinations(hex_string, tx_fields, threshold=0.6):
    """Try various combinations of transaction fields as decryption keys."""
    print("\n=== TRYING TRANSACTION DATA COMBINATIONS ===")
    
    bytes_data = hex_to_bytes(hex_string)
    if not bytes_data:
        return
    
    interesting_results = []
    
    # Try using pairs of fields as keys
    print("\nTrying field combinations...")
    keys = list(tx_fields.values())
    key_names = list(tx_fields.keys())
    
    # Add basic Bitcoin-related keys
    extra_keys = ["bitcoin", "satoshi", "nakamoto", "key", "address", "wallet", "block", "transaction"]
    extra_names = ["bitcoin", "satoshi", "nakamoto", "key", "address", "wallet", "block", "transaction"]
    
    keys.extend(extra_keys)
    key_names.extend(extra_names)
    
    # Try each key individually
    for i, key in enumerate(keys):
        if not key:
            continue
        
        try:
            # XOR decoding
            xor_result = xor_with_key(bytes_data, key)
            xor_printable = display_printable(xor_result)
            
            # Calculate printable ratio
            printable_ratio = sum(1 for c in xor_printable if c != '.') / len(xor_printable)
            
            # Check for patterns
            patterns = find_text_patterns(xor_printable)
            
            if printable_ratio > threshold or patterns:
                entropy = calculate_entropy(xor_result)
                interesting_results.append({
                    "key": key_names[i],
                    "method": "XOR",
                    "printable_ratio": printable_ratio,
                    "entropy": entropy,
                    "text": xor_printable,
                    "patterns": patterns
                })
                
                # Also try SHA-256 HMAC
                hmac_key = key.encode('utf-8') if isinstance(key, str) else key
                hmac_result = hmac.new(hmac_key, bytes_data, hashlib.sha256).hexdigest()
                interesting_results.append({
                    "key": key_names[i],
                    "method": "HMAC-SHA256",
                    "text": hmac_result,
                    "patterns": find_text_patterns(hmac_result)
                })
        except Exception as e:
            continue
    
    # Try HMAC with all fields combined
    try:
        combined_key = ''.join(str(v) for v in tx_fields.values()).encode('utf-8')
        hmac_result = hmac.new(combined_key, bytes_data, hashlib.sha256).hexdigest()
        interesting_results.append({
            "key": "All fields combined",
            "method": "HMAC-SHA256",
            "text": hmac_result,
            "patterns": find_text_patterns(hmac_result)
        })
    except Exception as e:
        pass
    
    # Try composite fields
    for i, key1 in enumerate(keys):
        for j, key2 in enumerate(keys):
            if i >= j or not key1 or not key2:
                continue
            
            composite_key = f"{key1}_{key2}"
            try:
                xor_result = xor_with_key(bytes_data, composite_key)
                xor_printable = display_printable(xor_result)
                printable_ratio = sum(1 for c in xor_printable if c != '.') / len(xor_printable)
                patterns = find_text_patterns(xor_printable)
                
                if printable_ratio > threshold or patterns:
                    entropy = calculate_entropy(xor_result)
                    interesting_results.append({
                        "key": f"{key_names[i]} + {key_names[j]}",
                        "method": "XOR with composite",
                        "printable_ratio": printable_ratio,
                        "entropy": entropy,
                        "text": xor_printable,
                        "patterns": patterns
                    })
            except Exception as e:
                continue
    
    # Sort by printable ratio and pattern count
    sorted_results = sorted(
        interesting_results, 
        key=lambda x: (
            len(x.get("patterns", [])), 
            x.get("printable_ratio", 0) if "printable_ratio" in x else 0
        ), 
        reverse=True
    )
    
    # Display top results
    print(f"\nFound {len(sorted_results)} interesting results. Top 10:")
    for i, result in enumerate(sorted_results[:10]):
        print(f"\n{i+1}. Key: {result['key']}, Method: {result['method']}")
        if "printable_ratio" in result:
            print(f"   Printable ratio: {result['printable_ratio']:.1%}")
        if "entropy" in result:
            print(f"   Entropy: {result['entropy']:.2f} bits/byte")
        if result.get("patterns"):
            print(f"   Patterns found: {result['patterns']}")
        print(f"   Result: {result['text'][:100]}{'...' if len(result['text']) > 100 else ''}")
    
    return sorted_results

def check_for_hidden_files(hex_string):
    """Check if the hex string contains file signatures indicating hidden files."""
    print("\n=== CHECKING FOR HIDDEN FILES ===")
    
    bytes_data = hex_to_bytes(hex_string)
    if not bytes_data:
        return
    
    # Common file signatures
    file_signatures = {
        b'\x50\x4B\x03\x04': 'ZIP archive',
        b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'PNG image',
        b'\xFF\xD8\xFF': 'JPEG image',
        b'GIF8': 'GIF image',
        b'PK': 'ZIP archive (short)',
        b'\x25\x50\x44\x46': 'PDF document',
        b'\x52\x61\x72\x21': 'RAR archive',
        b'\x42\x5A\x68': 'BZIP archive',
        b'\x1F\x8B\x08': 'GZIP archive',
        b'\x7F\x45\x4C\x46': 'ELF binary',
    }
    
    found_signatures = []
    
    for signature, file_type in file_signatures.items():
        if isinstance(signature, str):
            signature = signature.encode('ascii')
        
        for i in range(len(bytes_data) - len(signature) + 1):
            if bytes_data[i:i+len(signature)] == signature:
                found_signatures.append({
                    "type": file_type,
                    "offset": i,
                    "signature": signature.hex()
                })
    
    if found_signatures:
        print("Found potential embedded files:")
        for i, found in enumerate(found_signatures):
            print(f"{i+1}. {found['type']} signature at offset {found['offset']} (0x{found['offset']:X})")
    else:
        print("No common file signatures found in the hex data.")
    
    # Try to extract a Bitcoin private key in WIF format
    for i in range(len(bytes_data) - 32 + 1):
        potential_key = bytes_data[i:i+32]
        try:
            # Add version byte (0x80 for mainnet private key)
            with_version = b'\x80' + potential_key
            
            # Double SHA-256 for checksum
            checksum = hashlib.sha256(hashlib.sha256(with_version).digest()).digest()[:4]
            
            # Full WIF data
            wif_data = with_version + checksum
            
            # Convert to Base58
            result = ''
            value = int.from_bytes(wif_data, byteorder='big')
            alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
            
            while value:
                value, mod = divmod(value, 58)
                result = alphabet[mod] + result
            
            # Add 1's for leading zeros
            for byte in wif_data:
                if byte == 0:
                    result = '1' + result
                else:
                    break
            
            print(f"Potential WIF private key at offset {i}: {result}")
            
            # Try to convert to a Bitcoin address
            try:
                sha256_hash = hashlib.sha256(potential_key).digest()
                ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
                # Add version byte (0x00 for mainnet)
                versioned_hash = b'\x00' + ripemd160_hash
                # Double SHA-256
                checksum = hashlib.sha256(hashlib.sha256(versioned_hash).digest()).digest()[:4]
                binary_address = versioned_hash + checksum
                address = ''
                value = int.from_bytes(binary_address, byteorder='big')
                
                while value:
                    value, mod = divmod(value, 58)
                    address = alphabet[mod] + address
                
                # Add 1's for leading zeros
                for byte in binary_address:
                    if byte == 0:
                        address = '1' + address
                    else:
                        break
                
                print(f"Corresponding Bitcoin address: {address}")
            except Exception as e:
                print(f"Error calculating Bitcoin address: {e}")
        except Exception as e:
            # Skip errors and continue looking
            pass

def analyze_combinations(hex_string):
    """Try multiple 64-byte (128-character) combinations of the hex string."""
    print(f"\n=== TRYING DIFFERENT 64-BYTE COMBINATIONS ===")
    print(f"Original string: {hex_string} ({len(hex_string)} characters)")
    
    # If we're adding 2 characters to reach 128, try different insert positions
    chars_to_add = 128 - len(hex_string)
    
    if chars_to_add <= 0:
        print(f"String is already {len(hex_string)} characters. Not adding more.")
        return hex_string
    
    print(f"Need to add {chars_to_add} characters to reach 128 (64 bytes).")
    
    # Try different hex digit combinations
    hex_digits = "0123456789abcdef"
    combinations = []
    
    if chars_to_add == 1:
        # Try appending a character
        for digit in hex_digits:
            combinations.append((hex_string + digit, f"Append '{digit}'"))
    elif chars_to_add == 2:
        # Try first few combinations of (prefix, suffix)
        for prefix in hex_digits[:4]:  # Limit to first 4 digits for prefix
            for suffix in hex_digits[:4]:  # Limit to first 4 digits for suffix
                combinations.append((prefix + hex_string + suffix, f"Add '{prefix}' at start, '{suffix}' at end"))
    else:
        # For other cases, just use simple padding
        padding = "0" * chars_to_add
        combinations.append((hex_string + padding, f"Append {chars_to_add} zeros"))
    
    results = []
    
    # Test each combination and calculate interesting metrics
    for i, (combo, desc) in enumerate(combinations):
        try:
            data = bytes.fromhex(combo)
            
            # Calculate entropy
            entropy = calculate_entropy(data)
            
            # Calculate SHA-256 hash
            sha256 = hashlib.sha256(data).hexdigest()
            
            # Try XOR with 'bitcoin' as a test
            xor_result = xor_with_key(data, "bitcoin")
            xor_printable = display_printable(xor_result)
            printable_ratio = sum(1 for c in xor_printable if c != '.') / len(xor_printable)
            
            # Look for patterns
            patterns = find_text_patterns(xor_printable)
            
            results.append({
                "combination": desc,
                "hex": combo,
                "data": data,
                "entropy": entropy,
                "sha256": sha256,
                "xor_printable_ratio": printable_ratio,
                "xor_text": xor_printable,
                "patterns": patterns
            })
            
            print(f"\nTesting combination {i+1}: {desc}")
            print(f"Entropy: {entropy:.2f} bits/byte")
            print(f"SHA-256: {sha256}")
            print(f"XOR with 'bitcoin' (printable: {printable_ratio:.1%}): {xor_printable[:50]}...")
            if patterns:
                print(f"Found patterns: {patterns}")
        
        except ValueError as e:
            print(f"Error with combination {i+1}: {e}")
    
    # Sort by interesting factors (pattern count, entropy, printable ratio)
    sorted_results = sorted(
        results,
        key=lambda x: (len(x["patterns"]), x["entropy"], x["xor_printable_ratio"]),
        reverse=True
    )
    
    if sorted_results:
        best_result = sorted_results[0]
        print(f"\nBest combination: {best_result['combination']}")
        print(f"Hex: {best_result['hex']}")
        return best_result['hex']
    else:
        print("No valid combinations found.")
        return hex_string

def load_transaction_data():
    """Load transaction data from the term 68 file."""
    print("\n=== LOADING TRANSACTION DATA ===")
    
    tx_file = './tx_cache/1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ.json'
    if not os.path.exists(tx_file):
        print(f"Transaction file {tx_file} not found!")
        return {}
    
    try:
        with open(tx_file, 'r') as f:
            tx_data = json.load(f)
            print(f"Successfully loaded transaction data from {tx_file}")
            
            # Check if transaction data is empty or null
            if not tx_data:
                print("Transaction data is empty or null.")
                return {}
                
            # Extract key fields from the transaction
            tx_fields = {}
            
            # Handle different possible structures
            if isinstance(tx_data, dict):
                if "txs" in tx_data and isinstance(tx_data["txs"], list) and tx_data["txs"]:
                    # Handle structure with 'txs' array
                    tx = tx_data["txs"][0]  # Take the first transaction
                    print(f"Found transaction in 'txs' array with txid: {tx.get('txid', 'unknown')}")
                    
                    tx_fields = {
                        "txid": tx.get("txid", ""),
                        "version": str(tx.get("version", "")),
                        "locktime": str(tx.get("locktime", "")),
                    }
                    
                    # Extract input addresses if available
                    if "vin" in tx and tx["vin"]:
                        for i, vin in enumerate(tx["vin"]):
                            if "prevout" in vin and "scriptpubkey_address" in vin["prevout"]:
                                tx_fields[f"input_addr_{i}"] = vin["prevout"]["scriptpubkey_address"]
                            elif "txid" in vin:
                                tx_fields[f"input_txid_{i}"] = vin["txid"]
                    
                    # Extract output addresses if available
                    if "vout" in tx and tx["vout"]:
                        for i, vout in enumerate(tx["vout"]):
                            if "scriptpubkey_address" in vout:
                                tx_fields[f"output_addr_{i}"] = vout["scriptpubkey_address"]
                                tx_fields[f"output_value_{i}"] = str(vout.get("value", ""))
                
                # Try original structure as well
                elif "hash" in tx_data:
                    # Original expected structure
                    tx_fields = {
                        "txid": tx_data.get("hash", ""),
                        "version": str(tx_data.get("ver", "")),
                        "blockheight": str(tx_data.get("block_height", "")),
                        "timestamp": str(tx_data.get("time", "")),
                    }
                    
                    # Extract input addresses
                    if "inputs" in tx_data:
                        for i, inp in enumerate(tx_data.get("inputs", [])):
                            if "prev_out" in inp and "addr" in inp["prev_out"]:
                                tx_fields[f"input_addr_{i}"] = inp["prev_out"]["addr"]
                                tx_fields[f"input_value_{i}"] = str(inp["prev_out"].get("value", ""))
                    
                    # Extract output addresses
                    if "out" in tx_data:
                        for i, out in enumerate(tx_data.get("out", [])):
                            if "addr" in out:
                                tx_fields[f"output_addr_{i}"] = out["addr"]
                                tx_fields[f"output_value_{i}"] = str(out.get("value", ""))
            
            print("\nExtracted transaction fields:")
            for name, value in tx_fields.items():
                print(f"{name}: {value}")
            
            return tx_fields
    
    except Exception as e:
        print(f"Error processing transaction data: {e}")
        return {}

def main():
    # The original problematic hex string
    hex_string = "925f94cd6e13cb4fa50400050664458b371cc56a324b4d1e38e27305badbef1582c32d061820081b6f1172c9937f4eafd7cb7d2f2e4b2f95e23beafd2197e0"
    
    # First, try different 64-byte combinations
    fixed_hex = analyze_combinations(hex_string)
    
    # Load transaction data for additional analysis
    tx_fields = load_transaction_data()
    
    # Try transaction data field combinations
    if tx_fields:
        try_tx_data_combinations(fixed_hex, tx_fields)
    
    # Check for hidden files
    check_for_hidden_files(fixed_hex)
    
    print("\n=== ANALYSIS COMPLETE ===")
    print("Notes:")
    print("1. The data shows moderate entropy, consistent with encrypted or compressed content.")
    print("2. The original hex string could be part of a private key, transaction data, or a complex puzzle.")
    print("3. Multiple decryption methods and combinations have been attempted.")
    print("4. Consider examining any high printable-ratio results for hidden messages or clues.")

if __name__ == "__main__":
    main() 