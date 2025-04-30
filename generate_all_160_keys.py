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

def extend_key_pattern(known_keys: Dict[int, int], target_count: int = 160) -> Dict[int, int]:
    """Extend the key pattern to generate all 160 keys"""
    # Sort the known keys to analyze the pattern
    max_key_index = max(known_keys.keys())
    print(f"Maximum known key index: {max_key_index}")
    
    # Check if we need to generate more keys
    if max_key_index >= target_count:
        print(f"Already have {max_key_index} keys, which is >= target of {target_count}")
        return known_keys
    
    # Generate ratio patterns between consecutive keys to find the pattern
    ratios = []
    differences = []
    
    for i in range(max_key_index - 5, max_key_index):
        if i in known_keys and i+1 in known_keys:
            current = known_keys[i]
            next_key = known_keys[i+1]
            
            # Calculate ratio and difference
            ratio = next_key / current if current != 0 else 0
            diff = next_key - current
            
            ratios.append(ratio)
            differences.append(diff)
            
            print(f"Key {i} to {i+1}: {hex(current)} -> {hex(next_key)}")
            print(f"  Ratio: {ratio:.4f}, Difference: {diff}")
    
    # Use the patterns to generate more keys
    extended_keys = known_keys.copy()
    
    # Decide which pattern to use based on consistency
    ratio_consistency = len(set([round(r, 2) for r in ratios])) <= 2
    diff_consistency = len(set([d // 1000000 for d in differences])) <= 2
    
    if ratio_consistency and not diff_consistency:
        # Use ratio pattern (exponential growth)
        avg_ratio = sum(ratios) / len(ratios)
        print(f"Using ratio pattern with average ratio: {avg_ratio:.4f}")
        
        for i in range(max_key_index + 1, target_count + 1):
            prev_key = extended_keys[i-1]
            new_key = int(prev_key * avg_ratio)
            extended_keys[i] = new_key
            print(f"Generated key {i}: {hex(new_key)}")
            
    elif diff_consistency and not ratio_consistency:
        # Use difference pattern (linear growth)
        avg_diff = sum(differences) / len(differences)
        print(f"Using difference pattern with average difference: {avg_diff}")
        
        for i in range(max_key_index + 1, target_count + 1):
            prev_key = extended_keys[i-1]
            new_key = prev_key + int(avg_diff)
            extended_keys[i] = new_key
            print(f"Generated key {i}: {hex(new_key)}")
    else:
        # Try a more sophisticated pattern - check if it follows a Fibonacci-like pattern
        # where each new key depends on the previous two
        if max_key_index >= 3:
            patterns = []
            for i in range(3, max_key_index):
                if i-2 in known_keys and i-1 in known_keys and i in known_keys:
                    k1 = known_keys[i-2]
                    k2 = known_keys[i-1]
                    k3 = known_keys[i]
                    
                    # Check if k3 = a*k2 + b*k1 for some constants a and b
                    # We'll just check a simple case: k3 = k2 + k1 (Fibonacci)
                    if abs((k2 + k1) - k3) / k3 < 0.1:  # Within 10% of Fibonacci
                        patterns.append("fibonacci")
                        print(f"Key {i} follows approximate Fibonacci pattern")
                    else:
                        # Try other patterns: k3 = 2*k2 - k1 (linear extrapolation)
                        if abs((2*k2 - k1) - k3) / k3 < 0.1:
                            patterns.append("linear_extrap")
                            print(f"Key {i} follows linear extrapolation pattern")
            
            # Use the most common sophisticated pattern
            if patterns:
                most_common = max(set(patterns), key=patterns.count)
                print(f"Using sophisticated pattern: {most_common}")
                
                for i in range(max_key_index + 1, target_count + 1):
                    if i-2 in extended_keys and i-1 in extended_keys:
                        k1 = extended_keys[i-2]
                        k2 = extended_keys[i-1]
                        
                        if most_common == "fibonacci":
                            new_key = k1 + k2
                        elif most_common == "linear_extrap":
                            new_key = 2*k2 - k1
                        else:
                            # Default to exponential if pattern is unclear
                            new_key = int(k2 * (k2 / k1))
                        
                        extended_keys[i] = new_key
                        print(f"Generated key {i}: {hex(new_key)}")
            else:
                # If no clear pattern, use the last ratio as fallback
                last_ratio = ratios[-1]
                print(f"Using last observed ratio: {last_ratio:.4f}")
                
                for i in range(max_key_index + 1, target_count + 1):
                    prev_key = extended_keys[i-1]
                    new_key = int(prev_key * last_ratio)
                    extended_keys[i] = new_key
                    print(f"Generated key {i}: {hex(new_key)}")
    
    return extended_keys

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
    try:
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
    except Exception as e:
        print(f"Error generating address: {e}")
        return "ERROR_GENERATING_ADDRESS"

def generate_all_bitcoin_addresses(private_keys: Dict[int, int]) -> Dict[int, str]:
    """Generate Bitcoin addresses for all private keys"""
    addresses = {}
    target_address = "1CZqucvN1wZ4Gwq95dsNgj1xVjUcK3pcMQ"
    found_match = False
    
    print(f"\nGenerating Bitcoin addresses for {len(private_keys)} private keys...")
    
    for idx, private_key in sorted(private_keys.items()):
        try:
            # Skip very large keys that might cause issues
            if private_key.bit_length() > 256:
                print(f"Key {idx} is too large, skipping ({private_key.bit_length()} bits)")
                continue
                
            # Generate public key
            public_key = private_key_to_public_key(private_key)
            
            # Generate address
            address = public_key_to_address(public_key)
            
            # Store the address
            addresses[idx] = address
            
            # Check if this is our target address
            if address == target_address:
                print(f"✓ MATCH FOUND! Key {idx} produces target address: {address}")
                print(f"  Private key: {hex(private_key)}")
                found_match = True
                
            # Print progress for a few keys
            if idx <= 10 or idx % 20 == 0 or (idx >= 150):
                print(f"Key {idx}: {address} (priv: {hex(private_key)})")
            
        except Exception as e:
            print(f"Error processing key {idx}: {e}")
    
    if not found_match:
        print("\nNo exact match found for target address. Checking for similar addresses...")
        
        # Load target address details
        try:
            decoded = base58.b58decode(target_address)
            target_hash160 = decoded[1:21].hex()
            
            # Check for similar hash160 values
            for idx, address in addresses.items():
                try:
                    decoded = base58.b58decode(address)
                    hash160 = decoded[1:21].hex()
                    
                    # Calculate similarity (count matching characters)
                    similarity = sum(a == b for a, b in zip(target_hash160, hash160))
                    similarity_pct = similarity / len(target_hash160) * 100
                    
                    if similarity_pct > 70:  # More than 70% similar
                        print(f"Similar address found for key {idx}: {address}")
                        print(f"  Similarity: {similarity_pct:.1f}%")
                        print(f"  Hash160: {hash160}")
                        print(f"  Target:  {target_hash160}")
                except:
                    pass
        except Exception as e:
            print(f"Error checking for similar addresses: {e}")
    
    return addresses

def main():
    print("Bitcoin Key Pattern Extension - Generating All 160 Private Keys")
    print("============================================================")
    
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
    
    # Load known keys
    known_keys = load_known_keys()
    if not known_keys:
        print("Failed to load known keys. Exiting.")
        return
    
    print(f"Loaded {len(known_keys)} known keys.")
    
    # Display the first and last few known keys
    print("\nSample of known keys:")
    for i in [1, 2, 3, 64, 65, 66]:
        if i in known_keys:
            print(f"Key {i}: {hex(known_keys[i])}")
    
    # Extend the pattern to get all 160 keys
    all_keys = extend_key_pattern(known_keys, target_count=160)
    print(f"\nExtended to {len(all_keys)} keys total.")
    
    # Generate Bitcoin addresses for all keys
    all_addresses = generate_all_bitcoin_addresses(all_keys)
    
    # Save results to file
    with open("all_160_keys_and_addresses.txt", "w") as f:
        f.write("index,private_key,bitcoin_address\n")
        for idx in sorted(all_keys.keys()):
            private_key = all_keys[idx]
            address = all_addresses.get(idx, "ERROR")
            f.write(f"{idx},{hex(private_key)},{address}\n")
    
    print(f"\nSaved all keys and addresses to all_160_keys_and_addresses.txt")
    
    # Final summary
    print("\nVerification mechanism:")
    print("1. Check if any of the generated addresses match our target: 1CZqucvN1wZ4Gwq95dsNgj1xVjUcK3pcMQ")
    print("2. Analyze generated keys for consistency with the established pattern")
    print("3. Verify that the Nth character of the Nth address pattern still holds")

if __name__ == "__main__":
    main() 