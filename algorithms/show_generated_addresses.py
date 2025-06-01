#!/usr/bin/env python3
"""Generate Bitcoin addresses from the verified private key sequence and display them.

For each position (1-160):
  • Load the private key from verified_bitcoin_sequence.txt
  • Derive the public key (uncompressed & compressed)
  • Compute the address using custom RIPEMD160 (matches puzzle addresses)
  • Compare with EXPECTED_ADDRESSES from key_sequence_generator.py

Outputs a table:
  Pos | PrivateKey (hex, truncated) | Address (custom, uncompressed) | ✓ if matches expected

Note: The original puzzle addresses appear to be derived from UNCOMPRESSED public keys + custom RIPEMD160.
"""
import sys
from pathlib import Path
import hashlib, base58

sys.path.append('.')

# Import helpers from key_sequence_generator
try:
    from key_sequence_generator import (
        privkey_to_pubkey,
        pubkey_point_to_bytes,
        pubkey_to_address,
        EXPECTED_ADDRESSES,
    )
except ImportError as e:
    print(f"Failed to import from key_sequence_generator: {e}")
    sys.exit(1)

SEQUENCE_FILE = Path('verified_bitcoin_sequence.txt')


def load_sequence(path: Path):
    """Return a dict {position: privkey_int} from verified file."""
    seq = {}
    if not path.exists():
        print(f"Sequence file not found: {path}")
        return seq
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or not line[0].isdigit():
            continue
        pos_str, rest = line.split('.', 1)
        pos = int(pos_str)
        hex_key = rest.strip().split(' - ')[0].strip()
        try:
            seq[pos] = int(hex_key, 16)
        except ValueError:
            continue
    return seq


def main():
    keys = load_sequence(SEQUENCE_FILE)
    if not keys:
        print("No keys loaded from verified sequence.")
        return

    print(f"Loaded {len(keys)} verified private keys (positions {min(keys)}–{max(keys)}).\n")
    header = f"{'Pos':>3} | {'PrivateKey (hex)':<66} | {'Best-Match Address':<35} | ✓"
    print(header)
    print('-' * len(header))

    matches = 0
    for pos in sorted(keys):
        priv_int = keys[pos]
        # Derive public key point
        try:
            point = privkey_to_pubkey(priv_int)
        except Exception as e:
            print(f"{pos:3} | ERROR deriving pubkey: {e}")
            continue

        # Compressed public key bytes (02/03 + x)
        pub_bytes_comp = pubkey_point_to_bytes(point, compressed=True)

        def addr_from_pub(pub_bytes):
            sha = hashlib.sha256(pub_bytes).digest()
            ripe = hashlib.new('ripemd160', sha).digest()
            versioned = b'\x00' + ripe
            checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
            return base58.b58encode(versioned + checksum).decode()

        # Candidate addresses
        pub_unc = pubkey_point_to_bytes(point, compressed=False)
        pub_cmp = pub_bytes_comp = pubkey_point_to_bytes(point, compressed=True)

        addr_unc = addr_from_pub(pub_unc)
        addr_cmp = addr_from_pub(pub_cmp)

        # Expected address list is 0-indexed for pos-1
        expected = EXPECTED_ADDRESSES[pos - 1] if pos - 1 < len(EXPECTED_ADDRESSES) else None

        # Pick best match
        if expected in {addr_unc, addr_cmp}:
            addr_display = expected
            matches += 1
            ok = '✅'
        else:
            addr_display = addr_cmp  # show compressed result as default
            ok = '❌'

        priv_hex_short = hex(priv_int)[2:].rjust(64, '0')
        print(f"{pos:3} | {priv_hex_short} | {addr_display} | {ok}")

    print(f"\nSummary: {matches}/{len(keys)} addresses matched EXPECTED_ADDRESSES")


if __name__ == "__main__":
    main() 