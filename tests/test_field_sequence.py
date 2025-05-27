#!/usr/bin/env python3
"""
Test harness to verify each 32-byte hex entry in verified_bitcoin_sequence.txt is less than the secp256k1 field prime
and that its 32-byte big-endian representation round-trips correctly.
"""

P = int('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F', 16)


def main():
    with open('verified_bitcoin_sequence.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            idx, rest = line.split('.', 1)
            hex_str, status = rest.strip().split(' - ', 1)
            val = int(hex_str, 16)
            if val >= P:
                result = 'FAIL_GT_P'
            else:
                out_hex = val.to_bytes(32, 'big').hex()
                result = 'OK' if out_hex == hex_str.lower() else 'MISMATCH'
            print(f"{idx.strip()}: {hex_str} -> {result}")


if __name__ == '__main__':
    main() 