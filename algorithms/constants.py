"""
Bitcoin Puzzle Solver - Constants Module

Contains all constant values used throughout the Bitcoin puzzle solver.
"""

# Secp256k1 Elliptic Curve Parameters
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141  # Order of the curve
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F  # Field prime
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798  # Generator point x
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8  # Generator point y

# Base58 Alphabet (Bitcoin uses this for address encoding)
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

# The full 159-character Base58 string - assumed to encode transformations
# This string is critical. Its length and content directly affect lookups.
FULL_STRING = "60806040526000805460ff60A01B1916905560" 