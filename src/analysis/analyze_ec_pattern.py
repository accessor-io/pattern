#!/usr/bin/env python3
"""
Analyze elliptic curve patterns in the Bitcoin puzzle
"""

import hashlib
import binascii
import base58
from typing import List, Tuple

# The test value
TEST_VALUE = 0x4e5114d15126dfc4e0e9283275748a0667dd08abd95edfaa3f6e8165bebf1313

# secp256k1 curve parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G_x = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
G_y = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

def read_key_pairs(filename: str) -> List[Tuple[str, str]]:
    """Read private/public key pairs from the puzzle file."""
    pairs = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        for i in range(0, len(lines), 2):
            if i + 1 < len(lines):
                priv = lines[i].strip()
                pub = lines[i + 1].strip()
                pairs.append((priv, pub))
    return pairs

def mod_inverse(a: int, n: int) -> int:
    """Calculate modular multiplicative inverse."""
    def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y

    _, x, _ = extended_gcd(a, n)
    return (x % n + n) % n

def point_add(P1: Tuple[int, int], P2: Tuple[int, int]) -> Tuple[int, int]:
    """Add two points on secp256k1 curve."""
    if P1 == (0, 0):
        return P2
    if P2 == (0, 0):
        return P1
    
    x1, y1 = P1
    x2, y2 = P2
    
    if x1 == x2 and y1 == y2:
        # Point doubling
        if y1 == 0:
            return (0, 0)
        lam = (3 * x1 * x1) * mod_inverse(2 * y1, P) % P
    else:
        # Point addition
        if x1 == x2:
            return (0, 0)
        lam = (y2 - y1) * mod_inverse(x2 - x1, P) % P
    
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    
    return (x3, y3)

def scalar_multiply(k: int, point: Tuple[int, int]) -> Tuple[int, int]:
    """Multiply a point by a scalar on secp256k1."""
    result = (0, 0)
    addend = point
    
    while k:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1
    
    return result

def privkey_to_pubkey(privkey: int) -> Tuple[int, int]:
    """Convert private key to public key point."""
    return scalar_multiply(privkey, (G_x, G_y))

def analyze_ec_patterns(pairs: List[Tuple[str, str]]) -> None:
    """Analyze elliptic curve patterns between keys."""
    print("Analyzing elliptic curve patterns...\n")
    
    for i in range(len(pairs) - 1):
        try:
            # Decode private keys
            current_priv = base58.b58decode(pairs[i][0])[1:-4]
            next_priv = base58.b58decode(pairs[i + 1][0])[1:-4]
            
            current_priv_int = int.from_bytes(current_priv, 'big')
            next_priv_int = int.from_bytes(next_priv, 'big')
            
            # Generate public keys
            current_pub = privkey_to_pubkey(current_priv_int)
            next_pub = privkey_to_pubkey(next_priv_int)
            test_pub = privkey_to_pubkey(TEST_VALUE)
            
            print(f"\nPair {i} -> {i+1}:")
            print(f"Current private: {hex(current_priv_int)}")
            print(f"Next private:    {hex(next_priv_int)}")
            print(f"Current public:  ({hex(current_pub[0])}, {hex(current_pub[1])})")
            print(f"Next public:     ({hex(next_pub[0])}, {hex(next_pub[1])})")
            
            # Test if TEST_VALUE is involved in EC operations
            test_point = point_add(current_pub, test_pub)
            print(f"\nCurrent pub + TEST_VALUE point: ({hex(test_point[0])}, {hex(test_point[1])})")
            if test_point == next_pub:
                print("MATCH! Next public key is current + TEST_VALUE point")
            
            test_mult = scalar_multiply(TEST_VALUE, current_pub)
            print(f"Current pub * TEST_VALUE: ({hex(test_mult[0])}, {hex(test_mult[1])})")
            if test_mult == next_pub:
                print("MATCH! Next public key is current * TEST_VALUE")
            
            # Test if TEST_VALUE is a difference between private keys
            if (next_priv_int - current_priv_int) % N == TEST_VALUE:
                print("MATCH! TEST_VALUE is the difference between private keys mod N")
            
        except Exception as e:
            print(f"Error analyzing pair: {str(e)}")

def main():
    pairs = read_key_pairs("../5HpHagT65TZzG1PH3CSu63k8DbpvD8s5ip4nEB3k.vb")
    print(f"Testing with value: {hex(TEST_VALUE)}\n")
    analyze_ec_patterns(pairs[:10])  # Analyze first 10 pairs

if __name__ == "__main__":
    main() 