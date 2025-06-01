#!/usr/bin/env python3

import hashlib
import ecdsa
import base58
from datetime import datetime
import multiprocessing as mp
from tqdm import tqdm
import sys

def private_key_to_address(private_key_hex):
    # Clean up the private key - remove any whitespace and ensure it's 64 characters
    private_key_hex = private_key_hex.strip().zfill(64)
    
    # Convert private key to bytes
    private_key_bytes = bytes.fromhex(private_key_hex)
    
    # Create signing key
    signing_key = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
    
    # Get verifying key (public key)
    verifying_key = signing_key.get_verifying_key()
    
    # Get public key in compressed format
    public_key_bytes = verifying_key.to_string("compressed")
    
    # Perform SHA-256 hashing on the public key
    sha256_hash = hashlib.sha256(public_key_bytes).digest()
    
    # Perform RIPEMD-160 hashing on the result of SHA-256
    ripemd160_hash = hashlib.new('ripemd160')
    ripemd160_hash.update(sha256_hash)
    ripemd160_hash = ripemd160_hash.digest()
    
    # Add version byte in front of RIPEMD-160 hash (0x00 for mainnet)
    version_ripemd160_hash = b'\x00' + ripemd160_hash
    
    # Perform double SHA-256 hashing on the extended RIPEMD-160 result
    double_sha256_hash = hashlib.sha256(hashlib.sha256(version_ripemd160_hash).digest()).digest()
    
    # Take the first 4 bytes of the second SHA-256 hash for checksum
    checksum = double_sha256_hash[:4]
    
    # Add the 4 checksum bytes to the extended RIPEMD-160 hash
    binary_address = version_ripemd160_hash + checksum
    
    # Convert the result from bytes to base58 string
    address = base58.b58encode(binary_address).decode('utf-8')
    
    return address

def search_range(start_key, end_key, target_address, step_size, result_queue):
    current = start_key
    while current >= end_key:
        try:
            current_hex = hex(current)[2:].zfill(64)
            address = private_key_to_address(current_hex)
            
            if address == target_address:
                result_queue.put(("found", current_hex))
                return
                
            current -= step_size
            
        except Exception as e:
            print(f"\nError in worker: {e}")
            break
    
    result_queue.put(("not_found", None))

def find_matching_key(start_key, target_address, num_processes=8, step_size=100):
    start_int = int(start_key, 16)
    
    # Calculate range size for each process
    range_size = 1000000 * step_size  # Each process will check 1M keys with the given step size
    
    processes = []
    result_queue = mp.Queue()
    
    print(f"Starting search with {num_processes} processes")
    print(f"Step size: {step_size}")
    print(f"Starting from: {start_key}")
    print(f"Target address: {target_address}")
    
    try:
        # Create and start processes
        for i in range(num_processes):
            process_start = start_int - (i * range_size)
            process_end = process_start - range_size
            p = mp.Process(
                target=search_range,
                args=(process_start, process_end, target_address, step_size, result_queue)
            )
            processes.append(p)
            p.start()
        
        # Monitor results with progress bar
        with tqdm(total=num_processes, desc="Search Progress") as pbar:
            completed = 0
            while completed < num_processes:
                result_type, value = result_queue.get()
                if result_type == "found":
                    # Kill all processes
                    for p in processes:
                        p.terminate()
                    print(f"\nMatch found! Private key: {value}")
                    return value
                completed += 1
                pbar.update(1)
        
        print("\nNo match found in the searched range")
        return None
        
    except KeyboardInterrupt:
        print("\nSearch interrupted by user")
        for p in processes:
            p.terminate()
        sys.exit(0)
    finally:
        for p in processes:
            p.join()

if __name__ == "__main__":
    try:
        # Install tqdm if not present
        import tqdm
    except ImportError:
        import pip
        pip.main(['install', 'tqdm'])
        from tqdm import tqdm
    
    # Starting private key
    start_key = "68f5c28f5c28f60000"
    target_address = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"
    
    print("Starting parallel search...")
    result = find_matching_key(
        start_key=start_key,
        target_address=target_address,
        num_processes=8,  # Use 8 parallel processes
        step_size=100     # Check every 100th key
    ) 