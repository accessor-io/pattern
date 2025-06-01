from ecdsa import SigningKey, SECP256k1
import hashlib
import base58
from typing import Tuple

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
    """Generate Bitcoin address with index-specific bit length handling"""
    # Enforce exact bit length
    bit_length = index
    masked_key = private_key & ((1 << bit_length) - 1)
    
    # Convert to properly padded hex
    hex_str = f"{masked_key:x}"
    
    # Pad with trailing zero if odd length
    if len(hex_str) % 2 != 0:
        hex_str += '0'
    
    # Convert to 32-byte format (pad with zeros if needed)
    byte_length = (bit_length + 7) // 8
    privkey_bytes = masked_key.to_bytes(byte_length, byteorder='big').ljust(32, b'\x00')
    
    # Generate public key
    public_key, _ = private_key_to_public_key(int.from_bytes(privkey_bytes, 'big'))
    
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
    """Enhanced validation with bit length enforcement"""
    # Enforce exact bit length
    if private_key.bit_length() != index:
        print(f"Bit length mismatch: {private_key.bit_length()} vs {index}")
        return False
    
    # Generate address with proper padding
    try:
        generated_addr = private_key_to_address(private_key, index)
    except Exception as e:
        print(f"Address generation failed: {str(e)}")
        return False
    
    return generated_addr == known_address 