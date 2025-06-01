from ecdsa import SigningKey, SECP256k1
import hashlib
import base58
from typing import Tuple

SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def validate_private_key(private_key: int) -> bool:
    """Validate private key is within secp256k1 curve order bounds"""
    return 1 <= private_key < SECP256K1_ORDER

def hash160(data: bytes) -> bytes:
    """Proper RIPEMD160(SHA256()) implementation"""
    sha = hashlib.sha256(data).digest()
    return hashlib.new('ripemd160', sha).digest()

def private_key_to_public_key(private_key: int) -> Tuple[bytes, bytes]:
    """Generate uncompressed public key with proper validation"""
    if not validate_private_key(private_key):
        raise ValueError("Invalid private key for secp256k1 curve")
    
    sk = SigningKey.from_secret_exponent(private_key, curve=SECP256k1)
    vk = sk.get_verifying_key()
    
    # Uncompressed public key format (0x04 + x + y)
    x = vk.pubkey.point.x().to_bytes(32, byteorder='big')
    y = vk.pubkey.point.y().to_bytes(32, byteorder='big')
    return b'\x04' + x + y, x  # Return both full and x-only formats

def private_key_to_address(private_key: int, index: int) -> str:
    """Generate Bitcoin address with proper zero-padding"""
    # Shift significant bits to the left and pad with zeros
    padded_key = private_key << (256 - index)
    privkey_bytes = padded_key.to_bytes(32, byteorder='big')
    
    # Generate public key using the padded key
    public_key, _ = private_key_to_public_key(padded_key)
    
    # Calculate hash160
    h160 = hash160(public_key)
    
    # Create versioned payload
    version_payload = b'\x00' + h160
    
    # Calculate checksum
    checksum = hashlib.sha256(hashlib.sha256(version_payload).digest()).digest()[:4]
    
    # Base58Check encoding
    address = base58.b58encode(version_payload + checksum)
    return address.decode('utf-8')

def validate_solution(index: int, private_key: int, known_address: str) -> bool:
    """Enhanced validation with proper padding"""
    # Convert to 256-bit format with right-aligned bits
    padded_key = private_key << (256 - index)
    
    # Validate the full 256-bit key
    if not validate_private_key(padded_key):
        return False
    
    # Generate address with proper padding
    try:
        generated_addr = private_key_to_address(private_key, index)
    except Exception as e:
        print(f"Address generation failed: {str(e)}")
        return False
    
    return generated_addr == known_address 