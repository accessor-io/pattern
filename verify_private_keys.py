#!/usr/bin/env python3

import os
import sys
import hashlib
import base58
import binascii
import ecdsa
from typing import Dict, List, Tuple, Optional

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_known_keys() -> Dict[int, int]:
    """Load the known keys from the module"""
    try:
        from solvers.archive.known_keys import KNOWN_KEYS
        return KNOWN_KEYS
    except Exception as e:
        print(f"Error loading KNOWN_KEYS: {e}")
        return {}

def private_key_to_wif(private_key: int, compressed: bool = True, testnet: bool = False) -> str:
    """Convert private key to WIF format"""
    # Convert the private key to a byte array of length 32
    private_key_bytes = private_key.to_bytes(32, byteorder='big')
    
    # Add version byte (0x80 for mainnet, 0xEF for testnet)
    prefix = b'\xEF' if testnet else b'\x80'
    
    # Add compression flag if needed
    suffix = b'\x01' if compressed else b''
    
    # Create the format to be encoded (version + private key + compression flag)
    to_encode = prefix + private_key_bytes + suffix
    
    # Double SHA-256 hash
    first_sha = hashlib.sha256(to_encode).digest()
    second_sha = hashlib.sha256(first_sha).digest()
    
    # Take the first 4 bytes as checksum
    checksum = second_sha[:4]
    
    # Add checksum to the end
    to_encode_with_checksum = to_encode + checksum
    
    # Base58 encode
    wif = base58.b58encode(to_encode_with_checksum).decode('utf-8')
    
    return wif

def private_key_to_public_key(private_key: int, compressed: bool = True) -> bytes:
    """Generate public key from private key using ECDSA"""
    try:
        # Convert to bytes
        private_key_bytes = private_key.to_bytes(32, byteorder='big')
        
        # Use ECDSA to get the public key
        sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        
        if compressed:
            # Compressed public key format (33 bytes)
            x_coord = vk.pubkey.point.x()
            y_coord = vk.pubkey.point.y()
            if y_coord % 2 == 0:  # Even y
                return b'\x02' + x_coord.to_bytes(32, byteorder='big')
            else:  # Odd y
                return b'\x03' + x_coord.to_bytes(32, byteorder='big')
        else:
            # Uncompressed public key format (65 bytes)
            return b'\x04' + vk.to_string()
    except Exception as e:
        print(f"Error generating public key: {e}")
        # Return a dummy value for testing
        if compressed:
            return b'\x02' + b'\x00'*32
        else:
            return b'\x04' + b'\x00'*64

def public_key_to_address(public_key: bytes, testnet: bool = False) -> str:
    """Convert public key to Bitcoin address"""
    # SHA-256 hash
    sha256_hash = hashlib.sha256(public_key).digest()
    
    # RIPEMD-160 hash
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_hash)
    hash160 = ripemd160.digest()
    
    # Add version byte (0x00 for mainnet, 0x6F for testnet)
    version_byte = b'\x6F' if testnet else b'\x00'
    network_hash160 = version_byte + hash160
    
    # Double SHA-256 hash for checksum
    first_sha = hashlib.sha256(network_hash160).digest()
    second_sha = hashlib.sha256(first_sha).digest()
    
    # Take the first 4 bytes as checksum
    checksum = second_sha[:4]
    
    # Combine version, hash160, and checksum
    binary_address = network_hash160 + checksum
    
    # Base58 encode
    address = base58.b58encode(binary_address).decode('utf-8')
    
    return address

def verify_private_key_candidates():
    """Verify candidate private keys by generating addresses and comparing to expected"""
    known_keys = load_known_keys()
    if not known_keys:
        print("Failed to load known keys. Cannot verify.")
        return

    # Load candidate private keys from file
    candidates = []
    try:
        with open("derived_private_keys.txt", "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split(" -> ")
                if len(parts) != 2:
                    continue
                
                private_key_str, key_info = parts
                
                # Extract key index
                if "Key " in key_info:
                    try:
                        key_index = int(key_info.split("Key ")[1].split(" ")[0])
                        private_key_int = int(private_key_str)
                        candidates.append((key_index, private_key_int, key_info))
                    except:
                        pass
    except Exception as e:
        print(f"Error loading candidate private keys: {e}")
        return

    print(f"Loaded {len(candidates)} candidate private keys")
    
    # Verify each candidate
    matches = []
    for key_index, private_key, key_info in candidates:
        try:
            # Generate public key (compressed)
            public_key = private_key_to_public_key(private_key, compressed=True)
            
            # Generate Bitcoin address
            address = public_key_to_address(public_key)
            
            # Print details for the first few keys
            if len(matches) < 5:
                print(f"\nKey {key_index}:")
                print(f"  Private Key: {private_key} (0x{private_key:x})")
                print(f"  Public Key: {public_key.hex()}")
                print(f"  Address: {address}")
                
                # Get WIF format for the private key
                wif = private_key_to_wif(private_key)
                print(f"  WIF: {wif}")
                
                # Compare with the known key
                if key_index in known_keys:
                    known_key = known_keys[key_index]
                    print(f"  Known key value: 0x{known_key:x}")
                    print(f"  Matches known key: {private_key == known_key}")
                    
                    if private_key == known_key:
                        matches.append((key_index, private_key, address))
                        print("  ✓ VERIFIED: Private key matches known key!")
                    else:
                        print("  ✗ NOT VERIFIED: Private key does not match known key")
        except Exception as e:
            print(f"Error verifying key {key_index}: {e}")
    
    # Summarize matches
    if matches:
        print(f"\nFound {len(matches)} private keys that match known keys:")
        for key_index, private_key, address in matches:
            print(f"Key {key_index}: {private_key} -> {address}")
    else:
        print("\nNo matching private keys found.")
        print("This suggests that:")
        print("1. The private keys are not directly derivable from the patterns we tried")
        print("2. There might be an additional transformation or encryption step")
        print("3. The puzzle may require specialized cryptographic knowledge")
        print("4. The bit patterns we observed might be hints rather than direct keys")

def generate_target_address():
    """Generate and verify the hidden Bitcoin address we're looking for"""
    # Our discovered address with corrected checksum
    target_address = "1CZqucvN1wZ4Gwq95dsNgj1xVjUcK3pcMQ"
    
    try:
        # Verify it decodes correctly
        decoded = base58.b58decode(target_address)
        if len(decoded) == 25:
            version = decoded[0]
            hash160 = decoded[1:21]
            checksum = decoded[21:25]
            
            # Calculate checksum
            payload = decoded[:21]
            calculated_checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
            
            print("\nTarget Bitcoin Address Analysis:")
            print(f"Address: {target_address}")
            print(f"Version: {version}")
            print(f"Hash160: {hash160.hex()}")
            print(f"Checksum: {checksum.hex()}")
            print(f"Calculated checksum: {calculated_checksum.hex()}")
            print(f"Checksum valid: {checksum == calculated_checksum}")
            
            # Now try to find a private key that generates this hash160
            print("\nSearching for a private key that generates this address...")
            print("(Note: This is computationally infeasible without additional clues)")
            print("Trying a small sample of keys as a demonstration...")
            
            # Try a small range to demonstrate the approach
            for test_key in range(1, 100):
                public_key = private_key_to_public_key(test_key, compressed=True)
                test_address = public_key_to_address(public_key)
                
                # Compare the hash160 part
                test_decoded = base58.b58decode(test_address)
                test_hash160 = test_decoded[1:21]
                
                if test_hash160 == hash160:
                    print(f"Found match! Private key: {test_key}")
                    return
            
            print("No match found in the sample range.")
    except Exception as e:
        print(f"Error analyzing target address: {e}")

if __name__ == "__main__":
    print("Bitcoin Private Key Verification Tool")
    print("====================================")
    
    # Install required packages if they don't exist
    try:
        import ecdsa
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.call([sys.executable, "-m", "pip", "install", "ecdsa"])
        import ecdsa
    
    try:
        import base58
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.call([sys.executable, "-m", "pip", "install", "base58"])
        import base58
    
    verify_private_key_candidates()
    generate_target_address() 