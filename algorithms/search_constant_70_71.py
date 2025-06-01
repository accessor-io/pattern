#!/usr/bin/env python3
"""
Brute-force additive constant Δ for transition 70 → 71.

k70 is known (position 70).  We need Δ such that
    hash160(CompressedPubKey(k70 + Δ)) matches the hash160 of the known
    address 1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU.

The script searches a window around the current best guess (≈9.704e17)
with adjustable step size.  If found, it prints Δ and the resulting
private key for position 71.
"""
import sys, time, hashlib, base58
sys.path.append('.')
from key_sequence_generator import privkey_to_pubkey, pubkey_point_to_bytes

# --- constants ------------------------------------------------------------
# private key at position 70 (decimal / hex from verified list)
K70_HEX = '349b84b6431a6c4ef1'  # 70th key in hex (from verified list)
K70 = int(K70_HEX, 16)

# known Bitcoin address for position 71
ADDRESS_71 = '1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU'

# predicted constant from earlier analysis
PREDICTED_DELTA = 970_436_974_005_023_690_483

# search parameters (edit as needed)
WINDOW  = 10**10          # ± window around prediction (default 10 B)
STEP    = 100_000         # step size (default 1e5)
PROGRESS_EVERY = 10_000    # print a status line every N iterations

# -------------------------------------------------------------------------
ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def base58_decode_full(s: str) -> bytes:
    """Return full decoded bytes (with leading-zero padding)"""
    n = 0
    for c in s:
        n = n * 58 + ALPHABET.index(c)
    raw = n.to_bytes((n.bit_length() + 7) // 8, 'big')
    pad = 0
    for c in s:
        if c == '1':
            pad += 1
        else:
            break
    return b'\x00' * pad + raw

def hash160_of_compressed_pub(priv_int: int) -> bytes:
    pt = privkey_to_pubkey(priv_int)
    comp = pubkey_point_to_bytes(pt, compressed=True)
    sha = hashlib.sha256(comp).digest()
    return hashlib.new('ripemd160', sha).digest()

# target hash160 for address 71
FULL_DEC = base58_decode_full(ADDRESS_71)
TARGET_HASH160 = FULL_DEC[1:-4]

print('k70  =', hex(K70))
print('addr71 hash160 =', TARGET_HASH160.hex())
print('pred Δ =', PREDICTED_DELTA)
print(f'searching Δ in [pred-W, pred+W] with step {STEP:,}\n')

start_delta = PREDICTED_DELTA - WINDOW
end_delta   = PREDICTED_DELTA + WINDOW

start_time = time.time()
tried = 0
found = None
for delta in range(start_delta, end_delta + 1, STEP):
    tried += 1
    k_candidate = (K70 + delta) % (2**256)
    if hash160_of_compressed_pub(k_candidate) == TARGET_HASH160:
        found = delta
        break
    if tried % PROGRESS_EVERY == 0:
        rate = tried / (time.time() - start_time)
        pct  = 100 * (delta - start_delta) / (end_delta - start_delta)
        print(f"[{pct:5.1f}%] tested {tried:,}  |  {rate:,.0f} per sec", end="\r", flush=True)

elapsed = time.time() - start_time
print(f'Tested {tried:,} candidates in {elapsed:.2f} s')
if found is not None:
    print('\nFOUND Δ  =', found)
    print('k71     =', hex((K70 + found) % (2**256)))
else:
    print('\nNo match in this window.  Increase WINDOW or STEP resolution.') 