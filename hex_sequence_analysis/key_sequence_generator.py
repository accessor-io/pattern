#!/usr/bin/env python3
"""
Bitcoin Puzzle Key Sequence Generator
-----------------------------------
This script attempts to generate the sequence of 159 private keys
based on a starting key and transformation rules potentially encoded
in the FULL_STRING. It verifies derived addresses against the expected
list and checks the balance of any matching address.
Uses KNOWN_SOLUTIONS to verify transformation steps.
"""

import hashlib
import requests
import time # For potential API rate limiting
from typing import Tuple, List, Dict, Optional
import ecdsa
import base58
import struct

# Expected addresses list (copied from puzzle_deep_dive.py)
EXPECTED_ADDRESSES = [
    "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH", "1CUNEBjYrCn2y1SdiUMohaKUi4wpP326Lb",
    "19ZewH8Kk1PDbSNdJ97FP4EiCjTRaZMZQA", "1EhqbyUMvvs7BfL8goY6qcPbD6YKfPqb7e",
    "1E6NuFjCi27W5zoXg8TRdcSRq84zJeBW3k", "1PitScNLyp2HCygzadCh7FveTnfmpPbfp8",
    "1McVt1vMtCC7yn5b9wgX1833yCcLXzueeC", "1M92tSqNmQLYw33fuBvjmeadirh1ysMBxK",
    "1CQFwcjw1dwhtkVWBttNLDtqL7ivBonGPV", "1LeBZP5QCwwgXRtmVUvTVrraqPUokyLHqe",
    "1PgQVLmst3Z314JrQn5TNiys8Hc38TcXJu", "1DBaumZxUkM4qMQRt2LVWyFJq5kDtSZQot",
    "1Pie8JkxBT6MGPz9Nvi3fsPkr2D8q3GBc1", "1ErZWg5cFCe4Vw5BzgfzB74VNLaXEiEkhk",
    "1QCbW9HWnwQWiQqVo5exhAnmfqKRrCRsvW", "1BDyrQ6WoF8VN3g9SAS1iKZcPzFfnDVieY",
    "1HduPEXZRdG26SUT5Yk83mLkPyjnZuJ7Bm", "1GnNTmTVLZiqQfLbAdp9DVdicEnB5GoERE",
    "1NWmZRpHH4XSPwsW6dsS3nrNWfL1yrJj4w", "1HsMJxNiV7TLxmoF6uJNkydxPFDog4NQum",
    "14oFNXucftsHiUMY8uctg6N487riuyXs4h", "1CfZWK1QTQE3eS9qn61dQjV89KDjZzfNcv",
    "1L2GM8eE7mJWLdo3HZS6su1832NX2txaac", "1rSnXMr63jdCuegJFuidJqWxUPV7AtUf7",
    "15JhYXn6Mx3oF4Y7PcTAv2wVVAuCFFQNiP", "1JVnST957hGztonaWK6FougdtjxzHzRMMg",
    "128z5d7nN7PkCuX5qoA4Ys6pmxUYnEy86k", "12jbtzBb54r97TCwW3G1gCFoumpckRAPdY",
    "19EEC52krRUK1RkUAEZmQdjTyHT7Gp1TYT", "1LHtnpd8nU5VHEMkG2TMYYNUjjLc992bps",
    "1LhE6sCTuGae42Axu1L1ZB7L96yi9irEBE", "1FRoHA9xewq7DjrZ1psWJVeTer8gHRqEvR",
    "187swFMjz1G54ycVU56B7jZFHFTNVQFDiu", "1PWABE7oUahG2AFFQhhvViQovnCr4rEv7Q",
    "1PWCx5fovoEaoBowAvF5k91m2Xat9bMgwb", "1Be2UF9NLfyLFbtm3TCbmuocc9N1Kduci1",
    "14iXhn8bGajVWegZHJ18vJLHhntcpL4dex", "1HBtApAFA9B2YZw3G2YKSMCtb3dVnjuNe2",
    "122AJhKLEfkFBaGAd84pLp1kfE7xK3GdT8", "1EeAxcprB2PpCnr34VfZdFrkUWuxyiNEFv",
    "1L5sU9qvJeuwQUdt4y1eiLmquFxKjtHr3E", "1E32GPWgDyeyQac4aJxm9HVoLrrEYPnM4N",
    "1PiFuqGpG8yGM5v6rNHWS3TjsG6awgEGA1", "1CkR2uS7LmFwc3T2jV8C1BhWb5mQaoxedF",
    "1NtiLNGegHWE3Mp9g2JPkgx6wUg4TW7bbk", "1F3JRMWudBaj48EhwcHDdpeuy2jwACNxjP",
    "1Pd8VvT49sHKsmqrQiP61RsVwmXCZ6ay7Z", "1DFYhaB2J9q1LLZJWKTnscPWos9VBqDHzv",
    "12CiUhYVTTH33w3SPUBqcpMoqnApAV4WCF", "1MEzite4ReNuWaL5Ds17ePKt2dCxWEofwk",
    "1NpnQyZ7x24ud82b7WiRNvPm6N8bqGQnaS", "15z9c9sVpu6fwNiK7dMAFgMYSK4GqsGZim",
    "15K1YKJMiJ4fpesTVUcByoz334rHmknxmT", "1KYUv7nSvXx4642TKeuC2SNdTk326uUpFy",
    "1LzhS3k3e9Ub8i2W1V8xQFdB8n2MYCHPCa", "17aPYR1m6pVAacXg1PTDDU7XafvK1dxvhi",
    "15c9mPGLku1HuW9LRtBf4jcHVpBUt8txKz", "1Dn8NF8qDyyfHMktmuoQLGyjWmZXgvosXf",
    "1HAX2n9Uruu9YDt4cqRgYcvtGvZj1rbUyt", "1Kn5h2qpgw9mWE5jKpk8PP4qvvJ1QVy8su",
    "1AVJKwzs9AskraJLGHAZPiaZcrpDr1U6AB", "1Me6EfpwZK5kQziBwBfvLiHjaPGxCKLoJi",
    "1NpYjtLira16LfGbGwZJ5JbDPh3ai9bjf4", "16jY7qLJnxb7CHZyqBP8qca9d51gAjyXQN",
    "18ZMbwUFLMHoZBbfpCjUJQTCMCbktshgpe", "13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so",
    "1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9", "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ",
    "19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG", "19YZECXj3SxEZMoUeJ1yiPsw8xANe7M7QR",
    "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU", "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR",
    "12VVRNPi4SJqUTsp6FmqDqY5sGosDtysn4", "1FWGcVDK3JGzCC3WtkYetULPszMaK2Jksv",
    "1J36UjUByGroXcCvmj13U6uwaVv9caEeAt", "1DJh2eHFYQfACPmrvpyWc8MSTYKh7w9eRF",
    "1Bxk4CQdqL9p22JEtDfdXMsng1XacifUtE", "15qF6X51huDjqTmF9BJgxXdt1xcj46Jmhb",
    "1ARk8HWJMn8js8tQmGUJeQHjSE7KRkn2t8", "1BCf6rHUW6m3iH2ptsvnjgLruAiPQQepLe",
    "15qsCm78whspNQFydGJQk5rexzxTQopnHZ", "13zYrYhhJxp6Ui1VV7pqa5WDhNWM45ARAC",
    "14MdEb4eFcT3MVG5sPFG4jGLuHJSnt1Dk2", "1CMq3SvFcVEcpLMuuH8PUcNiqsK1oicG2D",
    "1Kh22PvXERd2xpTQk3ur6pPEqFeckCJfAr", "1K3x5L6G57Y494fDqBfrojD28UJv4s5JcK",
    "1PxH3K1Shdjb7gSEoTX7UPDZ6SH4qGPrvq", "16AbnZjZZipwHMkYKBSfswGWKDmXHjEpSf",
    "19QciEHbGVNY4hrhfKXmcBBCrJSBZ6TaVt", "1L12FHH2FHjvTviyanuiFVfmzCy46RRATU",
    "1EzVHtmbN4fs4MiNk3ppEnKKhsmXYJ4s74", "1AE8NzzgKE7Yhz7BWtAcAAxiFMbPo82NB5",
    "17Q7tuG2JwFFU9rXVj3uZqRtioH3mx2Jad", "1K6xGMUbs6ZTXBnhw1pippqwK6wjBWtNpL",
    "19eVSDuizydXxhohGh8Ki9WY9KsHdSwoQC", "15ANYzzCp5BFHcCnVFzXqyibpzgPLWaD8b",
    "18ywPwj39nGjqBrQJSzZVq2izR12MDpDr8", "1CaBVPrwUxbQYYswu32w7Mj4HR4maNoJSX",
    "1JWnE6p6UN7ZJBN7TtcbNDoRcjFtuDWoNL", "1KCgMv8fo2TPBpddVi9jqmMmcne9uSNJ5F",
    "1CKCVdbDJasYmhswB6HKZHEAnNaDpK7W4n", "1PXv28YxmYMaB8zxrKeZBW8dt2HK7RkRPX",
    "1AcAmB6jmtU6AiEcXkmiNE9TNVPsj9DULf", "1EQJvpsmhazYCcKX5Au6AZmZKRnzarMVZu",
    "1CMjscKB3QW7SDyQ4c3C3DEUHiHRhiZVib", "18KsfuHuzQaBTNLASyj15hy4LuqPUo1FNB",
    "15EJFC5ZTs9nhsdvSUeBXjLAuYq3SWaxTc", "1HB1iKUqeffnVsvQsbpC6dNi1XKbyNuqao",
    "1GvgAXVCbA8FBjXfWiAms4ytFeJcKsoyhL", "12JzYkkN76xkwvcPT6AWKZtGX6w2LAgsJg",
    "1824ZJQ7nKJ9QFTRBqn7z7dHV5EGpzUpH3", "18A7NA9FTsnJxWgkoFfPAFbQzuQxpRtCos",
    "1NeGn21dUDDeqFQ63LUFC9uDcVdGjqkxKy", "174SNxfqpdMGYy5YQcfLbSTK3MRNZEePoy",
    "1NLbHuJebVwUZ1XqDjsAyfTRUPwDQbemfv", "1MnJ6hdhvK37VLmqcdEwqC3iFxyWH2PHUV",
    "1KNRfGWw7Q9Rmwsc6NT5zsdvEb9M2Wkj5Z", "1PJZPzvGX19a7twf5HyD2VvNiPdHLzm9F6",
    "1GuBBhf61rnvRe4K8zu8vdQB3kHzwFqSy7", "17s2b9ksz5y7abUm92cHwG8jEPCzK3dLnT",
    "1GDSuiThEV64c166LUFC9uDcVdGjqkxKyh", "1Me3ASYt5JCTAK2XaC32RMeH34PdprrfDx",
    "1CdufMQL892A69KXgv6UNBD17ywWqYpKut", "1BkkGsX9ZM6iwL3zbqs7HWBV7SvosR6m8N",
    "1PXAyUB8ZoH3WD8n5zoAthYjN15yN5CVq5", "1AWCLZAjKbV1P7AHvaPNCKiB7ZWVDMxFiz",
    "1G6EFyBRU86sThN3SSt3GrHu1sA7w7nzi4", "1MZ2L1gFrCtkkn6DnTT2e4PFUTHw9gNwaj",
    "1Hz3uv3nNZzBVMXLGadCucgjiCs5W9vaGz", "1Fo65aKq8s8iquMt6weF1rku1moWVEd5Ua",
    "16zRPnT8znwq42q7XeMkZUhb1KqgRogyy", "1KrU4dHE5WrW8rhWDsTRjR21r8t3dsrS3R",
    "17uDfp5r4n441xkgLFmhNoSW1KWp6xVLD", "13A3JrvXmvg5w9XGvyyR4JEJqiLz8ZySY3",
    "16RGFo6hjq9ym6Pj7N5H7L1NR1rVPJyw2v", "1UDHPdovvR985NrWSkdWQDEQ1xuRiTALq",
    "15nf31J46iLuK1ZkTnqHo7WgN5cARFK3RA", "1Ab4vzG6wEQBDNQM1B2bvUz4fqXXdFk2WT",
    "1Fz63c775VV9fNyj25d9Xfw3YHE6sKCxbt", "1QKBaU6WAeycb3DbKbLBkX7vJiaS8r42Xo",
    "1CD91Vm97mLQvXhrnoMChhJx4TP9MaQkJo", "15MnK2jXPqTMURX4xC3h4mAZxyCcaWWEDD",
    "13N66gCzWWHEZBxhVxG18P8wyjEWF9Yoi1", "1NevxKDYuDcCh1ZMMi6ftmWwGrZKC6j7Ux",
    "19GpszRNUej5yYqxXoLnbZWKew3KdVLkXg", "1M7ipcdYHey2Y5RZM34MBbpugghmjaV89P",
    "18aNhurEAJsw6BAgtANpexk5ob1aGTwSeL", "1FwZXt6EpRT7Fkndzv6K4b4DFoT4trbMrV",
    "1CXvTzR6qv8wJ7eprzUKeWxyGcHwDYP1i2", "1MUJSJYtGPVGkBCTqGspnxyHahpt5Te8jy",
    "13Q84TNNvgcL3HJiqQPvyBb9m4hxjS3jkV", "1LuUHyrQr8PKSvbcY1v1PiuGuqFjWpDumN",
    "18192XpzzdDi2K11QVHR7td2HcPS6Qs5vg", "1NgVmsCCJaKLzGyKLFJfVequnFW9ZvnMLN",
    "1AoeP37TmHdFh8uN72fu9AqgtLrUwcv2wJ", "1FTpAbQa4h8trvhQXjXnmNhqdiGBd1oraE",
    "14JHoRAdmJg3XR4RjMDh6Wed6ft6hzbQe9", "19z6waranEf8CcP8FqNgdwUe1QRxvUNKBG",
    "14u4nA5sugaswb6SZgn5av2vuChdMnD9E5"
]

# Base58 alphabet used by Bitcoin
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

# The full 159-character Base58 string - assumed to encode transformations
FULL_STRING = "BC9EEPMMCLPDPEQBHGN4CLr5J28HLFPWBi4HE2CNE3NPFD2N5a7cAKMJHNgBPM9PK6zNCFJBDK5qG8H2JNG4zKrUD6RAbFQM58gCKEHGP28CNMAEyQ7K6C8s2G"

# --- Known Solutions (Provided by User) ---
KNOWN_SOLUTIONS = {
    1: 0x1, 2: 0x3, 3: 0x7, 4: 0x8, 5: 0x15, 6: 0x31, 7: 0x4c, 8: 0xe0,
    9: 0x1d3, 10: 0x202, 11: 0x483, 12: 0xa7b, 13: 0x1460, 14: 0x2930,
    15: 0x68f3, 16: 0xc936, 17: 0x1764f, 18: 0x3080d, 19: 0x5749f,
    20: 0xd2c55, 21: 0x1ba534, 22: 0x2de40f, 23: 0x556e52, 24: 0xdc2a04,
    25: 0x1fa5ee5, 26: 0x340326e, 27: 0x6ac3875, 28: 0xd916ce8, 29: 0x17e2551e,
    30: 0x3d94cd64, 31: 0x7d4fe747, 32: 0xb862a62e, 33: 0xa96ca8d8,
    34: 0x4a65911d, 35: 0xaed21170, 36: 0x9de820a7c, 37: 0x1757756a93,
    38: 0x22382facd0, 39: 0x4b5f8303e9, 40: 0xe9ae4933d6, 41: 0x153869acc5b,
    42: 0x2a221c58d8f, 43: 0x6bd3b27c591, 44: 0xe02b35a358f, 45: 0x122fca143c05,
    46: 0x2ec18388d544, 47: 0x6cd610b53cba, 48: 0xade6d7ce3b9b, 49: 0x174176b015f4d,
    50: 0x22bd43c2e9354, 51: 0x75070a1a009d4, 52: 0xefae164cb9e3c,
    53: 0x180788e47e326c, 54: 0x236fb6d5ad1f43, 55: 0x6abe1f9b67e114,
    56: 0x9d18b63ac4ffdf, 57: 0x1eb25c90795d61c, 58: 0x2c675b852189a21,
    59: 0x7496cbb87cab44f, 60: 0xfc07a1825367bbe, 61: 0x13c96a3742f64906,
    62: 0x363d541eb611abee, 63: 0x7cce5efdaccf6808, 64: 0xf7051f27b09112d4,
    65: 0xa838b13505b26867, 66: 0x2832ed74f2b5e3ee
}


# --- Helper Functions (Copied/Adapted from puzzle_deep_dive.py) ---

def rol(n, rotations, width=32):
    return ((n << rotations) | (n >> (width - rotations))) & ((1 << width) - 1)

def f(j, x, y, z):
    if j < 16: return x ^ y ^ z
    elif j < 32: return (x & y) | (~x & z)
    elif j < 48: return (x | ~y) ^ z
    elif j < 64: return (x & z) | (y & ~z)
    else: return x ^ (y | ~z)

def custom_ripemd160(data):
    h = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xc3d2e1f0]
    s = [11, 14, 15, 12, 5, 8, 7, 9, 11, 13, 14, 15, 6, 7, 9, 8, 7, 6, 8, 9, 11, 15, 13, 14, 7, 6, 9, 8, 13, 11, 12, 14, 12, 15, 5, 7, 9, 11, 8, 6, 13, 14, 7, 9, 12, 15, 5, 11, 9, 14, 15, 5, 7, 6, 8, 13, 11, 12, 14, 15, 5, 8, 6, 13, 9, 13, 6, 14, 15, 11, 7, 12, 5, 8, 13, 14, 6, 9, 15, 11]
    k = [0, 0x5a827999, 0x6ed9eba1, 0x8f1bbcdc, 0xa953fd4e]
    kp = [0x50a28be6, 0x5c4dd124, 0x6d703ef3, 0x7a6d76e9, 0]
    msg = bytearray(data)
    orig_len = len(msg) * 8
    msg.append(0x80)
    while (len(msg) * 8) % 512 != 448: msg.append(0)
    msg += (orig_len & 0xffffffffffffffff).to_bytes(8, "little")
    for i in range(0, len(msg), 64):
        block = msg[i:i+64]
        w = [int.from_bytes(block[j:j+4], "little") for j in range(0, 64, 4)]
        a, b, c, d, e = h; ap, bp, cp, dp, ep = h
        for j in range(80):
            t = rol(a + f(j, b, c, d) + w[(j % 16) ^ (j // 16)] + k[j // 16], s[j]) + e
            a, b, c, d, e = e, t, b, rol(c, 10), d
            tp = rol(ap + f(79 - j, bp, cp, dp) + w[(j % 16) ^ (79 - j) // 16] + kp[j // 16], s[79 - j]) + ep
            ap, bp, cp, dp, ep = ep, tp, bp, rol(cp, 10), dp
        h = [(h[i] + x + y) & 0xffffffff for i, (x, y) in enumerate(zip((a, b, c, d, e), (ap, bp, cp, dp, ep)))]
    return bytes().join(x.to_bytes(4, "little") for x in h)

def base58_encode(data: bytes) -> str:
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    num = int.from_bytes(data, byteorder='big')
    encode = ''
    while num > 0:
        num, rem = divmod(num, 58)
        encode = alphabet[rem] + encode
    # Add leading '1's for zero bytes
    leading_zeros = len(data) - len(data.lstrip(b'\x00'))
    encode = '1' * leading_zeros + encode
    return encode

def base58_decode_payload(s: str) -> Optional[bytes]:
    """Decodes a Base58Check encoded string and returns the payload, verifying the checksum."""
    num = 0
    for char in s:
        if char not in BASE58_ALPHABET:
            print(f"Error: Invalid Base58 character '{char}' in '{s}'")
            return None
        num = num * 58 + BASE58_ALPHABET.index(char)

    decoded = num.to_bytes((num.bit_length() + 7) // 8, 'big')

    # Adjust for leading zeros
    pad = 0
    for char in s:
        if char == '1':
            pad += 1
        else:
            break
    full_decoded = b'\x00' * pad + decoded

    if len(full_decoded) < 5:
        print(f"Error: Base58Check string too short: {s}")
        return None

    payload = full_decoded[:-4]
    checksum = full_decoded[-4:]

    # Verify checksum
    h1 = hashlib.sha256(payload).digest()
    h2 = hashlib.sha256(h1).digest()
    expected_checksum = h2[:4]

    if checksum != expected_checksum:
        print(f"Warning: Base58 checksum mismatch for {s}. Got {checksum.hex()}, expected {expected_checksum.hex()}")
        # Return payload anyway, but warn
    return payload

# Keep the _full version for cases where we need the checksum too
def base58_decode_full(encoded_str: str) -> Optional[Tuple[bytes, bytes, bytes]]:
    """Decodes a Base58Check encoded string and returns (version+payload, payload, checksum)."""
    num = 0
    for char in encoded_str:
        if char not in BASE58_ALPHABET:
            print(f"Error: Invalid Base58 character '{char}' in '{encoded_str}'")
            return None
        num = num * 58 + BASE58_ALPHABET.index(char)

    decoded = num.to_bytes((num.bit_length() + 7) // 8, 'big')

    # Adjust for leading zeros
    pad = 0
    for char in encoded_str:
        if char == '1':
            pad += 1
        else:
            break
    full_decoded = b'\x00' * pad + decoded

    if len(full_decoded) < 5:
        print(f"Error: Base58Check string too short: {encoded_str}")
        return None

    payload_with_version = full_decoded[:-4]
    checksum = full_decoded[-4:]

    # Verify checksum
    h1 = hashlib.sha256(payload_with_version).digest()
    h2 = hashlib.sha256(h1).digest()
    expected_checksum = h2[:4]

    if checksum != expected_checksum:
        print(f"Warning: Base58 checksum mismatch for {encoded_str}. Got {checksum.hex()}, expected {expected_checksum.hex()}")
        # Return anyway, but warn

    # Assuming version byte is the first byte of the payload
    payload = payload_with_version[1:]
    return payload_with_version, payload, checksum


def pubkey_to_address(pubkey_bytes: bytes, version_byte: bytes = b'\x00', hash_func=custom_ripemd160) -> Optional[str]:
    """Derives a Bitcoin address from public key bytes using specified hash function."""
    try:
        # Ensure pubkey_bytes is bytes
        if not isinstance(pubkey_bytes, bytes):
            raise TypeError("pubkey_bytes must be bytes")
        if not pubkey_bytes:
            raise ValueError("pubkey_bytes cannot be empty")

        sha = hashlib.sha256(pubkey_bytes).digest()
        ripe = hash_func(sha)
        versioned = version_byte + ripe
        checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
        binary_address = versioned + checksum
        address = base58_encode(binary_address)
        return address
    except Exception as e:
        print(f"Error deriving address from pubkey {pubkey_bytes.hex()}: {e}")
        return None

# DEPRECATED - Use BitcoinTools.privkey_to_pubkey directly
# def privkey_to_pubkey(privkey_int):
#     point = BitcoinTools.point_mul(privkey_int, (BitcoinTools._Gx, BitcoinTools._Gy))
#     if point is None: return None
#     x, y = point
#     pubkey_bytes = b'\x04' + x.to_bytes(32, byteorder='big') + y.to_bytes(32, byteorder='big')
#     return pubkey_bytes

# --- BitcoinTools Class (Copied from puzzle_deep_dive.py) ---
class BitcoinTools:
    _p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    _n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    _Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    _Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

    @staticmethod
    def point_add(p1: Optional[Tuple[int, int]], p2: Optional[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        if p1 is None: return p2
        if p2 is None: return p1
        x1, y1 = p1; x2, y2 = p2
        if x1 == x2 and y1 != y2: return None
        if x1 == x2: slope = (3 * x1 * x1) * pow(2 * y1, BitcoinTools._p - 2, BitcoinTools._p) % BitcoinTools._p
        else: slope = (y2 - y1) * pow(x2 - x1, BitcoinTools._p - 2, BitcoinTools._p) % BitcoinTools._p
        x3 = (slope * slope - x1 - x2) % BitcoinTools._p
        y3 = (slope * (x1 - x3) - y1) % BitcoinTools._p
        return (x3, y3)

    @staticmethod
    def point_mul(k: int, point: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        result = None; addend = point
        while k:
            if k & 1: result = BitcoinTools.point_add(result, addend)
            addend = BitcoinTools.point_add(addend, addend)
            k >>= 1
        return result

    @staticmethod
    def privkey_to_pubkey(privkey: int, compressed: bool = False) -> Optional[bytes]:
        """Generates public key bytes from a private key integer."""
        if not 1 <= privkey < BitcoinTools._n:
            print(f"Error: Private key {hex(privkey)} out of range.")
            return None
        point = BitcoinTools.point_mul(privkey, (BitcoinTools._Gx, BitcoinTools._Gy))
        if point is None:
             print(f"Error: Point multiplication resulted in None for privkey {hex(privkey)}.")
             return None
        x, y = point
        if compressed:
            prefix = b'\x02' if (y % 2 == 0) else b'\x03'
            pubkey_bytes = prefix + x.to_bytes(32, byteorder='big')
        else:
            pubkey_bytes = b'\x04' + x.to_bytes(32, byteorder='big') + y.to_bytes(32, byteorder='big')
        return pubkey_bytes

# --- Balance Checking ---
def check_balance(address: str) -> Optional[int]:
    """Checks the balance of a Bitcoin address using Blockchair API."""
    try:
        url = f"https://api.blockchair.com/bitcoin/dashboards/address/{address}?limit=1"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data and data.get('data') and address in data['data']:
            balance_satoshi = data['data'][address]['address']['balance']
            print(f"    Balance check for {address}: {balance_satoshi} satoshis")
            return balance_satoshi
        else:
            print(f"    Could not retrieve balance for {address} (API response format changed?)")
            return None
    except requests.exceptions.RequestException as e:
        print(f"    Error querying Blockchair API for balance of {address}: {e}")
        return None
    except Exception as e:
        print(f"    An unexpected error occurred during balance check for {address}: {e}")
        return None

# --- NEW: Address Derivation Analysis ---
def analyze_address_derivation(private_key_int: int, target_address: str, index: int):
    """Analyzes the derivation of a target address from a known private key."""
    print(f"\n===== Analyzing Derivation for Index {index} =====")
    print(f"  Target Address: {target_address}")
    print(f"  Private Key:    {hex(private_key_int)}")

    try:
        # 1. Decode the target address
        decoded_bytes = base58_decode_full(target_address)
        print(f"  Decoded Address Bytes (Hex): {decoded_bytes.hex()}")
        
        if len(decoded_bytes) != 25:
            print("  ERROR: Decoded address length is not 25 bytes.")
            return

        version_byte = decoded_bytes[0:1]
        target_hash_payload = decoded_bytes[1:21]
        target_checksum = decoded_bytes[21:25]

        print(f"    Version Byte: {version_byte.hex()}")
        print(f"    Target Hash Payload: {target_hash_payload.hex()}")
        print(f"    Target Checksum:     {target_checksum.hex()}")

        # 2. Verify target checksum
        versioned_payload = version_byte + target_hash_payload
        h1 = hashlib.sha256(versioned_payload).digest()
        h2 = hashlib.sha256(h1).digest()
        calculated_checksum = h2[:4]
        print(f"    Calculated Checksum: {calculated_checksum.hex()}")
        if target_checksum == calculated_checksum:
            print("    Checksum Verification: MATCH")
        else:
            print("    Checksum Verification: MISMATCH")

        # 3. Derive Pubkeys from Private Key
        pubkey_uncompressed = BitcoinTools.privkey_to_pubkey(private_key_int, compressed=False)
        pubkey_compressed = BitcoinTools.privkey_to_pubkey(private_key_int, compressed=True)
        
        if not pubkey_uncompressed or not pubkey_compressed:
            print("  ERROR: Failed to derive public keys.")
            return
            
        pubkey_unc_bytes = bytes.fromhex(pubkey_uncompressed)
        pubkey_comp_bytes = bytes.fromhex(pubkey_compressed)

        # 4. Calculate Hashes using different methods
        print("  Comparing Target Hash with Derived Hashes:")
        
        # Uncompressed Pubkey Hashes
        sha_unc = hashlib.sha256(pubkey_unc_bytes).digest()
        hash_unc_std = hashlib.new('ripemd160', sha_unc).digest()
        hash_unc_custom = custom_ripemd160(sha_unc)
        print(f"    Uncompressed + SHA256 + STD RIPEMD160:  {hash_unc_std.hex()} -> Match: {hash_unc_std == target_hash_payload}")
        print(f"    Uncompressed + SHA256 + CUSTOM RIPEMD160:{hash_unc_custom.hex()} -> Match: {hash_unc_custom == target_hash_payload}")

        # Compressed Pubkey Hashes
        sha_comp = hashlib.sha256(pubkey_comp_bytes).digest()
        hash_comp_std = hashlib.new('ripemd160', sha_comp).digest()
        hash_comp_custom = custom_ripemd160(sha_comp)
        print(f"    Compressed + SHA256 + STD RIPEMD160:    {hash_comp_std.hex()} -> Match: {hash_comp_std == target_hash_payload}")
        print(f"    Compressed + SHA256 + CUSTOM RIPEMD160:  {hash_comp_custom.hex()} -> Match: {hash_comp_custom == target_hash_payload}")
        
    except ValueError as e:
        print(f"  Error during analysis: {e}")
    except Exception as e:
        print(f"  An unexpected error occurred: {e}")

# --- Transformation Logic (COMMENTED OUT - NOT USED IN THIS APPROACH) ---
# def apply_transformation(input_key_int: int, index: int) -> int:
#     """Applies the transformation based on FULL_STRING and index."""
#     # ... (Implementation omitted as we are iterating through known keys directly)
#     pass 

# --- Main Generation Logic --- (Modified to call analysis first)
def generate_key_sequence():
    """Analyzes derivation of first address, then iterates through KNOWN_SOLUTIONS..."""
    
    # --- Analyze Address 1 Derivation --- 
    if 1 in KNOWN_SOLUTIONS and len(EXPECTED_ADDRESSES) > 0:
        analyze_address_derivation(KNOWN_SOLUTIONS[1], EXPECTED_ADDRESSES[0], 1)
    else:
        print("Cannot perform initial analysis: Key 1 or Address 1 missing.")

    # --- Original Loop (Direct Check) --- 
    print("\nVerifying KNOWN_SOLUTIONS against EXPECTED_ADDRESSES (using COMPRESSED pubkeys - as per last test)...")
    found_keys_count = 0
    matching_addresses_found = 0
    positive_balances_found = 0

    # Iterate through the known solution keys
    for i in sorted(KNOWN_SOLUTIONS.keys()): # i goes from 1 to 66
        if i > len(EXPECTED_ADDRESSES):
             print(f"Warning: Index {i} from KNOWN_SOLUTIONS exceeds length of EXPECTED_ADDRESSES. Stopping.")
             break
        
        target_address = EXPECTED_ADDRESSES[i-1] # List is 0-indexed
        print(f"\n--- Processing Index {i} (Target: {target_address}) ---")

        # Get the known key for this index
        current_privkey_int = KNOWN_SOLUTIONS[i]
        print(f"  Known Private Key (Int): {current_privkey_int}")
        # print(f"  Known Private Key (Hex): {current_privkey_int.to_bytes(32, 'big').hex()}") # Optional: Less verbose

        # 1. Derive Public Key (Compressed)
        pubkey_hex = BitcoinTools.privkey_to_pubkey(current_privkey_int, compressed=True)
        if not pubkey_hex: 
            print("  ERROR: Failed to derive public key."); 
            continue # Skip to next key
        print(f"  Derived Compressed Pubkey: {pubkey_hex}")

        # 2. Derive Address
        derived_address = pubkey_to_address(pubkey_hex)
        if not derived_address: 
            print("  ERROR: Failed to derive address."); 
            continue # Skip to next key
        print(f"  Derived Address: {derived_address}")

        # 3. Compare Derived Address with Expected Address
        if derived_address == target_address:
            print(f"  *** MATCH FOUND: Derived address matches expected address for Index {i}! ***")
            matching_addresses_found += 1
            # Check balance only if address matches
            balance = check_balance(derived_address)
            if balance is not None and balance > 0:
                positive_balances_found += 1
            # time.sleep(0.5) # Optional delay for API rate limiting
        else:
            print(f"  MISMATCH: Derived address does not match expected address for Index {i}.")
            # print(f"    Expected: {target_address}") # Uncomment for detailed mismatch info
        
        found_keys_count +=1 # Count successfully processed keys

    print("\nVerification complete.")
    print(f"Processed {found_keys_count} keys from KNOWN_SOLUTIONS.")
    print(f"Found {matching_addresses_found} derived addresses matching the corresponding entry in EXPECTED_ADDRESSES.")
    if positive_balances_found > 0:
        print(f"*** Found {positive_balances_found} matching addresses with a positive balance! ***")
    else:
        print("No positive balances found on any matching addresses.")

def reverse_analyze_address1():
    """Decodes the first address and compares its payload hash with derivations from key 1."""
    target_address = "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH"
    private_key = 1
    print(f"\n--- Reverse Analysis for Address 1 ({target_address}) ---")
    print(f"Using Private Key: {hex(private_key)}")

    # 1. Decode the target address
    decoded_data = base58_decode_full(target_address)
    if not decoded_data:
        print("Failed to decode target address.")
        return
    payload_with_version, payload_hash, actual_checksum = decoded_data
    version_byte = payload_with_version[:1]

    print(f"  Decoded Address:")
    print(f"    - Full Decoded (hex): {payload_with_version.hex() + actual_checksum.hex()}")
    print(f"    - Version Byte (hex): {version_byte.hex()}")
    print(f"    - Payload Hash (RIPEMD160) (hex): {payload_hash.hex()}")
    print(f"    - Actual Checksum (hex): {actual_checksum.hex()}")

    # 2. Verify checksum (already done by base58_decode_full, but double-check logic)
    h1 = hashlib.sha256(payload_with_version).digest()
    h2 = hashlib.sha256(h1).digest()
    expected_checksum = h2[:4]
    print(f"    - Expected Checksum (hex): {expected_checksum.hex()}")
    if actual_checksum == expected_checksum:
        print(f"    - Checksum: OK")
    else:
        # This was already printed by base58_decode_full
        print(f"    - Checksum: MISMATCH (Should have been warned above)")


    # 3. Get public keys for private key 1
    pubkey_uncompressed = BitcoinTools.privkey_to_pubkey(private_key, compressed=False)
    pubkey_compressed = BitcoinTools.privkey_to_pubkey(private_key, compressed=True)

    if not pubkey_uncompressed or not pubkey_compressed:
        print("Failed to generate public keys for key 1.")
        return

    print(f"  Public Keys for PrivKey {hex(private_key)}:")
    print(f"    - Uncompressed: {pubkey_uncompressed.hex()}")
    print(f"    - Compressed:   {pubkey_compressed.hex()}")

    # 4. Calculate hashes of public keys (Standard and Custom RIPEMD160)
    sha_unc = hashlib.sha256(pubkey_uncompressed).digest()
    sha_comp = hashlib.sha256(pubkey_compressed).digest()

    std_ripe_unc = hashlib.new('ripemd160', sha_unc).digest()
    std_ripe_comp = hashlib.new('ripemd160', sha_comp).digest()
    custom_ripe_unc = custom_ripemd160(sha_unc)
    custom_ripe_comp = custom_ripemd160(sha_comp)

    print(f"  Calculated Hashes:")
    print(f"    - Standard RIPEMD160 (Uncompressed): {std_ripe_unc.hex()}")
    print(f"    - Standard RIPEMD160 (Compressed):   {std_ripe_comp.hex()}")
    print(f"    - Custom RIPEMD160 (Uncompressed):   {custom_ripe_unc.hex()}")
    print(f"    - Custom RIPEMD160 (Compressed):     {custom_ripe_comp.hex()}")


    # 5. Compare calculated hashes with the decoded payload hash
    print(f"  Comparison with Target Payload Hash ({payload_hash.hex()}):")
    match = False
    if payload_hash == std_ripe_unc:
        print("    - MATCH: Standard RIPEMD160 (Uncompressed)")
        match = True
    if payload_hash == std_ripe_comp:
        print("    - MATCH: Standard RIPEMD160 (Compressed)")
        match = True
    if payload_hash == custom_ripe_unc:
        print("    - MATCH: Custom RIPEMD160 (Uncompressed)")
        match = True
    if payload_hash == custom_ripe_comp:
        print("    - MATCH: Custom RIPEMD160 (Compressed)")
        match = True

    if not match:
        print("    - NO MATCH found between target payload hash and calculated hashes.")

    # 6. Try deriving the address using the calculated hashes and compare
    print(f"  Address Derivation Comparison:")
    addr_std_unc = base58_encode(version_byte + std_ripe_unc + hashlib.sha256(hashlib.sha256(version_byte + std_ripe_unc).digest()).digest()[:4])
    addr_std_comp = base58_encode(version_byte + std_ripe_comp + hashlib.sha256(hashlib.sha256(version_byte + std_ripe_comp).digest()).digest()[:4])
    addr_custom_unc = base58_encode(version_byte + custom_ripe_unc + hashlib.sha256(hashlib.sha256(version_byte + custom_ripe_unc).digest()).digest()[:4])
    addr_custom_comp = base58_encode(version_byte + custom_ripe_comp + hashlib.sha256(hashlib.sha256(version_byte + custom_ripe_comp).digest()).digest()[:4])

    print(f"    - Target Address:            {target_address}")
    print(f"    - Derived (Std Unc):         {addr_std_unc}")
    print(f"    - Derived (Std Comp):        {addr_std_comp}")
    print(f"    - Derived (Custom Unc):      {addr_custom_unc}")
    print(f"    - Derived (Custom Comp):     {addr_custom_comp}")

    print(f"--- End Reverse Analysis for Address 1 ---")


# --- Main Execution ---
if __name__ == "__main__":
    # Optionally, run the full sequence generation:
    # print("Starting key sequence generation and analysis...")
    # generate_key_sequence()
    # print("\nFinished key sequence generation and analysis.")

    # Run the reverse analysis for the first address:
    reverse_analyze_address1()

    # Optionally, run the original analysis loop or specific parts
    # print("\n--- Original Analysis Loop ---")
    # for i, (priv_hex, expected_addr) in enumerate(KNOWN_SOLUTIONS.items()):
    #     if i < 32: # Limit analysis for brevity
    #         analyze_address_derivation(int(priv_hex, 16), expected_addr)
    pass # Keep the script runnable without the loop for now 