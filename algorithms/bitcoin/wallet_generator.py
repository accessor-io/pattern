import hashlib
import hmac
import base58
from binascii import hexlify, unhexlify

def generate_wallet():
    # Our key
    key = "BHJKKXGOMMXCYTV"
    
    print("Bitcoin Wallet Generator")
    print("=" * 40)
    
    # Method 1: Direct conversion to WIF
    print("\nMethod 1: Direct WIF Generation")
    
    # Convert key to bytes (using ASCII values)
    key_bytes = key.encode('ascii')
    
    # SHA256
    sha256 = hashlib.sha256(key_bytes).digest()
    
    # Add version byte (0x80 for mainnet private key)
    version_key = b'\x80' + sha256
    
    # Double SHA256 for checksum
    double_sha = hashlib.sha256(hashlib.sha256(version_key).digest()).digest()
    
    # Add first 4 bytes as checksum
    final_key = version_key + double_sha[:4]
    
    # Convert to base58
    wif = base58.b58encode(final_key).decode('ascii')
    print(f"WIF Private Key: {wif}")
    
    # Method 2: HD Wallet Generation
    print("\nMethod 2: HD Wallet Generation")
    
    # Use key as seed
    seed = hmac.new(b'Bitcoin seed', key_bytes, hashlib.sha512).digest()
    
    # Split into master private key and chain code
    master_private_key = seed[:32]
    chain_code = seed[32:]
    
    print(f"Master Private Key: {hexlify(master_private_key).decode('ascii')}")
    print(f"Chain Code: {hexlify(chain_code).decode('ascii')}")
    
    # Generate master public key
    # Note: This is simplified, real implementation would use secp256k1
    master_public_key = hashlib.sha256(master_private_key).digest()
    
    # Generate addresses
    # Version byte (0x00 for mainnet public address)
    version_pub_key = b'\x00' + master_public_key
    
    # Double SHA256 for checksum
    double_sha_pub = hashlib.sha256(hashlib.sha256(version_pub_key).digest()).digest()
    
    # Add checksum
    final_pub_key = version_pub_key + double_sha_pub[:4]
    
    # Convert to base58
    address = base58.b58encode(final_pub_key).decode('ascii')
    print(f"Bitcoin Address: {address}")
    
    # Method 3: Try key parts separately
    print("\nMethod 3: Key Parts Analysis")
    
    # Split key into parts
    identifier = key[0]  # B
    prefix = key[1:6]    # HJKKX
    core = key[6:10]     # GOMM
    checksum = key[10:]  # XCYTV
    
    print(f"Identifier: {identifier}")
    print(f"Prefix: {prefix}")
    print(f"Core: {core}")
    print(f"Checksum: {checksum}")
    
    # Try using core as seed
    core_seed = hmac.new(b'Bitcoin seed', core.encode('ascii'), hashlib.sha512).digest()
    core_private_key = core_seed[:32]
    core_chain_code = core_seed[32:]
    
    print(f"\nCore-based Private Key: {hexlify(core_private_key).decode('ascii')}")
    print(f"Core-based Chain Code: {hexlify(core_chain_code).decode('ascii')}")

if __name__ == "__main__":
    generate_wallet() 