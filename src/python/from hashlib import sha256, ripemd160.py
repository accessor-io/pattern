from hashlib import sha256, ripemd160
import base58
from ecdsa import SigningKey, SECP256k1

# Input hexadecimal string
private_key_hex = "cf51215a5ec4298688a69c17ddea1d41aa707cc7b820b8a827c05a82cfdc969"

def validate_private_key(hex_str: str) -> bool:
    """Validate a Bitcoin private key"""
    try:
        # Check length (32 bytes = 64 hex chars)
        if len(hex_str) != 64:
            return False
            
        # Convert to integer and check range
        key_int = int(hex_str, 16)
        if not (1 <= key_int < 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141):
            return False
            
        return True
    except:
        return False

def private_key_to_address(hex_str: str) -> str:
    """Convert private key to uncompressed Bitcoin address"""
    # Convert to bytes
    privkey_bytes = bytes.fromhex(hex_str)
    
    # Generate public key
    sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()
    
    # Get uncompressed public key (04 prefix)
    x = vk.pubkey.point.x()
    y = vk.pubkey.point.y()
    pubkey = b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
    
    # Hash with SHA-256 and RIPEMD-160
    sha_hash = sha256(pubkey).digest()
    hash160 = ripemd160(sha_hash).digest()
    
    # Add version byte (00 for mainnet)
    version_hash = b'\x00' + hash160
    
    # Calculate checksum
    checksum = sha256(sha256(version_hash).digest()).digest()[:4]
    
    # Base58Check encoding
    address_bytes = version_hash + checksum
    return base58.b58encode(address_bytes).decode()

if __name__ == "__main__":
    if not validate_private_key(private_key_hex):
        print("Invalid private key!")
    else:
        address = private_key_to_address(private_key_hex)
        print(f"Private Key: {private_key_hex}")
        print(f"Bitcoin Address: {address}")