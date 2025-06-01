import base64
import hashlib
import requests
import json
import os.path
import re

# Step 1: Convert Hexadecimal to Bytes
def hex_to_bytes(hex_string):
    # Check for non-hexadecimal characters
    invalid_chars = [char for char in hex_string if char not in "0123456789abcdefABCDEF"]
    if invalid_chars:
        print(f"Invalid characters found: {invalid_chars}")
        return None

    try:
        return bytes.fromhex(hex_string)
    except ValueError as e:
        print(f"Error converting hex to bytes: {e}")
        return None

# Step 2: Base64 Decoding
def base64_decode(data):
    try:
        return base64.b64decode(data)
    except Exception as e:
        print(f"Error decoding Base64: {e}")
        return None

# Step 3: XOR Decryption with Key
def xor_decrypt(data, key="KONAMI"):
    key_bytes = key.encode('utf-8')
    return bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data)])

# Step 4: Vigenère Cipher Decryption
def vigenere_decrypt(text, key="KONAMI"):
    decrypted = []
    key_length = len(key)
    key_int = [ord(i) for i in key]
    for i, char in enumerate(text):
        value = (ord(char) - key_int[i % key_length]) % 256
        decrypted.append(chr(value))
    return ''.join(decrypted)

# Step 5: ROT47 Transformation
def rot47(s):
    result = []
    for char in s:
        ascii_val = ord(char)
        if 33 <= ascii_val <= 126:
            result.append(chr(33 + ((ascii_val + 14) % 94)))
        else:
            result.append(char)
    return ''.join(result)

# Helper function to display only printable characters
def display_printable(data):
    if isinstance(data, bytes):
        # Convert bytes to string
        text = data.decode('latin-1', errors='ignore')
    else:
        text = data
    
    result = []
    for char in text:
        if 32 <= ord(char) <= 126:
            result.append(char)
        else:
            result.append('.')
    return ''.join(result)

def find_invalid_hex_char(hex_string):
    for i, char in enumerate(hex_string):
        if char not in "0123456789abcdefABCDEF":
            return i, char
    return None, None

# Main Solver Function - Original approach
def solve_puzzle(hex_string):
    # Find and correct invalid characters
    index, invalid_char = find_invalid_hex_char(hex_string)
    if invalid_char:
        print(f"Invalid character '{invalid_char}' found at position {index}.")
        # Correct the invalid character (e.g., replace with '0')
        hex_string = hex_string[:index] + '0' + hex_string[index+1:]
        print(f"Corrected hex string: {hex_string}")

    # Convert hex to bytes
    bytes_data = hex_to_bytes(hex_string)
    if not bytes_data:
        print("Failed to convert hex to bytes.")
        return
    print("Hex to Bytes:", bytes_data)

    # Base64 decode (if applicable)
    base64_decoded = base64_decode(bytes_data)
    if base64_decoded:
        bytes_data = base64_decoded
        print("Base64 Decoded:", bytes_data)

    # XOR decryption
    xor_decrypted = xor_decrypt(bytes_data)
    print("XOR Decrypted:", xor_decrypted)
    print("XOR Decrypted (Printable Only):", display_printable(xor_decrypted))

    # Vigenère decryption
    vigenere_decrypted = vigenere_decrypt(xor_decrypted.decode('latin-1', errors='ignore'))
    print("Vigenère Decrypted:", vigenere_decrypted)
    print("Vigenère Decrypted (Printable Only):", display_printable(vigenere_decrypted))

    # ROT47 transformation
    final_output = rot47(vigenere_decrypted)
    print("Final ROT47 Decrypted Message:", final_output)
    print("Final ROT47 (Printable Only):", display_printable(final_output))

# Alternative approach: Try different keys
def try_different_keys(hex_string):
    print("\n=== TRYING DIFFERENT KEYS ===")
    bytes_data = hex_to_bytes(hex_string)
    if not bytes_data:
        print("Failed to convert hex to bytes.")
        return
    
    alternative_keys = ["NINTENDO", "SEGA", "CAPCOM", "ATARI", "NAMCO"]
    
    for key in alternative_keys:
        print(f"\nUsing Key: {key}")
        # XOR decryption
        xor_decrypted = xor_decrypt(bytes_data, key)
        print(f"XOR with {key} (Printable Only):", display_printable(xor_decrypted))
        
        # Vigenère decryption
        vigenere_decrypted = vigenere_decrypt(xor_decrypted.decode('latin-1', errors='ignore'), key)
        print(f"Vigenère with {key} (Printable Only):", display_printable(vigenere_decrypted))
        
        # ROT47 transformation
        final_output = rot47(vigenere_decrypted)
        print(f"ROT47 with {key} (Printable Only):", display_printable(final_output))

# Alternative approach: Try different order of operations
def try_different_order(hex_string):
    print("\n=== TRYING DIFFERENT ORDER OF OPERATIONS ===")
    bytes_data = hex_to_bytes(hex_string)
    if not bytes_data:
        print("Failed to convert hex to bytes.")
        return
    
    # 1. Vigenère -> XOR -> ROT47
    print("\nOrder: Vigenère -> XOR -> ROT47")
    str_data = bytes_data.decode('latin-1', errors='ignore')
    vigenere_first = vigenere_decrypt(str_data)
    xor_second = xor_decrypt(vigenere_first.encode('latin-1'))
    rot47_third = rot47(xor_second.decode('latin-1', errors='ignore'))
    print("Result (Printable Only):", display_printable(rot47_third))
    
    # 2. ROT47 -> XOR -> Vigenère
    print("\nOrder: ROT47 -> XOR -> Vigenère")
    str_data = bytes_data.decode('latin-1', errors='ignore')
    rot47_first = rot47(str_data)
    xor_second = xor_decrypt(rot47_first.encode('latin-1'))
    vigenere_third = vigenere_decrypt(xor_second.decode('latin-1', errors='ignore'))
    print("Result (Printable Only):", display_printable(vigenere_third))

# Try to detect file signatures or patterns
def analyze_as_binary(hex_string):
    print("\n=== ANALYZING AS BINARY DATA ===")
    bytes_data = hex_to_bytes(hex_string)
    if not bytes_data:
        print("Failed to convert hex to bytes.")
        return
    
    # Check for common file signatures
    signatures = {
        b'PK\x03\x04': 'ZIP archive',
        b'\x89PNG': 'PNG image',
        b'GIF8': 'GIF image',
        b'\xFF\xD8\xFF': 'JPEG image',
        b'%PDF': 'PDF document',
        b'BM': 'BMP image',
        b'\x7FELF': 'ELF executable',
        b'MZ': 'Windows executable',
        b'ID3': 'MP3 audio with ID3 tag'
    }
    
    for sig, desc in signatures.items():
        if bytes_data.startswith(sig):
            print(f"Detected file signature: {desc}")
            return
    
    # If no file signature detected, check for ASCII representation
    try:
        ascii_text = bytes_data.decode('ascii', errors='ignore')
        printable_ascii = ''.join(c for c in ascii_text if c.isprintable())
        if len(printable_ascii) > len(ascii_text) * 0.7:  # If more than 70% is printable
            print("Data appears to be ASCII text:")
            print(printable_ascii[:100])  # Show first 100 chars
        else:
            print("Data appears to be binary with no recognizable file signature.")
    except Exception as e:
        print(f"Error during ASCII analysis: {e}")

# Try to decode using Bitcoin transaction data
def try_bitcoin_tx_decode(hex_string):
    print("\n=== TRYING BITCOIN TRANSACTION-BASED DECODING ===")
    bytes_data = hex_to_bytes(hex_string)
    if not bytes_data:
        print("Failed to convert hex to bytes.")
        return
    
    # Function to fetch transaction data from a local txcache file or blockchain API
    def get_tx_data(tx_hash):
        # Try to read from local txcache file first
        cache_file = os.path.join('txcache', f"{tx_hash}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading txcache file: {e}")
        
        # If local cache doesn't exist, try using a blockchain API
        try:
            response = requests.get(f"https://blockchain.info/rawtx/{tx_hash}?format=json")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching transaction data: {e}")
        
        return None
    
    # Try to extract a potential Bitcoin transaction hash from the data
    # A Bitcoin tx hash is 32 bytes (64 hex chars) - let's look for potential hashes
    # in the data or its decoded forms
    
    # 1. Try to interpret first 32 bytes as a transaction hash
    potential_tx_hash = bytes_data[:32].hex()
    print(f"Potential transaction hash: {potential_tx_hash}")
    tx_data = get_tx_data(potential_tx_hash)
    
    if tx_data:
        print(f"Found transaction data for hash {potential_tx_hash}")
        
        # Try using various transaction fields as decryption keys
        tx_fields = {
            "txid": tx_data.get("hash", ""),
            "blockheight": str(tx_data.get("block_height", "")),
            "timestamp": str(tx_data.get("time", "")),
            "inputs": "_".join([inp.get("prev_out", {}).get("addr", "") for inp in tx_data.get("inputs", [])])[:20],
            "outputs": "_".join([out.get("addr", "") for out in tx_data.get("out", [])])[:20]
        }
        
        for field_name, key in tx_fields.items():
            if not key:
                continue
                
            print(f"\nTrying key from transaction {field_name}: {key}")
            
            # Try XOR with this key
            try:
                tx_xor_decrypted = xor_decrypt(bytes_data, key)
                print(f"XOR with {field_name} (Printable Only):", display_printable(tx_xor_decrypted))
                
                # Try further decoding
                tx_vig_decrypted = vigenere_decrypt(tx_xor_decrypted.decode('latin-1', errors='ignore'), key)
                print(f"Vigenère with {field_name} (Printable Only):", display_printable(tx_vig_decrypted))
                
                # ROT47
                tx_rot_output = rot47(tx_vig_decrypted)
                print(f"ROT47 with {field_name} (Printable Only):", display_printable(tx_rot_output))
            except Exception as e:
                print(f"Error using {field_name} as key: {e}")
    else:
        print("No transaction data found for the potential hash.")
        
        # Try another approach - use the data as input to various hashing functions
        # and check if the result matches known Bitcoin tx hashes
        
        print("\nTrying to derive transaction hash from the data...")
        hash_funcs = {
            "sha256": hashlib.sha256,
            "double_sha256": lambda x: hashlib.sha256(hashlib.sha256(x).digest()).digest(),
            "ripemd160": lambda x: hashlib.new('ripemd160', x).digest(),
        }
        
        for hash_name, hash_func in hash_funcs.items():
            try:
                derived_hash = hash_func(bytes_data).hex()
                print(f"{hash_name.upper()}: {derived_hash}")
                
                # Try to fetch transaction data for this hash
                tx_data = get_tx_data(derived_hash)
                if tx_data:
                    print(f"Found transaction data for derived {hash_name} hash: {derived_hash}")
                    # Process the transaction data as above
            except Exception as e:
                print(f"Error calculating {hash_name}: {e}")
    
    # Final approach - try scanning the data for OP_RETURN messages
    # OP_RETURN outputs in Bitcoin transactions can contain messages
    print("\nScanning for potential OP_RETURN message patterns...")
    try:
        # Look for common OP_RETURN indicators in the binary data
        op_return_indicators = [b'\x6a', b'OP_RETURN', b'message']
        for indicator in op_return_indicators:
            pos = bytes_data.find(indicator)
            if pos >= 0:
                # Found a potential OP_RETURN indicator, extract following data
                potential_message = bytes_data[pos + len(indicator):pos + len(indicator) + 80]
                print(f"Potential OP_RETURN message found at offset {pos}: {potential_message}")
                print(f"As text: {potential_message.decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"Error scanning for OP_RETURN patterns: {e}")

# Use specific transaction data for decoding
def try_target_tx_decode(hex_string):
    print("\n=== TRYING TARGET TRANSACTION DECODING ===")
    bytes_data = hex_to_bytes(hex_string)
    if not bytes_data:
        print("Failed to convert hex to bytes.")
        return
    
    # Load the specific transaction file for term 68
    tx_file = './tx_cache/1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ.json'
    
    try:
        with open(tx_file, 'r') as f:
            tx_data = json.load(f)
            print(f"Successfully loaded transaction data from {tx_file}")
            
            # Extract various pieces of data from the transaction that might be used as keys
            if isinstance(tx_data, dict):
                # Single transaction
                tx_fields = {
                    "txid": tx_data.get("hash", ""),
                    "version": str(tx_data.get("ver", "")),
                    "blockheight": str(tx_data.get("block_height", "")),
                    "timestamp": str(tx_data.get("time", "")),
                }
                
                # Add input and output addresses if available
                if "inputs" in tx_data:
                    input_addrs = []
                    for inp in tx_data.get("inputs", []):
                        if "prev_out" in inp and "addr" in inp["prev_out"]:
                            input_addrs.append(inp["prev_out"]["addr"])
                    if input_addrs:
                        tx_fields["input_addr"] = input_addrs[0]  # Just use the first one as a key
                
                if "out" in tx_data:
                    output_addrs = []
                    for out in tx_data.get("out", []):
                        if "addr" in out:
                            output_addrs.append(out["addr"])
                    if output_addrs:
                        tx_fields["output_addr"] = output_addrs[0]  # Just use the first one as a key
            
            elif isinstance(tx_data, list) and len(tx_data) > 0:
                # List of transactions, use the first one
                tx = tx_data[0]
                tx_fields = {
                    "txid": tx.get("hash", ""),
                    "version": str(tx.get("ver", "")),
                    "blockheight": str(tx.get("block_height", "")),
                    "timestamp": str(tx.get("time", "")),
                }
                
                # Add input and output addresses if available
                if "inputs" in tx:
                    input_addrs = []
                    for inp in tx.get("inputs", []):
                        if "prev_out" in inp and "addr" in inp["prev_out"]:
                            input_addrs.append(inp["prev_out"]["addr"])
                    if input_addrs:
                        tx_fields["input_addr"] = input_addrs[0]  # Just use the first one as a key
                
                if "out" in tx:
                    output_addrs = []
                    for out in tx.get("out", []):
                        if "addr" in out:
                            output_addrs.append(out["addr"])
                    if output_addrs:
                        tx_fields["output_addr"] = output_addrs[0]  # Just use the first one as a key
            
            # Try using each field as a key for decryption
            for field_name, key in tx_fields.items():
                if not key:
                    continue
                    
                print(f"\nTrying key from transaction {field_name}: {key}")
                
                # Try XOR with this key
                try:
                    tx_xor_decrypted = xor_decrypt(bytes_data, key)
                    print(f"XOR with {field_name} (Printable Only):", display_printable(tx_xor_decrypted))
                    
                    # Try further decoding
                    tx_vig_decrypted = vigenere_decrypt(tx_xor_decrypted.decode('latin-1', errors='ignore'), key)
                    print(f"Vigenère with {field_name} (Printable Only):", display_printable(tx_vig_decrypted))
                    
                    # ROT47
                    tx_rot_output = rot47(tx_vig_decrypted)
                    print(f"ROT47 with {field_name} (Printable Only):", display_printable(tx_rot_output))
                except Exception as e:
                    print(f"Error using {field_name} as key: {e}")
            
            # Try using the transaction itself as the data to decode, rather than the key
            print("\nTrying to decode transaction data itself...")
            # Extract the raw transaction hex
            tx_hex = tx_data.get("hex", "")
            if tx_hex:
                print(f"Transaction hex found, length: {len(tx_hex)}")
                tx_bytes = bytes.fromhex(tx_hex)
                
                # Try common keys
                common_keys = ["KONAMI", "NINTENDO", "SEGA", "BITCOIN", "SATOSHI", "NAKAMOTO"]
                for key in common_keys:
                    print(f"\nDecoding transaction data with key: {key}")
                    
                    try:
                        tx_xor_decrypted = xor_decrypt(tx_bytes, key)
                        print(f"XOR Transaction with {key} (First 100 chars):", display_printable(tx_xor_decrypted)[:100])
                        
                        # Try looking for messages in the decrypted data
                        printable_chars = display_printable(tx_xor_decrypted)
                        # Look for sequences of printable characters (potential messages)
                        message_candidates = re.findall(r'[A-Za-z0-9\s.,!?;:\'\"]{5,}', printable_chars)
                        if message_candidates:
                            print("Potential messages found in transaction data:")
                            for msg in message_candidates[:5]:  # Show up to 5 candidates
                                print(f"  - {msg}")
                    except Exception as e:
                        print(f"Error decoding transaction with {key}: {e}")
            else:
                print("No transaction hex found to decode.")
                
    except Exception as e:
        print(f"Error processing transaction file: {e}")

# Main execution
if __name__ == "__main__":
    hex_string = "925f94cd6e13cb4fa50400050664458b371cc56a324b4d1e38e27305badbef1582c32d061820081b6f1172c9937f4eafd7cb7d2f2e4b2f95e23beafd2197e0"
    
    # Use just the target transaction decode to focus on this approach
    try_target_tx_decode(hex_string)