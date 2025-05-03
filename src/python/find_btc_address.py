#!/usr/bin/env python3
"""
Bitcoin Private Key Finder for address: 1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ

This specialized script focuses on finding the private key by searching:
1. Near the known sequence terms with tiny step sizes
2. Testing common mathematical and bit-wise transformations
3. Testing incremental values from known sequence positions
"""

import hashlib
import base58
from ecdsa import SigningKey, SECP256k1
import time
import concurrent.futures
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("btc_address_search.log")
    ]
)
logger = logging.getLogger("btc_finder")

# Target Bitcoin address
TARGET_ADDRESS = "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"

# Known sequence values
SEQUENCE = {
    1: 0x1,
    10: 0x202,
    20: 0xd2c55,
    30: 0x3d94cd64,
    40: 0x9de820a7c,
    50: 0xefae164cb9e3c, 
    60: 0xfc07a1825367bbe,
    66: 0x2832ed74f2b5e35ee,
    67: 0x730fc235c1942c1ae,
    70: 0x349b84b6431a6c4ef1,
    75: 0x4c5ce114686a1336e07,
    80: 0xea1a5c66dcc11b5ad180,
    85: 0x11720c4f018d51b8cebba8,
    90: 0x2ce00bb2136a445c71e85bf
}

def private_key_to_address(private_key):
    """
    Convert a private key (integer) to a compressed Bitcoin address.
    """
    try:
        # Convert integer to bytes
        privkey_bytes = private_key.to_bytes(32, byteorder='big')
        
        # Create ECDSA signing key
        sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()
        
        # Get x and y coordinates
        x = vk.pubkey.point.x()
        y = vk.pubkey.point.y()
        
        # Create compressed public key format (0x02 if y is even, 0x03 if y is odd)
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        compressed_pubkey = prefix + x.to_bytes(32, 'big')
        
        # Hash with SHA-256 and RIPEMD-160
        sha_digest = hashlib.sha256(compressed_pubkey).digest()
        ripemd_digest = hashlib.new('ripemd160', sha_digest).digest()
        
        # Add network byte (0x00 for mainnet)
        versioned_payload = b'\x00' + ripemd_digest
        
        # Calculate and append checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
        address_bytes = versioned_payload + checksum
        
        # Encode with Base58
        address = base58.b58encode(address_bytes).decode('utf-8')
        return address
    except Exception as e:
        logger.error(f"Error generating address: {e}")
        return None

def save_result(private_key):
    """
    Save the private key and address if found.
    """
    result = {
        "private_key_hex": hex(private_key),
        "private_key_integer": private_key,
        "address": TARGET_ADDRESS,
        "found_timestamp": time.time()
    }
    
    logger.info(f"PRIVATE KEY FOUND: {hex(private_key)}")
    logger.info(f"Address: {TARGET_ADDRESS}")
    
    # Save to file
    with open("bitcoin_key_found.txt", "w") as f:
        for key, value in result.items():
            f.write(f"{key}: {value}\n")
    
    return result

def test_key(private_key):
    """
    Test if a private key corresponds to the target address.
    """
    if private_key <= 0 or private_key >= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141:
        return False  # Invalid ECDSA private key range
        
    address = private_key_to_address(private_key)
    if address == TARGET_ADDRESS:
        return True
    return False

def search_region(base, range_size, step=1):
    """
    Search a specific region around a base value.
    """
    logger.info(f"Searching region around {hex(base)} (±{range_size}, step={step})")
    
    # First test the exact base value
    if test_key(base):
        logger.info(f"Found match at exact base value: {hex(base)}")
        return base
    
    # Search above the base value
    for i in range(step, range_size + 1, step):
        if i % 10000 == 0:
            logger.info(f"Testing +{i} from {hex(base)}")
            
        test_value = base + i
        if test_key(test_value):
            logger.info(f"Found match at {hex(test_value)} (+{i} from base)")
            return test_value
    
    # Search below the base value
    for i in range(step, range_size + 1, step):
        if i % 10000 == 0:
            logger.info(f"Testing -{i} from {hex(base)}")
            
        test_value = base - i
        if test_value <= 0:
            break
            
        if test_key(test_value):
            logger.info(f"Found match at {hex(test_value)} (-{i} from base)")
            return test_value
    
    logger.info(f"No match found in region around {hex(base)}")
    return None

def search_transformed_values(base_values, transformations):
    """
    Search using various transformations of base values.
    """
    logger.info(f"Searching with {len(transformations)} transformations on {len(base_values)} base values")
    
    for base in base_values:
        for name, transform_func in transformations.items():
            try:
                transformed = transform_func(base)
                logger.info(f"Testing transformation {name} on {hex(base)}: {hex(transformed)}")
                
                if test_key(transformed):
                    logger.info(f"Found match with {name} on {hex(base)}: {hex(transformed)}")
                    return transformed
                    
                # Also try +1 and -1 from the transformed value
                if test_key(transformed + 1):
                    logger.info(f"Found match with {name}+1 on {hex(base)}: {hex(transformed + 1)}")
                    return transformed + 1
                    
                if transformed > 1 and test_key(transformed - 1):
                    logger.info(f"Found match with {name}-1 on {hex(base)}: {hex(transformed - 1)}")
                    return transformed - 1
                    
            except Exception as e:
                logger.error(f"Error applying {name} to {hex(base)}: {e}")
    
    logger.info("No matches found with transformations")
    return None

def main():
    """
    Main execution function.
    """
    logger.info(f"Starting search for private key of address: {TARGET_ADDRESS}")
    start_time = time.time()
    
    # Define base values to search around
    base_values = list(SEQUENCE.values())
    logger.info(f"Loaded {len(base_values)} sequence values as search bases")
    
    # Define transformations to try
     transformations = {
        "no_change": lambda x: x,
        "add_1": lambda x: x + 1,
        "subtract_1": lambda x: x - 1,
        "add_68": lambda x: x + 0x68,
        "subtract_68": lambda x: x - 0x68,
        "multiply_1.1": lambda x: int(x * 1.1),
        "multiply_1.5": lambda x: int(x * 1.5),
        "multiply_2": lambda x: x * 2,
        "divide_2": lambda x: x // 2,
        "bit_shift_left_1": lambda x: x << 1,
        "bit_shift_right_1": lambda x: x >> 1,
        "xor_with_term67": lambda x: x ^ SEQUENCE[67],
        "add_position_number": lambda x: x + list(SEQUENCE.keys())[list(SEQUENCE.values()).index(x)]
    }
    
    # 1. First search small areas around base values
    logger.info("Phase 1: Searching small regions around base values")
    for base in base_values:
        result = search_region(base, 1000, 1)
        if result:
            save_result(result)
            logger.info(f"Search completed in {time.time() - start_time:.2f} seconds")
            return result
    
    # 2. Search transformed values
    logger.info("Phase 2: Searching with transformations")
    result = search_transformed_values(base_values, transformations)
    if result:
        save_result(result)
        logger.info(f"Search completed in {time.time() - start_time:.2f} seconds")
        return result
    
    # 3. Try larger regions around the latest sequence values
    logger.info("Phase 3: Searching larger regions around latest sequence values")
    latest_values = [SEQUENCE[67], SEQUENCE[66]]
    for base in latest_values:
        result = search_region(base, 100000, 1)
        if result:
            save_result(result)
            logger.info(f"Search completed in {time.time() - start_time:.2f} seconds")
            return result
    
    logger.info(f"Search completed without finding a match in {time.time() - start_time:.2f} seconds")
    return None

if __name__ == "__main__":
    try:
        result = main()
        if result:
            print(f"\n=== PRIVATE KEY FOUND ===")
            print(f"Key: {hex(result)}")
            print(f"Address: {TARGET_ADDRESS}")
        else:
            print("\nNo match found in the specified search space.")
    except KeyboardInterrupt:
        print("\nSearch interrupted by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\nError: {e}") 