#!/usr/bin/env python3
import hashlib
import binascii
import base58
import hmac
import json

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

def wif_to_private_key(wif):
    """Convert a WIF private key back to the original hex private key."""
    try:
        # Decode the Base58Check encoding
        decoded = base58.b58decode_check(wif)
        
        # Remove network byte (first byte) and compression flag (last byte, if present)
        if len(decoded) == 34:  # Compressed private key (with compression flag)
            private_key = decoded[1:-1]
        else:  # Uncompressed private key
            private_key = decoded[1:]
        
        return private_key.hex()
    except Exception as e:
        print(f"Error decoding WIF: {e}")
        return None

def private_key_to_wif(private_key_hex, compressed=False, testnet=False):
    """Convert a private key hex to WIF format."""
    try:
        # Convert hex string to bytes
        private_key_bytes = bytes.fromhex(private_key_hex)
        
        # Add network byte (0x80 for mainnet, 0xEF for testnet)
        network_byte = b'\xEF' if testnet else b'\x80'
        extended_key = network_byte + private_key_bytes
        
        # Add compression flag if needed
        if compressed:
            extended_key += b'\x01'
        
        # Double SHA-256 for checksum
        checksum = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()[:4]
        
        # Append checksum
        wif_bytes = extended_key + checksum
        
        # Encode with Base58
        wif = base58.b58encode(wif_bytes)
        
        return wif.decode('ascii')
    except Exception as e:
        print(f"Error creating WIF: {e}")
        return None

def calculate_bitcoin_address(private_key_hex, compressed=True):
    """Calculate the Bitcoin address from a private key hex."""
    try:
        # Import libraries here to deal with potential import issues
        try:
            from ecdsa import SigningKey, SECP256k1
            import hashlib
            import base58
        except ImportError:
            print("Please install required libraries: pip install ecdsa base58")
            return None
        
        # Convert hex to bytes
        private_key_bytes = bytes.fromhex(private_key_hex)
        
        # Get public key
        signing_key = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        verifying_key = signing_key.get_verifying_key()
        
        # Convert public key to bytes
        if compressed:
            if verifying_key.pubkey.point.y() % 2 == 0:
                public_key_bytes = b'\x02' + verifying_key.pubkey.point.x().to_bytes(32, 'big')
            else:
                public_key_bytes = b'\x03' + verifying_key.pubkey.point.x().to_bytes(32, 'big')
        else:
            public_key_bytes = b'\x04' + verifying_key.pubkey.point.x().to_bytes(32, 'big') + \
                              verifying_key.pubkey.point.y().to_bytes(32, 'big')
        
        # Hash the public key
        sha256_hash = hashlib.sha256(public_key_bytes).digest()
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
        
        # Add version byte
        version_byte = b'\x00'  # Mainnet
        network_hash = version_byte + ripemd160_hash
        
        # Calculate checksum
        checksum = hashlib.sha256(hashlib.sha256(network_hash).digest()).digest()[:4]
        
        # Append checksum
        binary_address = network_hash + checksum
        
        # Encode with Base58
        address = base58.b58encode(binary_address)
        
        return address.decode('ascii')
    except Exception as e:
        print(f"Error calculating Bitcoin address: {e}")
        return None

def check_hmac_signatures(hex_string):
    """Check for potential HMAC patterns in the hexadecimal string."""
    print("\n=== CHECKING HMAC SIGNATURES ===")
    
    bytes_data = hex_to_bytes(hex_string)
    if not bytes_data:
        return
    
    # Common keys to try
    keys = [
        "bitcoin", "satoshi", "nakamoto", "wallet", "key", "address", "transaction",
        "block", "hash", "private", "public", "signature", "term68", "puzzle",
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"
    ]
    
    results = []
    
    for key in keys:
        key_bytes = key.encode('utf-8')
        
        # Calculate HMAC-SHA256
        hmac_result = hmac.new(key_bytes, bytes_data, hashlib.sha256).hexdigest()
        
        # Check if the result looks like a Bitcoin private key or address
        # (Example check: private keys are 64 hex characters, addresses start with 1)
        if len(hmac_result) == 64:
            # Check if this could generate a valid Bitcoin address
            try:
                wif = private_key_to_wif(hmac_result)
                print(f"Key: '{key}' -> HMAC-SHA256 potential private key: {hmac_result}")
                print(f"  WIF: {wif}")
                
                # Try calculating the address (will require external libraries)
                address = calculate_bitcoin_address(hmac_result)
                if address:
                    print(f"  Bitcoin address: {address}")
                
                results.append({
                    "key": key,
                    "hmac_result": hmac_result,
                    "wif": wif,
                    "address": address
                })
            except Exception as e:
                pass
    
    return results

def analyze_offsets(hex_string):
    """Analyze the hex string at different offsets to find valid Bitcoin keys."""
    print("\n=== ANALYZING POTENTIAL KEYS AT DIFFERENT OFFSETS ===")
    
    bytes_data = hex_to_bytes(hex_string)
    if not bytes_data:
        return
    
    # Try different offsets to extract 32-byte chunks
    results = []
    
    for offset in range(0, len(bytes_data) - 32 + 1):
        key_bytes = bytes_data[offset:offset+32]
        key_hex = key_bytes.hex()
        
        try:
            # Convert to WIF
            wif = private_key_to_wif(key_hex)
            if wif:
                print(f"Offset {offset}: Potential private key: {key_hex}")
                print(f"  WIF: {wif}")
                
                # Try to calculate address
                address = calculate_bitcoin_address(key_hex)
                if address:
                    print(f"  Bitcoin address: {address}")
                    
                    # Check if the address is known for term 68
                    term68_address = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"
                    if address == term68_address:
                        print(f"  !!! MATCH: Term 68 address !!!")
                    
                    # Save this result
                    results.append({
                        "offset": offset,
                        "private_key": key_hex,
                        "wif": wif,
                        "address": address,
                        "is_term68_match": address == term68_address
                    })
        except Exception as e:
            # Skip errors and continue
            pass
    
    return results

def try_xor_combinations(hex_string):
    """Try XOR combinations that might yield a valid private key."""
    print("\n=== TRYING XOR COMBINATIONS FOR PRIVATE KEYS ===")
    
    bytes_data = hex_to_bytes(hex_string)
    if not bytes_data:
        return
    
    # Common XOR keys to try
    xor_keys = [
        "bitcoin", "satoshi", "nakamoto", "wallet", "key", "address", "transaction",
        "block", "hash", "private", "public", "signature", "term68", "puzzle"
    ]
    
    results = []
    
    for key in xor_keys:
        key_bytes = key.encode('utf-8')
        
        # Simple XOR (no byte repetition needed for a short key)
        xor_result = bytes(bytes_data[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(bytes_data)))
        
        # Extract 32-byte chunks at different offsets from the XOR result
        for offset in range(0, len(xor_result) - 32 + 1, 8):  # Step by 8 to reduce output
            potential_key = xor_result[offset:offset+32].hex()
            
            try:
                # Convert to WIF
                wif = private_key_to_wif(potential_key)
                if wif:
                    print(f"XOR with '{key}', Offset {offset}: {potential_key}")
                    print(f"  WIF: {wif}")
                    
                    # Try to calculate address
                    address = calculate_bitcoin_address(potential_key)
                    if address:
                        print(f"  Bitcoin address: {address}")
                        
                        # Check if the address is known for term 68
                        term68_address = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"
                        if address == term68_address:
                            print(f"  !!! MATCH: Term 68 address !!!")
                        
                        # Save this result
                        results.append({
                            "xor_key": key,
                            "offset": offset,
                            "private_key": potential_key,
                            "wif": wif,
                            "address": address,
                            "is_term68_match": address == term68_address
                        })
            except Exception as e:
                # Skip errors and continue
                pass
    
    return results

def check_hmac_variations(hex_string):
    """Check variations of HMAC with transaction data."""
    print("\n=== CHECKING HMAC VARIATIONS ===")
    
    # Load transaction data
    tx_file = './tx_cache/1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ.json'
    tx_fields = {}
    
    try:
        with open(tx_file, 'r') as f:
            tx_data = json.load(f)
            
            if isinstance(tx_data, dict) and "txs" in tx_data and tx_data["txs"]:
                tx = tx_data["txs"][0]
                
                # Extract key fields
                tx_fields = {
                    "txid": tx.get("txid", ""),
                    "version": str(tx.get("version", "")),
                    "locktime": str(tx.get("locktime", "")),
                }
                
                # Get input/output addresses
                if "vin" in tx and tx["vin"] and "prevout" in tx["vin"][0] and "scriptpubkey_address" in tx["vin"][0]["prevout"]:
                    tx_fields["input_addr"] = tx["vin"][0]["prevout"]["scriptpubkey_address"]
                
                if "vout" in tx and tx["vout"] and "scriptpubkey_address" in tx["vout"][0]:
                    tx_fields["output_addr"] = tx["vout"][0]["scriptpubkey_address"]
                    tx_fields["output_value"] = str(tx["vout"][0].get("value", ""))
    except Exception as e:
        print(f"Error loading transaction data: {e}")
    
    if not tx_fields:
        print("No transaction fields available for HMAC.")
        return []
    
    print("Transaction fields for HMAC:")
    for name, value in tx_fields.items():
        print(f"  {name}: {value}")
    
    bytes_data = hex_to_bytes(hex_string)
    if not bytes_data:
        return []
    
    results = []
    
    # Try HMAC with each field
    for field_name, field_value in tx_fields.items():
        if not field_value:
            continue
        
        key_bytes = field_value.encode('utf-8')
        
        # Calculate HMAC-SHA256
        hmac_result = hmac.new(key_bytes, bytes_data, hashlib.sha256).hexdigest()
        
        print(f"HMAC-SHA256 with '{field_name}': {hmac_result}")
        
        # Check if this looks like a private key
        try:
            wif = private_key_to_wif(hmac_result)
            print(f"  WIF: {wif}")
            
            # Try to calculate address
            address = calculate_bitcoin_address(hmac_result)
            if address:
                print(f"  Bitcoin address: {address}")
                
                # Check if the address is known for term 68
                term68_address = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"
                if address == term68_address:
                    print(f"  !!! MATCH: Term 68 address !!!")
                
                # Save this result
                results.append({
                    "field_name": field_name,
                    "field_value": field_value,
                    "hmac_result": hmac_result,
                    "wif": wif,
                    "address": address,
                    "is_term68_match": address == term68_address
                })
        except Exception as e:
            # Skip errors and continue
            pass
    
    return results

def main():
    # The original hex string
    hex_string = "925f94cd6e13cb4fa50400050664458b371cc56a324b4d1e38e27305badbef1582c32d061820081b6f1172c9937f4eafd7cb7d2f2e4b2f95e23beafd2197e0"
    
    # Add a '0' prefix and '1' suffix to create a 128-character string (as determined from previous analysis)
    padded_hex_string = "0" + hex_string + "1"
    
    print(f"Original hex string: {hex_string}")
    print(f"Padded hex string (128 chars): {padded_hex_string}")
    
    # Analyze the padded hex string
    hmac_results = check_hmac_signatures(padded_hex_string)
    offset_results = analyze_offsets(padded_hex_string)
    xor_results = try_xor_combinations(padded_hex_string)
    hmac_variation_results = check_hmac_variations(padded_hex_string)
    
    # Consolidate all results
    all_results = []
    if hmac_results:
        all_results.extend([{"type": "HMAC", **r} for r in hmac_results])
    if offset_results:
        all_results.extend([{"type": "Offset", **r} for r in offset_results])
    if xor_results:
        all_results.extend([{"type": "XOR", **r} for r in xor_results])
    if hmac_variation_results:
        all_results.extend([{"type": "HMAC Variation", **r} for r in hmac_variation_results])
    
    # Save all results to a JSON file
    if all_results:
        with open("potential_keys.json", "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"\nSaved {len(all_results)} potential keys to potential_keys.json")
    
    # Print summary
    print("\n=== ANALYSIS SUMMARY ===")
    print(f"Total potential keys found: {len(all_results)}")
    print(f"  HMAC signatures: {len(hmac_results) if hmac_results else 0}")
    print(f"  Offset analysis: {len(offset_results) if offset_results else 0}")
    print(f"  XOR combinations: {len(xor_results) if xor_results else 0}")
    print(f"  HMAC variations: {len(hmac_variation_results) if hmac_variation_results else 0}")
    
    # Check for any term 68 matches
    term68_matches = [r for r in all_results if r.get("is_term68_match", False)]
    if term68_matches:
        print("\n!!! FOUND TERM 68 MATCHES !!!")
        for match in term68_matches:
            print(f"Type: {match['type']}")
            print(f"Private Key: {match.get('private_key', match.get('hmac_result', ''))}")
            print(f"WIF: {match.get('wif', '')}")
            print(f"Address: {match.get('address', '')}")
    else:
        print("\nNo direct matches to the term 68 address were found.")
        print("The key might require additional transformations or combinatorial steps.")
    
    print("\nNotes:")
    print("1. The original hex string may be a piece of a larger puzzle or encryption system.")
    print("2. Consider exploring combinations with other known puzzle elements or clues.")
    print("3. Try checking other transaction-related data for further insights.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error in main execution: {e}")
        print("Note: This script requires the 'ecdsa' and 'base58' libraries for full functionality.")
        print("Install with: pip install ecdsa base58") 