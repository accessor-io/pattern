#!/usr/bin/env python3
import json
import os
import binascii
import hashlib
import base64
import itertools
import struct
import re
import math

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

def xor_with_key(data, key):
    """XOR the data with a key."""
    if isinstance(key, str):
        key = key.encode('utf-8')
    
    return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))

def try_various_xor_keys(hex_string):
    """Try XORing with various Bitcoin-related keys."""
    print("\n=== TRYING VARIOUS XOR KEYS ===")
    bytes_data = hex_to_bytes(hex_string)
    if not bytes_data:
        return
    
    # Common Bitcoin-related keys to try
    keys = [
        "bitcoin", "satoshi", "nakamoto", "blockchain", "transaction",
        "private", "public", "key", "address", "wallet", "btc", "hash",
        "block", "mine", "coin", "crypto", "secp256k1", "sha256", "ripemd160",
        "p2pkh", "segwit", "bip32", "bip39", "bip44", "xpub", "xprv"
    ]
    
    for key in keys:
        result = xor_with_key(bytes_data, key)
        printable = display_printable(result)
        # Only show results that have a high percentage of printable characters
        printable_ratio = sum(1 for c in printable if c != '.') / len(printable)
        if printable_ratio > 0.6:  # Show if more than 60% is printable
            print(f"XOR with '{key}': {printable}")

def analyze_as_tx_structure(hex_string):
    """Analyze the hex as a potential Bitcoin transaction structure."""
    print("\n=== ANALYZING AS POTENTIAL TRANSACTION STRUCTURE ===")
    
    bytes_data = hex_to_bytes(hex_string)
    if not bytes_data:
        return
    
    # Check if it might be a transaction version
    if len(bytes_data) >= 4:
        possible_version = int.from_bytes(bytes_data[:4], 'little')
        print(f"If first 4 bytes represent version: {possible_version}")
    
    # Look for potential lock_time at the end (4 bytes)
    if len(bytes_data) >= 4:
        possible_locktime = int.from_bytes(bytes_data[-4:], 'little')
        print(f"If last 4 bytes represent lock_time: {possible_locktime}")
    
    # Look for Bitcoin message headers (like "Bitcoin Signed Message:")
    bitcoin_msg_pattern = b"Bitcoin Signed Message:"
    if re.search(bitcoin_msg_pattern, bytes_data, re.IGNORECASE):
        print("Found Bitcoin signed message pattern!")

def analyze_as_bip39_seed(hex_string):
    """Check if the hex could be a BIP39 seed for wallet generation."""
    print("\n=== ANALYZING AS POTENTIAL BIP39 SEED ===")
    
    # BIP39 seeds are typically 128, 160, 192, 224, or 256 bits (16-32 bytes)
    bytes_len = len(hex_string) // 2
    if bytes_len in [16, 20, 24, 28, 32]:
        print(f"Length ({bytes_len} bytes) matches a valid BIP39 seed length!")
    else:
        print(f"Length ({bytes_len} bytes) doesn't match standard BIP39 seed lengths")
    
    # Calculate checksum and see if it might be a valid seed
    try:
        bytes_data = hex_to_bytes(hex_string)
        if bytes_data:
            checksum_bits = hashlib.sha256(bytes_data).digest()[0] >> (8 - (len(bytes_data) * 8) // 32)
            print(f"BIP39 checksum bits would be: {bin(checksum_bits)[2:].zfill((len(bytes_data) * 8) // 32)}")
    except Exception as e:
        print(f"Error in BIP39 seed analysis: {e}")

def analyze_as_wallet_import_format(hex_string):
    """Check if the hex could represent a private key in Wallet Import Format."""
    print("\n=== ANALYZING AS POTENTIAL WIF PRIVATE KEY ===")
    
    # A typical Bitcoin private key should be 32 bytes
    if len(hex_string) != 64:
        print(f"Length ({len(hex_string)//2} bytes) doesn't match a standard Bitcoin private key (32 bytes)")
        return
    
    try:
        # Steps to convert private key to WIF
        bytes_data = hex_to_bytes(hex_string)
        if not bytes_data:
            return
        
        # 1. Add version byte (0x80 for mainnet)
        with_version = b'\x80' + bytes_data
        
        # 2. Calculate SHA-256 hash of the extended key
        hash1 = hashlib.sha256(with_version).digest()
        
        # 3. Calculate SHA-256 hash of the result
        hash2 = hashlib.sha256(hash1).digest()
        
        # 4. Take the first 4 bytes as checksum
        checksum = hash2[:4]
        
        # 5. Add checksum to the extended key
        with_checksum = with_version + checksum
        
        # 6. Convert to Base58
        # (Simplified - would need actual Base58 implementation)
        print("To convert to WIF, you would need to Base58 encode the versioned key with checksum")
        print(f"First few bytes of versioned key with checksum: {with_checksum[:8].hex()}")
    except Exception as e:
        print(f"Error in WIF analysis: {e}")

def entropy_analysis(hex_string):
    """Analyze the entropy/randomness of the hex string."""
    print("\n=== ENTROPY ANALYSIS ===")
    
    bytes_data = hex_to_bytes(hex_string)
    if not bytes_data:
        return
    
    # Count occurrences of each byte
    byte_counts = {}
    for byte in bytes_data:
        byte_counts[byte] = byte_counts.get(byte, 0) + 1
    
    # Calculate entropy using proper logarithm calculation
    entropy = 0
    for count in byte_counts.values():
        probability = count / len(bytes_data)
        if probability > 0:  # Avoid log(0)
            entropy -= probability * math.log2(probability)
    
    max_entropy = math.log2(256)  # Maximum entropy for a byte is log2(256)
    total_info_bits = entropy * len(bytes_data)
    entropy_ratio = entropy / max_entropy if max_entropy > 0 else 0
    
    print(f"Entropy estimate: {entropy:.2f} bits per byte (ratio: {entropy_ratio:.2%})")
    print(f"Total information content estimate: {total_info_bits:.2f} bits")
    print(f"Number of unique bytes: {len(byte_counts)} out of 256 possible values")
    
    if entropy_ratio > 0.9:
        print("High entropy - likely random or encrypted data")
    elif entropy_ratio > 0.7:
        print("Moderate entropy - could be compressed or encoded data")
    else:
        print("Low entropy - likely structured or plaintext data")

def analyze_as_tx_hash(hex_string):
    """Analyze the hex string as a potential transaction hash."""
    print("\n=== ANALYZING AS POTENTIAL TRANSACTION HASH ===")
    
    # A Bitcoin tx hash is 32 bytes (64 hex chars)
    if len(hex_string) >= 64:
        potential_tx_hash = hex_string[:64]
        print(f"Potential transaction hash: {potential_tx_hash}")
        print(f"This could be used to look up a transaction on a block explorer:")
        print(f"https://www.blockchain.com/explorer/transactions/{potential_tx_hash}")
    
    # It could also be just a portion of a hash
    if len(hex_string) < 64:
        print(f"String length ({len(hex_string)}) is less than a full tx hash (64). Could be partial hash.")
    
    # Try reversing the bytes (Bitcoin often stores hashes in little-endian)
    if len(hex_string) >= 2:
        reversed_hex = ''.join(reversed([hex_string[i:i+2] for i in range(0, len(hex_string), 2)]))
        print(f"Reversed bytes: {reversed_hex}")
        print(f"This could also be used to look up a transaction if the original is byte-reversed.")

def analyze_as_private_key(hex_string):
    """Check if the hex string could be a Bitcoin private key."""
    print("\n=== ANALYZING AS POTENTIAL PRIVATE KEY ===")
    
    # A Bitcoin private key is typically 32 bytes (64 hex chars)
    if len(hex_string) == 64:
        print("Length matches a typical Bitcoin private key (32 bytes).")
    
    # Calculate the potential Bitcoin address from this private key
    # Note: This is simplified and doesn't implement full Bitcoin key derivation
    try:
        # Simulate the process of deriving a Bitcoin address from a private key
        # (This is a simplified version and would require the secp256k1 library for actual implementation)
        print("To properly check if this is a valid private key, we would need to:")
        print("1. Use the secp256k1 library to derive the public key from this private key")
        print("2. Hash the public key with SHA-256 and RIPEMD-160")
        print("3. Add version byte and checksum")
        print("4. Encode with Base58Check to get the Bitcoin address")
    except Exception as e:
        print(f"Error in private key analysis: {e}")

def analyze_as_script(hex_string):
    """Analyze the hex as a potential Bitcoin script."""
    print("\n=== ANALYZING AS POTENTIAL BITCOIN SCRIPT ===")
    
    # Common Bitcoin script opcodes
    opcodes = {
        "00": "OP_0",
        "51": "OP_1",
        "52": "OP_2",
        "76": "OP_DUP",
        "a9": "OP_HASH160",
        "88": "OP_EQUALVERIFY",
        "ac": "OP_CHECKSIG",
        # ... many more opcodes exist
    }
    
    script_analysis = []
    for i in range(0, len(hex_string), 2):
        if i+2 <= len(hex_string):
            byte = hex_string[i:i+2]
            if byte in opcodes:
                script_analysis.append(f"{byte}: {opcodes[byte]}")
            else:
                script_analysis.append(f"{byte}: (data)")
    
    print("Potential script interpretation (limited opcodes recognized):")
    print(", ".join(script_analysis))

def bit_pattern_analysis(hex_string):
    """Analyze bit patterns and potential bit positions that might be significant."""
    print("\n=== BIT PATTERN ANALYSIS ===")
    
    bytes_data = hex_to_bytes(hex_string)
    if not bytes_data:
        return
    
    # Convert to binary representation for bit-level analysis
    binary = ''.join(format(byte, '08b') for byte in bytes_data)
    
    # Count 1s and 0s
    ones = binary.count('1')
    zeros = binary.count('0')
    total_bits = len(binary)
    
    print(f"Total bits: {total_bits} (Ones: {ones} - {ones/total_bits:.2%}, Zeros: {zeros} - {zeros/total_bits:.2%})")
    
    # Look for repeating patterns
    for pattern_len in range(3, 11):  # Look for patterns of length 3 to 10
        patterns = {}
        for i in range(len(binary) - pattern_len + 1):
            pattern = binary[i:i+pattern_len]
            patterns[pattern] = patterns.get(pattern, 0) + 1
        
        # Find most common patterns
        common_patterns = sorted([(p, c) for p, c in patterns.items() if c > 1], key=lambda x: x[1], reverse=True)
        if common_patterns and len(common_patterns) > 0:
            most_common = common_patterns[0]
            if most_common[1] > 3:  # Only show if pattern appears more than 3 times
                print(f"Most common {pattern_len}-bit pattern: {most_common[0]} (occurs {most_common[1]} times)")

def find_text_patterns(result_string):
    """Look for patterns in the decoded result that might indicate hidden text."""
    # Common pattern indicators
    patterns = [
        r'bitcoin', r'btc', r'satoshi', r'nakamoto', r'wallet', r'key', r'address',
        r'block', r'transaction', r'http[s]?://', r'www\.', r'\.com', r'\.org',
        r'puzzle', r'clue', r'hint', r'secret', r'hidden', r'find', r'congrat',
        r'password', r'passphrase', r'encrypt', r'decrypt', r'cipher', r'private',
        r'public', r'message', r'rick', r'roll', r'never', r'gonna', r'xmr', r'eth',
        r'dogecoin', r'smart', r'contract', r'script', r'hash', r'sha256', r'nonce'
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

def analyze_xor_result_for_patterns(result, key_desc):
    """Analyze XOR result for interesting patterns."""
    # Get printable version
    printable = display_printable(result)
    
    # Calculate printable ratio
    printable_ratio = sum(1 for c in printable if c != '.') / len(printable)
    
    # Find text patterns
    patterns = find_text_patterns(printable)
    
    output = {
        "printable_ratio": printable_ratio,
        "has_interesting_patterns": len(patterns) > 0,
        "patterns": patterns,
        "printable_text": printable
    }
    
    # Check for high printable ratio or interesting patterns
    if printable_ratio > 0.5 or len(patterns) > 0:
        print(f"Result for {key_desc} (printable: {printable_ratio:.1%}): {printable}")
        if patterns:
            print(f"  Found patterns: {patterns}")
    
    return output

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

def rot13_transform(text):
    """Apply ROT13 transformation to the text."""
    result = []
    for char in text:
        char_code = ord(char)
        # Apply ROT13 to letters only
        if 65 <= char_code <= 90:  # A-Z
            result.append(chr((char_code - 65 + 13) % 26 + 65))
        elif 97 <= char_code <= 122:  # a-z
            result.append(chr((char_code - 97 + 13) % 26 + 97))
        else:
            result.append(char)
    return ''.join(result)

def try_multi_layer_decryption(hex_string, tx_fields):
    """Try multiple layers of decryption (XOR, Vigenère, ROT13) with various keys."""
    print("\n=== TRYING MULTI-LAYER DECRYPTION ===")
    bytes_data = hex_to_bytes(hex_string)
    if not bytes_data:
        return
    
    # Additional Bitcoin-related keys to try
    common_keys = [
        "bitcoin", "satoshi", "nakamoto", "blockchain", "transaction",
        "private", "wallet", "key", "address", "puzzle", "term68",
        "KONAMI", "btc", "crypto", "block", "reward"
    ]
    
    # Combine tx_fields with common keys
    all_keys = list(tx_fields.values()) + common_keys
    
    multi_layer_results = []
    
    print("Trying XOR + Vigenère + ROT13 combinations...")
    for xor_key in all_keys:
        if not xor_key:
            continue
        
        try:
            # Apply XOR
            xor_result = xor_with_key(bytes_data, xor_key)
            
            # Get printable representation of the XOR result
            xor_printable = display_printable(xor_result)
            
            # Apply Vigenère with each key as a second layer
            for vig_key in all_keys:
                if not vig_key:
                    continue
                
                # Skip if same key
                if xor_key == vig_key:
                    continue
                
                try:
                    # Apply Vigenère cipher
                    vig_result = vigenere_decrypt(xor_result, vig_key)
                    
                    # Check for interesting patterns in the Vigenère result
                    vig_patterns = find_text_patterns(vig_result)
                    
                    # Calculate printable ratio for Vigenère result
                    vig_printable_ratio = sum(1 for c in vig_result if 32 <= ord(c) <= 126) / len(vig_result)
                    
                    # If Vigenère result looks promising
                    if vig_printable_ratio > 0.6 or vig_patterns:
                        # Also try ROT13 as a third layer
                        rot13_result = rot13_transform(vig_result)
                        rot13_patterns = find_text_patterns(rot13_result)
                        
                        # Keep track of both Vigenère and ROT13 results
                        multi_layer_results.append({
                            "xor_key": xor_key,
                            "vig_key": vig_key,
                            "layer": "vigenere",
                            "result": vig_result,
                            "patterns": vig_patterns,
                            "printable_ratio": vig_printable_ratio
                        })
                        
                        if rot13_patterns:
                            multi_layer_results.append({
                                "xor_key": xor_key,
                                "vig_key": vig_key,
                                "layer": "rot13",
                                "result": rot13_result,
                                "patterns": rot13_patterns,
                                "printable_ratio": sum(1 for c in rot13_result if 32 <= ord(c) <= 126) / len(rot13_result)
                            })
                
                except Exception as e:
                    continue  # Skip this key combination if it fails
        
        except Exception as e:
            continue  # Skip this XOR key if it fails
    
    # Sort results by the number of patterns and printable ratio
    promising_results = sorted(
        [r for r in multi_layer_results if r["printable_ratio"] > 0.6 or r["patterns"]],
        key=lambda x: (len(x["patterns"]), x["printable_ratio"]),
        reverse=True
    )
    
    # Show the most promising results
    if promising_results:
        print(f"\nFound {len(promising_results)} promising multi-layer decryption results.")
        print("\nTop 5 Multi-Layer Decryption Results:")
        for i, result in enumerate(promising_results[:5]):
            print(f"{i+1}. XOR key: '{result['xor_key']}', {result['layer'].capitalize()} key: '{result['vig_key']}'")
            print(f"   Printable ratio: {result['printable_ratio']:.1%}")
            if result["patterns"]:
                print(f"   Patterns found: {result['patterns']}")
            print(f"   Text: {result['result']}")
    else:
        print("No promising multi-layer decryption results found.")
    
    return promising_results

def try_tx_data_fields(hex_string):
    """Try to extract transaction data fields from the hex string."""
    print("\n=== ANALYZING FOR TX DATA FIELDS ===")
    
    # Try to load transaction data from the term 68 file
    tx_file = './tx_cache/1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ.json'
    if not os.path.exists(tx_file):
        print(f"Transaction file {tx_file} not found!")
        return
    
    try:
        with open(tx_file, 'r') as f:
            tx_data = json.load(f)
            print(f"Successfully loaded transaction data from {tx_file}")
            
            # Check if transaction data is empty or null
            if not tx_data:
                print("Transaction data is empty or null.")
                return
                
            # Check transaction data type
            print(f"Transaction data type: {type(tx_data)}")
            
            # Print raw transaction data fields for debugging
            print("\nRaw transaction data keys:", list(tx_data.keys()) if isinstance(tx_data, dict) else "Not a dictionary")
            
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
            if tx_fields:
                for name, value in tx_fields.items():
                    print(f"{name}: {value}")
            else:
                print("No transaction fields could be extracted.")
                return
                
            # Try using each field as a key for XOR decoding
            bytes_data = hex_to_bytes(hex_string)
            if bytes_data:
                xor_results = []
                
                print("\n=== XOR DECODING WITH TRANSACTION FIELDS ===")
                for field_name, key in tx_fields.items():
                    if not key:
                        continue
                    
                    print(f"\nTrying XOR with transaction field {field_name}: {key}")
                    try:
                        xor_result = xor_with_key(bytes_data, key)
                        analysis = analyze_xor_result_for_patterns(xor_result, f"field {field_name}")
                        xor_results.append({
                            "field": field_name,
                            "key": key,
                            "analysis": analysis
                        })
                    except Exception as e:
                        print(f"Error with XOR: {e}")
                    
                    # Try XOR with the first N bytes of the field
                    for length in [4, 8, 16]:
                        if len(key) >= length:
                            partial_key = key[:length]
                            try:
                                xor_result = xor_with_key(bytes_data, partial_key)
                                analysis = analyze_xor_result_for_patterns(xor_result, f"first {length} chars of {field_name} ({partial_key})")
                                xor_results.append({
                                    "field": f"{field_name} (first {length} chars)",
                                    "key": partial_key,
                                    "analysis": analysis
                                })
                            except Exception as e:
                                print(f"Error with partial XOR: {e}")
                
                # Summarize the most promising results
                print("\n=== SUMMARY OF MOST PROMISING XOR RESULTS ===")
                promising_results = sorted(
                    [r for r in xor_results if r["analysis"]["printable_ratio"] > 0.5 or r["analysis"]["has_interesting_patterns"]],
                    key=lambda x: (len(x["analysis"]["patterns"]), x["analysis"]["printable_ratio"]),
                    reverse=True
                )
                
                for i, result in enumerate(promising_results[:5]):  # Show top 5
                    print(f"{i+1}. Key: {result['field']} ({result['key']})")
                    print(f"   Printable ratio: {result['analysis']['printable_ratio']:.1%}")
                    if result["analysis"]["patterns"]:
                        print(f"   Patterns found: {result['analysis']['patterns']}")
                    print(f"   Text: {result['analysis']['printable_text']}")
                
                # Try multi-layer decryption with the transaction fields
                try_multi_layer_decryption(hex_string, tx_fields)
            
    except Exception as e:
        print(f"Error processing transaction data: {e}")

def analyze_byte_frequencies(hex_string):
    """Analyze frequency of bytes for patterns."""
    print("\n=== BYTE FREQUENCY ANALYSIS ===")
    
    bytes_data = hex_to_bytes(hex_string)
    if not bytes_data:
        return
    
    # Count frequency of each byte
    freq = {}
    for b in bytes_data:
        freq[b] = freq.get(b, 0) + 1
    
    # Get top 10 most frequent bytes
    top_bytes = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
    print("Most frequent bytes:")
    for b, count in top_bytes:
        print(f"0x{b:02x} ({chr(b) if 32 <= b < 127 else '.'}) - {count} occurrences ({count/len(bytes_data):.2%})")
    
    # Check for ASCII bias
    ascii_count = sum(1 for b in bytes_data if 32 <= b < 127)
    ascii_ratio = ascii_count / len(bytes_data)
    print(f"ASCII character ratio: {ascii_ratio:.2%}")
    
    if ascii_ratio > 0.7:
        print("High ASCII ratio suggests text data")
    elif ascii_ratio < 0.3:
        print("Low ASCII ratio suggests binary/encrypted data")

def try_complete_hex_string(hex_string):
    """Try to complete the hex string by testing various appended characters."""
    print("\n=== ATTEMPTING TO COMPLETE HEX STRING ===")
    
    if len(hex_string) % 2 == 0:
        print("Hex string already has an even length. No need to complete.")
        return hex_string
    
    # First, try appending characters (most common case)
    append_completions = []
    for char in "0123456789abcdef":
        test_hex = hex_string + char
        try:
            # Try to convert to bytes to validate
            bytes.fromhex(test_hex)
            append_completions.append((char, test_hex))
        except ValueError:
            continue
    
    if append_completions:
        print(f"Found {len(append_completions)} valid ways to complete the hex string by appending characters:")
        for i, (char, completed) in enumerate(append_completions):
            print(f"Option {i+1}: Append '{char}' -> {completed}")
        
        # Default to the first valid completion
        print(f"\nUsing first valid completion (append '{append_completions[0][0]}') for further analysis.")
        return append_completions[0][1]
    
    # If appending doesn't work, try inserting characters at each possible position
    print("Trying to insert characters at different positions...")
    insert_completions = []
    
    for pos in range(len(hex_string) + 1):
        for char in "0123456789abcdef":
            test_hex = hex_string[:pos] + char + hex_string[pos:]
            try:
                # Try to convert to bytes to validate
                bytes.fromhex(test_hex)
                insert_completions.append((pos, char, test_hex))
            except ValueError:
                continue
    
    if insert_completions:
        print(f"Found {len(insert_completions)} valid ways to complete the hex string by inserting characters:")
        for i, (pos, char, completed) in enumerate(insert_completions[:10]):  # Show only first 10 for brevity
            prefix = completed[:pos]
            inserted = completed[pos]
            suffix = completed[pos+1:]
            print(f"Option {i+1}: Insert '{char}' at position {pos} -> {prefix}[{inserted}]{suffix}")
        
        if len(insert_completions) > 10:
            print(f"... and {len(insert_completions) - 10} more options.")
        
        # Default to the first valid completion
        print(f"\nUsing first valid completion (insert '{insert_completions[0][1]}' at position {insert_completions[0][0]}) for further analysis.")
        return insert_completions[0][2]
    
    print("Could not find a valid way to complete the hex string.")
    return hex_string

def try_every_hex_digit(hex_string):
    """Try inserting every hex digit at every position to see if the resulting string becomes valid."""
    print("\n=== SYSTEMATIC CHARACTER INSERTION ===")
    
    if len(hex_string) % 2 == 0:
        print("Hex string already has an even length. No need to insert characters.")
        return hex_string, []
    
    valid_insertions = []
    hex_digits = "0123456789abcdef"
    
    # Try inserting at each position
    for pos in range(len(hex_string) + 1):
        for digit in hex_digits:
            test_string = hex_string[:pos] + digit + hex_string[pos:]
            try:
                # Check if valid hex
                bytes.fromhex(test_string)
                valid_insertions.append((pos, digit, test_string))
                print(f"Valid insertion: '{digit}' at position {pos}")
            except ValueError:
                continue
    
    if valid_insertions:
        sorted_insertions = sorted(valid_insertions, key=lambda x: x[0])
        print(f"Total valid insertions found: {len(valid_insertions)}")
        return sorted_insertions[0][2], sorted_insertions
    else:
        print("No valid character insertions found")
        return hex_string, []

def analyze_hex_string(hex_string):
    """Analyze a hex string for potential Bitcoin-related patterns."""
    print(f"Analyzing hex string: {hex_string}")
    print(f"Length: {len(hex_string)} characters ({len(hex_string)//2} bytes)")
    
    # Clean the hex string
    hex_string = hex_string.strip().lower()
    
    # Try basic conversions
    print("\n=== BASIC CONVERSIONS ===")
    bytes_data = hex_to_bytes(hex_string)
    if bytes_data:
        print(f"As UTF-8 (printable only): {display_printable(bytes_data)}")
        print(f"As Base64: {base64.b64encode(bytes_data).decode('utf-8')}")
    
    # Try different analyses
    analyze_as_tx_hash(hex_string)
    analyze_as_private_key(hex_string)
    analyze_as_script(hex_string)
    analyze_as_tx_structure(hex_string)
    analyze_as_bip39_seed(hex_string)
    analyze_as_wallet_import_format(hex_string)
    analyze_byte_frequencies(hex_string)
    entropy_analysis(hex_string)
    bit_pattern_analysis(hex_string)
    try_various_xor_keys(hex_string)
    
    # Try using transaction data for decoding
    try_tx_data_fields(hex_string)
    
    print("\n=== ANALYSIS COMPLETE ===")
    print("Notes:")
    print("1. XOR, Vigenère, and other decoding methods have been applied to search for hidden patterns.")
    print("2. The entropy analysis suggests this data could be encrypted or encoded with structured information.")
    print("3. Transaction data from term 68 has been used as potential decryption keys.")
    print("4. Consider inspecting any promising decoded outputs for Bitcoin addresses, URLs, or messages.")

if __name__ == "__main__":
    original_hex_string = "925f94cd6e13cb4fa50400050664458b371cc56a324b4d1e38e27305badbef1582c32d061820081b6f1172c9937f4eafd7cb7d2f2e4b2f95e23beafd2197e0"
    print(f"Original hex string: {original_hex_string}")
    print(f"Length: {len(original_hex_string)} characters ({len(original_hex_string)//2} bytes)")
    
    # Validate hex string length
    if len(original_hex_string) % 2 != 0:
        print(f"WARNING: Hex string has an odd length ({len(original_hex_string)} characters), which is unusual.")
        print("Each byte should be represented by 2 hex characters. There might be a missing character.")
        
        # Try to complete the hex string
        completed_hex_string, all_valid_insertions = try_every_hex_digit(original_hex_string)
        
        if completed_hex_string != original_hex_string:
            print(f"\nProceeding with completed hex string: {completed_hex_string}")
            hex_string = completed_hex_string
        else:
            print("Could not automatically fix the odd-length hex string.")
            # Try a different approach - append '0' as a last resort
            hex_string = original_hex_string + '0'
            print(f"Using hex string with appended '0' as fallback: {hex_string}")
    else:
        hex_string = original_hex_string
    
    analyze_hex_string(hex_string) 