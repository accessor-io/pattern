import hashlib
import base58
from ripemd160 import ripemd160 as ripemd160_hash

class Point:
    def __init__(self,
        x=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
        y=0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
        p=2**256 - 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 - 1):
        self.x = x
        self.y = y
        self.p = p

    def __add__(self, other):
        return self.__radd__(other)

    def __mul__(self, other):
        return self.__rmul__(other)

    def __rmul__(self, other):
        n = self
        q = None

        for i in range(256):
            if other & (1 << i):
                q = q + n
            n = n + n

        return q

    def __radd__(self, other):
        if other is None:
            return self
        x1 = other.x
        y1 = other.y
        x2 = self.x
        y2 = self.y
        p = self.p

        if self == other:
            l = pow(2 * y2 % p, p-2, p) * (3 * x2 * x2) % p
        else:
            l = pow(x1 - x2, p-2, p) * (y1 - y2) % p

        newX = (l ** 2 - x2 - x1) % p
        newY = (l * x2 - l * newX - y2) % p

        return Point(newX, newY)

    def toBytes(self):
        x = self.x.to_bytes(32, "big")
        y = self.y.to_bytes(32, "big")
        return b"\x04" + x + y

def sha256(data):
    digest = hashlib.new("sha256")
    digest.update(data)
    return digest.digest()

def ripemd160(x):
    return ripemd160_hash(x)

def get_address(private_key_hex):
    # Remove 0x prefix if present
    if private_key_hex.startswith('0x'):
        private_key_hex = private_key_hex[2:]
    
    # Convert to integer
    private_key_int = int(private_key_hex, 16)
    
    # Get public key point
    SPEC256k1 = Point()
    public_key_point = SPEC256k1 * private_key_int
    
    # Get public key bytes
    public_key_bytes = public_key_point.toBytes()
    
    # Get RIPEMD160(SHA256()) hash
    h160 = ripemd160(sha256(public_key_bytes))
    
    # Add version byte in front of RIPEMD-160 hash (0x00 for mainnet)
    vh160 = b"\x00" + h160
    
    # Add checksum
    chk = sha256(sha256(vh160))[:4]
    
    # Encode in base58
    addr = vh160 + chk
    address = base58.b58encode(addr).decode()
    
    return address

# Private keys in hex
key69 = "0000000000000000000000000000000000000000000000101d83275fb2bc7e0c"
key70 = "0000000000000000000000000000000000000000000000349b84b6431a6c4ef1"

# Expected addresses
expected69 = "19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG"
expected70 = "19YZECXj3SxEZMoUeJ1yiPsw8xANe7M7QR"

# Get addresses
addr69 = get_address(key69)
addr70 = get_address(key70)

print(f"Key 69: 0x{key69}")
print(f"Generated Address: {addr69}")
print(f"Expected Address:  {expected69}")
print(f"Match: {addr69 == expected69}")

print(f"\nKey 70: 0x{key70}")
print(f"Generated Address: {addr70}")
print(f"Expected Address:  {expected70}")
print(f"Match: {addr70 == expected70}") 