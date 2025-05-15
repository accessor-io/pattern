import hashlib
import base58
import ecdsa
from ripemd160 import ripemd160 as ripemd160_pure
import argparse
import threading
import time
from queue import Queue
import sys

class KeyHunt:
    def __init__(self, mode, target_file, bit_range=None, num_threads=1, quiet=False, random_mode=False):
        self.mode = mode
        self.target_file = target_file
        self.bit_range = bit_range
        self.num_threads = num_threads
        self.quiet = quiet
        self.random_mode = random_mode
        self.targets = set()
        self.load_targets()
        
    def load_targets(self):
        """Load target addresses or hashes from file"""
        try:
            with open(self.target_file, 'r') as f:
                for line in f:
                    target = line.strip()
                    if target:
                        self.targets.add(target)
        except Exception as e:
            print(f"Error loading targets: {e}")
            sys.exit(1)
            
    def generate_address(self, private_key_hex):
        """Generate Bitcoin address from private key"""
        private_key = bytes.fromhex(private_key_hex)
        sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        public_key = b"\x04" + vk.to_string()
        sha256_hash = hashlib.sha256(public_key).digest()
        hash160 = ripemd160_pure(sha256_hash)
        version = b"\x00"
        payload = version + hash160
        checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        address = base58.b58encode(payload + checksum).decode()
        return address
        
    def generate_rmd160(self, private_key_hex):
        """Generate RIPEMD160 hash from private key"""
        private_key = bytes.fromhex(private_key_hex)
        sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        public_key = b"\x04" + vk.to_string()
        sha256_hash = hashlib.sha256(public_key).digest()
        hash160 = ripemd160_pure(sha256_hash)
        return hash160.hex()
        
    def worker(self, start_key, end_key, result_queue):
        """Worker thread for key hunting"""
        current_key = start_key
        keys_checked = 0
        start_time = time.time()
        
        while current_key < end_key:
            current_key_hex = hex(current_key)[2:].zfill(64)
            
            if self.mode == 'address':
                result = self.generate_address(current_key_hex)
            elif self.mode == 'rmd160':
                result = self.generate_rmd160(current_key_hex)
                
            if result in self.targets:
                result_queue.put((current_key_hex, result))
                
            current_key += 1
            keys_checked += 1
            
            if not self.quiet and keys_checked % 1000 == 0:
                elapsed = time.time() - start_time
                if elapsed > 0:
                    speed = keys_checked / elapsed
                    print(f"Thread {threading.current_thread().name}: {speed:.2f} keys/s")
                    
    def run(self):
        """Run the key hunt"""
        if self.bit_range:
            start_key = 2 ** (self.bit_range - 1)
            end_key = 2 ** self.bit_range
        else:
            start_key = 1
            end_key = 2 ** 256
            
        keys_per_thread = (end_key - start_key) // self.num_threads
        threads = []
        result_queue = Queue()
        
        for i in range(self.num_threads):
            thread_start = start_key + (i * keys_per_thread)
            thread_end = thread_start + keys_per_thread if i < self.num_threads - 1 else end_key
            
            t = threading.Thread(
                target=self.worker,
                args=(thread_start, thread_end, result_queue),
                name=f"Thread-{i}"
            )
            threads.append(t)
            t.start()
            
        # Monitor results
        while any(t.is_alive() for t in threads):
            try:
                key, result = result_queue.get(timeout=1)
                print(f"\nFound match!")
                print(f"Private Key: {key}")
                print(f"Result: {result}")
            except Queue.Empty:
                continue
                
        for t in threads:
            t.join()
            
def main():
    parser = argparse.ArgumentParser(description='Key hunting tool for Bitcoin addresses and hashes')
    parser.add_argument('-m', '--mode', choices=['address', 'rmd160', 'bsgs'], required=True,
                      help='Mode of operation')
    parser.add_argument('-f', '--file', required=True,
                      help='Target file containing addresses or hashes')
    parser.add_argument('-b', '--bit-range', type=int,
                      help='Bit range to search (e.g. 66 for puzzle 66)')
    parser.add_argument('-t', '--threads', type=int, default=1,
                      help='Number of threads to use')
    parser.add_argument('-q', '--quiet', action='store_true',
                      help='Quiet mode (no progress output)')
    parser.add_argument('-R', '--random', action='store_true',
                      help='Random mode')
    
    args = parser.parse_args()
    
    keyhunt = KeyHunt(
        mode=args.mode,
        target_file=args.file,
        bit_range=args.bit_range,
        num_threads=args.threads,
        quiet=args.quiet,
        random_mode=args.random
    )
    
    print(f"Starting key hunt in {args.mode} mode")
    print(f"Target file: {args.file}")
    if args.bit_range:
        print(f"Bit range: {args.bit_range}")
    print(f"Threads: {args.threads}")
    print(f"Random mode: {args.random}")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        keyhunt.run()
    except KeyboardInterrupt:
        print("\nStopping key hunt...")
        
if __name__ == "__main__":
    main() 