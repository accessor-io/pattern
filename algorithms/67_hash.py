from hashlib import sha256
import base58
from ecdsa import SigningKey, SECP256k1
from cryptos import hash160

# Input hexadecimal string
private_key_hex = "0xcfdb5093dbe9d115720501aa59168ff8bf650c4d584d012274b13b91fe7066df"

def validate_private_key(hex_str: str) -> bool:
    """Validate a Bitcoin private key"""
    try:
        # Pad with leading zeros if needed
        hex_str = hex_str.zfill(64)
            
        # Convert to integer and check range
        key_int = int(hex_str, 16)
        print(f"Validating private key integer: {key_int}")
        if not (1 <= key_int < 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141):
            return False
            
        return True
    except:
        return False

def private_key_to_address(hex_str: str) -> str:
    """Convert private key to uncompressed Bitcoin address"""
    # Pad with leading zeros if needed
    hex_str = hex_str.zfill(64)
    
    # Convert to bytes
    privkey_bytes = bytes.fromhex(hex_str)
    print(f"Private key bytes: {privkey_bytes.hex()}")
    
    # Generate public key
    sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()
    
    # Get uncompressed public key (04 prefix)
    x = vk.pubkey.point.x()
    y = vk.pubkey.point.y()
    print(f"Public key X coordinate: {hex(x)}")
    print(f"Public key Y coordinate: {hex(y)}")
    
    pubkey = b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
    print(f"Full uncompressed public key: {pubkey.hex()}")
    
    # Use cryptos for hashing
    hash160 = cryptos.hash160(pubkey)
    print(f"RIPEMD160(SHA256) hash: {hash160.hex()}")
    
    # Add version byte (00 for mainnet)
    version_hash = b'\x00' + hash160
    print(f"Version + hash: {version_hash.hex()}")
    
    # Calculate checksum using cryptos
    checksum = cryptos.sha256(cryptos.sha256(version_hash))[:4]
    print(f"Double SHA256 checksum: {checksum.hex()}")
    
    # Base58Check encoding
    address_bytes = version_hash + checksum
    print(f"Final bytes before base58: {address_bytes.hex()}")
    address = base58.b58encode(address_bytes).decode()
    print(f"Base58Check encoded address: {address}")
    return address

if __name__ == "__main__":
    # Pad with leading zeros if needed
    private_key_hex = private_key_hex.zfill(64)
        
    # Validate hex characters
    try:
        key_int = int(private_key_hex, 16)
        print(f"Private key as integer: {key_int}")
    except ValueError:
        print("Invalid private key: Must contain only valid hex characters (0-9, a-f)")
        exit()
        
    # Validate key range
    max_key = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    print(f"Maximum allowed key value: {max_key}")
    if not (1 <= key_int < max_key):
        print(f"Invalid private key: Value must be between 1 and {max_key}")
        exit()
        
    # Generate address if valid
    print("\nGenerating Bitcoin address...")
    address = private_key_to_address(private_key_hex)
    print(f"\nPrivate Key (hex): {private_key_hex}")
    print(f"Final Bitcoin Address: {address}")