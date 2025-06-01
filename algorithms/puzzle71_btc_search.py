#!/usr/bin/env python3
import threading
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
import hashlib
import base58
from time import sleep, time
from ecdsa import SigningKey, SECP256k1

class Puzzle71Search():
    def __init__(self):
        self.start_t = 0
        self.prev_n = 0
        self.cur_n = 0
        self.start_n = 0
        self.end_n = 0
        self.seq = False
        
        # Puzzle 71 specific targets
        self.target_address = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"
        self.target_ripemd160 = "f6f5431d25bbf7b12e8add9af5e3475c44a0a5b8"
        
        # Starting points based on our analysis
        self.ranges = [
            (0x402f1c8d9d44b99800 - 1000000, 0x402f1c8d9d44b99800 + 1000000),  # Around first prediction
            (0x402f1c8d9d44000000, 0x402f1c8d9d45000000),  # Wider range
            (0x402f1c8d9d44b90000, 0x402f1c8d9d44ba0000),  # Middle range
        ]
        
    def speed(self):
        while True:
            if self.cur_n != 0:
                cur_t = time()
                n = self.cur_n
                if self.prev_n == 0:
                    self.prev_n = n
                elapsed_t = cur_t - self.start_t
                print(f"Current: 0x{n:x}, Rate: {abs(n-self.prev_n)//2}/s, Time: [{int(elapsed_t//3600)}:{int(elapsed_t//60%60):02d}:{int(elapsed_t%60):02d}]", end="\r")
                self.prev_n = n
            sleep(2)

    def private_key_to_address(self, private_key: int) -> tuple[str, str]:
        """Convert private key to Bitcoin address and RIPEMD160"""
        try:
            # Convert to public key
            privkey_hex = format(private_key, '064x')
            privkey_bytes = bytes.fromhex(privkey_hex)
            sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
            vk = sk.get_verifying_key()
            x = vk.pubkey.point.x()
            y = vk.pubkey.point.y()
            
            # Compressed public key
            if y % 2 == 0:
                pubkey_bytes = b'\x02' + x.to_bytes(32, 'big')
            else:
                pubkey_bytes = b'\x03' + x.to_bytes(32, 'big')
            
            # Hash160 (SHA256 + RIPEMD160)
            sha256_hash = hashlib.sha256(pubkey_bytes).digest()
            ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
            ripemd160_hex = ripemd160_hash.hex()
            
            # Add version byte and checksum
            versioned_payload = b'\x00' + ripemd160_hash
            checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
            address_bytes = versioned_payload + checksum
            
            # Base58 encode
            address = base58.b58encode(address_bytes).decode()
            return address, ripemd160_hex
        except Exception:
            return None, None

    def check_key(self, n):
        self.cur_n = n
        addr, ripemd = self.private_key_to_address(n)
        if addr is None:
            return
        
        if ripemd == self.target_ripemd160:
            print("\nFOUND THE KEY!")
            print(f"Private Key (hex): 0x{n:x}")
            print(f"Generated Address: {addr}")
            print(f"RIPEMD160: {ripemd}")
            
            with open("puzzle71_solution.txt", "w") as f:
                f.write(f"Private Key (hex): 0x{n:x}\n")
                f.write(f"Address: {addr}\n")
                f.write(f"RIPEMD160: {ripemd}\n")
            
            exit(0)

    def search_range(self, start: int, end: int):
        """Search through a specific range of keys"""
        print(f"\nSearching range: 0x{start:x} - 0x{end:x}")
        with ThreadPoolExecutor(max_workers=cpu_count()) as pool:
            self.start_t = time()
            self.start_n = start
            self.end_n = end
            for i in range(start, end):
                pool.submit(self.check_key, i)

def main():
    searcher = Puzzle71Search()
    
    print("\nPuzzle 71 Bitcoin Key Search")
    print("===========================")
    print(f"Target Address: {searcher.target_address}")
    print(f"Target RIPEMD160: {searcher.target_ripemd160}")
    print(f"\nUsing {cpu_count()} CPU cores")
    
    # Start speed monitoring thread
    speed_thread = threading.Thread(target=searcher.speed)
    speed_thread.daemon = True
    speed_thread.start()
    
    # Search through each range
    try:
        for start, end in searcher.ranges:
            searcher.search_range(start, end)
    except KeyboardInterrupt:
        print("\n\nSearch stopped by user")
        exit(0)

if __name__ == "__main__":
    main() 