# Create a new file for validating Bitcoin addresses using Base58Check
import hashlib
import sys

BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def base58_decode(s: str) -> bytes:
    """
    Decode a Base58-encoded string to raw bytes (version+payload+checksum).
    """
    num = 0
    for char in s:
        num = num * 58 + BASE58_ALPHABET.index(char)
    return num.to_bytes(25, byteorder='big')


def validate_address(addr: str) -> bool:
    """
    Validate a Bitcoin P2PKH address by verifying its Base58Check checksum.

    Returns True if the address is valid, False otherwise.
    """
    try:
        decoded = base58_decode(addr)
    except ValueError:
        return False
    version_payload = decoded[:-4]
    checksum = decoded[-4:]
    hashed = hashlib.sha256(hashlib.sha256(version_payload).digest()).digest()
    return hashed[:4] == checksum


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python address_validator.py <bitcoin_address>")
        sys.exit(1)
    address = sys.argv[1]
    valid = validate_address(address)
    print(f"{address} is {'valid' if valid else 'invalid'}") 