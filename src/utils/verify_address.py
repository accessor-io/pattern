import hashlib
import base58

def hex_to_address(hex_string):
    # Remove leading zeros and '0x' if present
    hex_string = hex_string.replace('0x', '').lstrip('0')
    
    # Convert hex to bytes
    pub_bytes = bytes.fromhex(hex_string)
    
    # SHA256
    sha256_hash = hashlib.sha256(pub_bytes).digest()
    
    # RIPEMD160
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
    
    # Add version byte (0x00 for mainnet)
    version_ripemd160_hash = b'\x00' + ripemd160_hash
    
    # Double SHA256 for checksum
    double_sha256 = hashlib.sha256(hashlib.sha256(version_ripemd160_hash).digest()).digest()
    
    # First 4 bytes of double SHA256 as checksum
    checksum = double_sha256[:4]
    
    # Combine version, ripemd160 hash, and checksum
    binary_address = version_ripemd160_hash + checksum
    
    # Base58 encode
    address = base58.b58encode(binary_address).decode('utf-8')
    
    return address

# Test the prediction
hex_string = "0000000000000000000000000000000000000000000000004b47c924a0b64d0d0"
address = hex_to_address(hex_string)
print(f"Generated address: {address}")
print(f"Expected address: 1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9")
print(f"Match: {address == '1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9'}") 