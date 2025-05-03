import hashlib
from ripemd160 import ripemd160

class Point:
    def __init__(self, curve, x, y):
        self.curve = curve
        self.x = x
        self.y = y

    def __add__(self, other):
        # Handle special case of P + 0 = 0 + P = P
        if other == INF:
            return self
        if self == INF:
            return other
        
        # Handle special case of P + (-P) = 0
        if self.x == other.x and self.y != other.y:
            return INF
        
        # Handle special case of P + P
        if self == other:
            # Calculate slope of the tangent line
            slope = (3 * self.x * self.x) * pow(2 * self.y, -1, self.curve.p) % self.curve.p
        else:
            # Calculate slope of the line between points
            slope = (other.y - self.y) * pow(other.x - self.x, -1, self.curve.p) % self.curve.p
        
        # Calculate new point
        x3 = (slope * slope - self.x - other.x) % self.curve.p
        y3 = (slope * (self.x - x3) - self.y) % self.curve.p
        
        return Point(self.curve, x3, y3)

    def __rmul__(self, k):
        result = INF
        append = self
        while k:
            if k & 1:
                result += append
            append += append
            k >>= 1
        return result

class Curve:
    def __init__(self, p, a, b):
        self.p = p
        self.a = a
        self.b = b

# Define the secp256k1 curve used in Bitcoin
bitcoin_curve = Curve(
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
    a = 0,
    b = 7
)

# Generator point
G = Point(
    bitcoin_curve,
    x = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    y = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
)

# Point at infinity (identity element)
INF = Point(None, None, None)

def sha256(data):
    """Compute SHA256 hash of data."""
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).digest()

def hash160(data):
    """Compute RIPEMD160(SHA256()) of data."""
    return ripemd160(sha256(data))

def encode_base58check(version, payload):
    """Encode data in base58check format."""
    # Add version byte in front of payload
    s = bytes([version]) + payload
    
    # Add 4 bytes of checksum
    checksum = sha256(sha256(s))[:4]
    s += checksum
    
    # Convert to base58
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    value = int.from_bytes(s, 'big')
    result = ''
    while value:
        value, remainder = divmod(value, 58)
        result = alphabet[remainder] + result
    
    # Add leading zeros
    for byte in s:
        if byte == 0:
            result = alphabet[0] + result
        else:
            break
            
    return result

def private_to_public(private_key):
    """Convert private key to public key point."""
    # Ensure private key is an integer
    if isinstance(private_key, str):
        private_key = int(private_key, 16)
    elif isinstance(private_key, bytes):
        private_key = int.from_bytes(private_key, 'big')
    
    # Multiply generator point by private key
    return private_key * G

def public_to_address(public_key, compressed=True, testnet=True):
    """Convert public key to Bitcoin address."""
    # Convert point to bytes
    if compressed:
        prefix = b'\x02' if public_key.y % 2 == 0 else b'\x03'
        pk_bytes = prefix + public_key.x.to_bytes(32, 'big')
    else:
        pk_bytes = b'\x04' + public_key.x.to_bytes(32, 'big') + public_key.y.to_bytes(32, 'big')
    
    # Perform RIPEMD160(SHA256()) hash
    h = hash160(pk_bytes)
    
    # Add version byte (0x6f for testnet, 0x00 for mainnet)
    version = 0x6f if testnet else 0x00
    
    # Encode in base58check
    return encode_base58check(version, h)

def private_to_address(private_key, compressed=True, testnet=True):
    """Convert private key directly to Bitcoin address."""
    public_key = private_to_public(private_key)
    return public_to_address(public_key, compressed, testnet)

def verify_key(private_key_hex, expected_address):
    """Verify if a private key corresponds to an expected Bitcoin address."""
    # Convert private key to address
    address = private_to_address(private_key_hex, compressed=True, testnet=False)
    
    # Compare with expected address
    return address == expected_address

# Test keys 69 and 70
key69 = "0000000000000000000000000000000000000000000000101d83275fb2bc7e0c"
key70 = "0000000000000000000000000000000000000000000000349b84b6431a6c4ef1"

expected69 = "19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG"
expected70 = "19YZECXj3SxEZMoUeJ1yiPsw8xANe7M7QR"

print(f"Key 69 verification: {verify_key(key69, expected69)}")
print(f"Generated address: {private_to_address(key69, compressed=True, testnet=False)}")
print(f"Key 70 verification: {verify_key(key70, expected70)}")
print(f"Generated address: {private_to_address(key70, compressed=True, testnet=False)}") 