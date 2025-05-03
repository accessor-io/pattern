import hashlib
import base58
import ecdsa
from ripemd160 import ripemd160 as ripemd160_pure

def generate_address(private_key_hex):
    # Convert hex string to bytes
    private_key = bytes.fromhex(private_key_hex)
    
    # Generate signing key and verifying key
    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    
    # Get public key bytes
    public_key = b"\x04" + vk.to_string()
    
    # Calculate SHA256
    sha256_hash = hashlib.sha256(public_key).digest()
    
    # Calculate RIPEMD160 using our pure Python implementation
    hash160 = ripemd160_pure(sha256_hash)
    
    # Add version byte (0x00 for mainnet)
    version = b"\x00"
    payload = version + hash160
    
    # Calculate checksum
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    
    # Encode in base58
    address = base58.b58encode(payload + checksum).decode()
    
    return address

def main():
    # Starting private key
    start_key = "0000000000000000000000000000000000000000000000006937092c8634d89de3"
    
    # Convert to integer for incrementing
    current_key = int(start_key, 16)
    
    # Number of keys to check
    num_keys = 1000
    
    print(f"Starting key hunt from: {start_key}")
    print(f"Checking {num_keys} keys...\n")
    
    for i in range(num_keys):
        # Convert current key to hex string
        current_key_hex = hex(current_key)[2:].zfill(64)
        
        # Generate address
        address = generate_address(current_key_hex)
        
        # Print progress
        if i % 100 == 0:
            print(f"Checked {i} keys...")
            print(f"Current key: 0x{current_key_hex}")
            print(f"Address: {address}\n")
        
        # Increment key
        current_key += 1

if __name__ == "__main__":
    main() 