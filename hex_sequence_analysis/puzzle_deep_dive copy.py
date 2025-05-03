#!/usr/bin/env python3
"""
Bitcoin Puzzle Key Sequence Generator
-----------------------------------
This script generates a sequence of 159 Bitcoin private keys starting from 0x1, applying transformation rules
encoded in FULL_STRING. It derives addresses from these keys and checks them against EXPECTED_ADDRESSES.
For matching addresses, it checks the balance using the Blockchair API.

Note: The TRANSFORMATIONS dictionary contains placeholder rules. Refine these rules by analyzing the pattern
between consecutive KNOWN_SOLUTIONS and corresponding characters in FULL_STRING.
"""

import hashlib
import requests
import time
import binascii
from typing import Optional, Dict, Tuple, List

# Base58 alphabet for encoding
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

# Hardcoded custom RIPEMD-160 implementation
def rol(n, rotations, width=32):
    """Rotate left operation for RIPEMD160"""
    return ((n << rotations) | (n >> (width - rotations))) & ((1 << width) - 1)

def f(j, x, y, z):
    """RIPEMD160 compression function"""
    if j < 16: return x ^ y ^ z
    elif j < 32: return (x & y) | (~x & z)
    elif j < 48: return (x | ~y) ^ z
    elif j < 64: return (x & z) | (y & ~z)
    else: return x ^ (y | ~z)

def custom_ripemd160(data):
    """Custom RIPEMD160 implementation for Bitcoin puzzle verification"""
    h = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xc3d2e1f0]
    s = [11, 14, 15, 12, 5, 8, 7, 9, 11, 13, 14, 15, 6, 7, 9, 8,
         7, 6, 8, 9, 11, 15, 13, 14, 7, 6, 9, 8, 13, 11, 12, 14,
         12, 15, 5, 7, 9, 11, 8, 6, 13, 14, 7, 9, 12, 15, 5, 11,
         9, 14, 15, 5, 7, 6, 8, 13, 11, 12, 14, 15, 5, 8, 6, 13,
         9, 13, 6, 14, 15, 11, 7, 12, 5, 8, 13, 14, 6, 9, 15, 11]
    k = [0, 0x5a827999, 0x6ed9eba1, 0x8f1bbcdc, 0xa953fd4e]
    kp = [0x50a28be6, 0x5c4dd124, 0x6d703ef3, 0x7a6d76e9, 0]

    msg = bytearray(data)
    orig_len = len(msg) * 8
    msg.append(0x80)
    while (len(msg) * 8) % 512 != 448:
        msg.append(0)
    msg += (orig_len & 0xffffffffffffffff).to_bytes(8, "little")

    for i in range(0, len(msg), 64):
        block = msg[i:i+64]
        w = [int.from_bytes(block[j:j+4], "little") for j in range(0, 64, 4)]
        a, b, c, d, e = h
        ap, bp, cp, dp, ep = h
        for j in range(80):
            t = rol(a + f(j, b, c, d) + w[(j % 16) ^ (j // 16)] + k[j // 16], s[j]) + e
            a, b, c, d, e = e, t, b, rol(c, 10), d
            tp = rol(ap + f(79 - j, bp, cp, dp) + w[(j % 16) ^ (79 - j) // 16] + kp[j // 16], s[79 - j]) + ep
            ap, bp, cp, dp, ep = ep, tp, bp, rol(cp, 10), dp
        h = [(h[i] + x + y) & 0xffffffff for i, (x, y) in enumerate(zip((a, b, c, d, e), (ap, bp, cp, dp, ep)))]
    return bytes().join(x.to_bytes(4, "little") for x in h)


# List of 159 expected Bitcoin addresses (replace with full list as needed)
EXPECTED_ADDRESSES = [
    "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH",
    "1CUNEBjYrCn2y1SdiUMohaKUi4wpP326Lb",
    "19ZewH8Kk1PDbSNdJ97FP4EiCjTRaZMZQA",
    "1EhqbyUMvvs7BfL8goY6qcPbD6YKfPqb7e",
    "1E6NuFjCi27W5zoXg8TRdcSRq84zJeBW3k",
    "1PitScNLyp2HCygzadCh7FveTnfmpPbfp8",
    "1McVt1vMtCC7yn5b9wgX1833yCcLXzueeC",
    "1M92tSqNmQLYw33fuBvjmeadirh1ysMBxK",
    "1CQFwcjw1dwhtkVWBttNLDtqL7ivBonGPV",
    "1LeBZP5QCwwgXRtmVUvTVrraqPUokyLHqe",
    "1PgQVLmst3Z314JrQn5TNiys8Hc38TcXJu",
    "1DBaumZxUkM4qMQRt2LVWyFJq5kDtSZQot",
    "1Pie8JkxBT6MGPz9Nvi3fsPkr2D8q3GBc1",
    "1ErZWg5cFCe4Vw5BzgfzB74VNLaXEiEkhk",
    "1QCbW9HWnwQWiQqVo5exhAnmfqKRrCRsvW",
    "1BDyrQ6WoF8VN3g9SAS1iKZcPzFfnDVieY",
    "1HduPEXZRdG26SUT5Yk83mLkPyjnZuJ7Bm",
    "1GnNTmTVLZiqQfLbAdp9DVdicEnB5GoERE",
    "1NWmZRpHH4XSPwsW6dsS3nrNWfL1yrJj4w",
    "1HsMJxNiV7TLxmoF6uJNkydxPFDog4NQum",
    "14oFNXucftsHiUMY8uctg6N487riuyXs4h",
    "1CfZWK1QTQE3eS9qn61dQjV89KDjZzfNcv",
    "1L2GM8eE7mJWLdo3HZS6su1832NX2txaac",
    "1rSnXMr63jdCuegJFuidJqWxUPV7AtUf7",
    "15JhYXn6Mx3oF4Y7PcTAv2wVVAuCFFQNiP",
    "1JVnST957hGztonaWK6FougdtjxzHzRMMg",
    "128z5d7nN7PkCuX5qoA4Ys6pmxUYnEy86k",
    "12jbtzBb54r97TCwW3G1gCFoumpckRAPdY",
    "19EEC52krRUK1RkUAEZmQdjTyHT7Gp1TYT",
    "1LHtnpd8nU5VHEMkG2TMYYNUjjLc992bps",
    "1LhE6sCTuGae42Axu1L1ZB7L96yi9irEBE",
    "1FRoHA9xewq7DjrZ1psWJVeTer8gHRqEvR",
    "187swFMjz1G54ycVU56B7jZFHFTNVQFDiu",
    "1PWABE7oUahG2AFFQhhvViQovnCr4rEv7Q",
    "1PWCx5fovoEaoBowAvF5k91m2Xat9bMgwb",
    "1Be2UF9NLfyLFbtm3TCbmuocc9N1Kduci1",
    "14iXhn8bGajVWegZHJ18vJLHhntcpL4dex",
    "1HBtApAFA9B2YZw3G2YKSMCtb3dVnjuNe2",
    "122AJhKLEfkFBaGAd84pLp1kfE7xK3GdT8",
    "1EeAxcprB2PpCnr34VfZdFrkUWuxyiNEFv",
    "1L5sU9qvJeuwQUdt4y1eiLmquFxKjtHr3E",
    "1E32GPWgDyeyQac4aJxm9HVoLrrEYPnM4N",
    "1PiFuqGpG8yGM5v6rNHWS3TjsG6awgEGA1",
    "1CkR2uS7LmFwc3T2jV8C1BhWb5mQaoxedF",
    "1NtiLNGegHWE3Mp9g2JPkgx6wUg4TW7bbk",
    "1F3JRMWudBaj48EhwcHDdpeuy2jwACNxjP",
    "1Pd8VvT49sHKsmqrQiP61RsVwmXCZ6ay7Z",
    "1DFYhaB2J9q1LLZJWKTnscPWos9VBqDHzv",
    "12CiUhYVTTH33w3SPUBqcpMoqnApAV4WCF",
    "1MEzite4ReNuWaL5Ds17ePKt2dCxWEofwk",
    "1NpnQyZ7x24ud82b7WiRNvPm6N8bqGQnaS",
    "15z9c9sVpu6fwNiK7dMAFgMYSK4GqsGZim",
    "15K1YKJMiJ4fpesTVUcByoz334rHmknxmT",
    "1KYUv7nSvXx4642TKeuC2SNdTk326uUpFy",
    "1LzhS3k3e9Ub8i2W1V8xQFdB8n2MYCHPCa",
    "17aPYR1m6pVAacXg1PTDDU7XafvK1dxvhi",
    "15c9mPGLku1HuW9LRtBf4jcHVpBUt8txKz",
    "1Dn8NF8qDyyfHMktmuoQLGyjWmZXgvosXf",
    "1HAX2n9Uruu9YDt4cqRgYcvtGvZj1rbUyt",
    "1Kn5h2qpgw9mWE5jKpk8PP4qvvJ1QVy8su",
    "1AVJKwzs9AskraJLGHAZPiaZcrpDr1U6AB",
    "1Me6EfpwZK5kQziBwBfvLiHjaPGxCKLoJi",
    "1NpYjtLira16LfGbGwZJ5JbDPh3ai9bjf4",
    "16jY7qLJnxb7CHZyqBP8qca9d51gAjyXQN",
    "18ZMbwUFLMHoZBbfpCjUJQTCMCbktshgpe",
    "13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so",
    "1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9",
    "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ",
    "19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG",
    "19YZECXj3SxEZMoUeJ1yiPsw8xANe7M7QR",
    "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU",
    "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR",
    "12VVRNPi4SJqUTsp6FmqDqY5sGosDtysn4",
    "1FWGcVDK3JGzCC3WtkYetULPszMaK2Jksv",
    "1J36UjUByGroXcCvmj13U6uwaVv9caEeAt",
    "1DJh2eHFYQfACPmrvpyWc8MSTYKh7w9eRF",
    "1Bxk4CQdqL9p22JEtDfdXMsng1XacifUtE",
    "15qF6X51huDjqTmF9BJgxXdt1xcj46Jmhb",
    "1ARk8HWJMn8js8tQmGUJeQHjSE7KRkn2t8",
    "1BCf6rHUW6m3iH2ptsvnjgLruAiPQQepLe",
    "15qsCm78whspNQFydGJQk5rexzxTQopnHZ",
    "13zYrYhhJxp6Ui1VV7pqa5WDhNWM45ARAC",
    "14MdEb4eFcT3MVG5sPFG4jGLuHJSnt1Dk2",
    "1CMq3SvFcVEcpLMuuH8PUcNiqsK1oicG2D",
    "1Kh22PvXERd2xpTQk3ur6pPEqFeckCJfAr",
    "1K3x5L6G57Y494fDqBfrojD28UJv4s5JcK",
    "1PxH3K1Shdjb7gSEoTX7UPDZ6SH4qGPrvq",
    "16AbnZjZZipwHMkYKBSfswGWKDmXHjEpSf",
    "19QciEHbGVNY4hrhfKXmcBBCrJSBZ6TaVt",
    "1L12FHH2FHjvTviyanuiFVfmzCy46RRATU",
    "1EzVHtmbN4fs4MiNk3ppEnKKhsmXYJ4s74",
    "1AE8NzzgKE7Yhz7BWtAcAAxiFMbPo82NB5",
    "17Q7tuG2JwFFU9rXVj3uZqRtioH3mx2Jad",
    "1K6xGMUbs6ZTXBnhw1pippqwK6wjBWtNpL",
    "19eVSDuizydXxhohGh8Ki9WY9KsHdSwoQC",
    "15ANYzzCp5BFHcCnVFzXqyibpzgPLWaD8b",
    "18ywPwj39nGjqBrQJSzZVq2izR12MDpDr8",
    "1CaBVPrwUxbQYYswu32w7Mj4HR4maNoJSX",
    "1JWnE6p6UN7ZJBN7TtcbNDoRcjFtuDWoNL",
    "1KCgMv8fo2TPBpddVi9jqmMmcne9uSNJ5F",
    "1CKCVdbDJasYmhswB6HKZHEAnNaDpK7W4n",
    "1PXv28YxmYMaB8zxrKeZBW8dt2HK7RkRPX",
    "1AcAmB6jmtU6AiEcXkmiNE9TNVPsj9DULf",
    "1EQJvpsmhazYCcKX5Au6AZmZKRnzarMVZu",
    "1CMjscKB3QW7SDyQ4c3C3DEUHiHRhiZVib",
    "18KsfuHuzQaBTNLASyj15hy4LuqPUo1FNB",
    "15EJFC5ZTs9nhsdvSUeBXjLAuYq3SWaxTc",
    "1HB1iKUqeffnVsvQsbpC6dNi1XKbyNuqao",
    "1GvgAXVCbA8FBjXfWiAms4ytFeJcKsoyhL",
    "12JzYkkN76xkwvcPT6AWKZtGX6w2LAgsJg",
    "1824ZJQ7nKJ9QFTRBqn7z7dHV5EGpzUpH3",
    "18A7NA9FTsnJxWgkoFfPAFbQzuQxpRtCos",
    "1NeGn21dUDDeqFQ63LUFC9uDcVdGjqkxKy",
    "174SNxfqpdMGYy5YQcfLbSTK3MRNZEePoy",
    "1NLbHuJebVwUZ1XqDjsAyfTRUPwDQbemfv",
    "1MnJ6hdhvK37VLmqcdEwqC3iFxyWH2PHUV",
    "1KNRfGWw7Q9Rmwsc6NT5zsdvEb9M2Wkj5Z",
    "1PJZPzvGX19a7twf5HyD2VvNiPdHLzm9F6",
    "1GuBBhf61rnvRe4K8zu8vdQB3kHzwFqSy7",
    "17s2b9ksz5y7abUm92cHwG8jEPCzK3dLnT",
    "1GDSuiThEV64c166LUFC9uDcVdGjqkxKyh",
    "1Me3ASYt5JCTAK2XaC32RMeH34PdprrfDx",
    "1CdufMQL892A69KXgv6UNBD17ywWqYpKut",
    "1BkkGsX9ZM6iwL3zbqs7HWBV7SvosR6m8N",
    "1PXAyUB8ZoH3WD8n5zoAthYjN15yN5CVq5",
    "1AWCLZAjKbV1P7AHvaPNCKiB7ZWVDMxFiz",
    "1G6EFyBRU86sThN3SSt3GrHu1sA7w7nzi4",
    "1MZ2L1gFrCtkkn6DnTT2e4PFUTHw9gNwaj",
    "1Hz3uv3nNZzBVMXLGadCucgjiCs5W9vaGz",
    "1Fo65aKq8s8iquMt6weF1rku1moWVEd5Ua",
    "16zRPnT8znwq42q7XeMkZUhb1KqgRogyy",
    "1KrU4dHE5WrW8rhWDsTRjR21r8t3dsrS3R",
    "17uDfp5r4n441xkgLFmhNoSW1KWp6xVLD",
    "13A3JrvXmvg5w9XGvyyR4JEJqiLz8ZySY3",
    "16RGFo6hjq9ym6Pj7N5H7L1NR1rVPJyw2v",
    "1UDHPdovvR985NrWSkdWQDEQ1xuRiTALq",
    "15nf31J46iLuK1ZkTnqHo7WgN5cARFK3RA",
    "1Ab4vzG6wEQBDNQM1B2bvUz4fqXXdFk2WT",
    "1Fz63c775VV9fNyj25d9Xfw3YHE6sKCxbt",
    "1QKBaU6WAeycb3DbKbLBkX7vJiaS8r42Xo",
    "1CD91Vm97mLQvXhrnoMChhJx4TP9MaQkJo",
    "15MnK2jXPqTMURX4xC3h4mAZxyCcaWWEDD",
    "13N66gCzWWHEZBxhVxG18P8wyjEWF9Yoi1",
    "1NevxKDYuDcCh1ZMMi6ftmWwGrZKC6j7Ux",
    "19GpszRNUej5yYqxXoLnbZWKew3KdVLkXg",
    "1M7ipcdYHey2Y5RZM34MBbpugghmjaV89P",
    "18aNhurEAJsw6BAgtANpexk5ob1aGTwSeL",
    "1FwZXt6EpRT7Fkndzv6K4b4DFoT4trbMrV",
    "1CXvTzR6qv8wJ7eprzUKeWxyGcHwDYP1i2",
    "1MUJSJYtGPVGkBCTqGspnxyHahpt5Te8jy",
    "13Q84TNNvgcL3HJiqQPvyBb9m4hxjS3jkV",
    "1LuUHyrQr8PKSvbcY1v1PiuGuqFjWpDumN",
    "18192XpzzdDi2K11QVHR7td2HcPS6Qs5vg",
    "1NgVmsCCJaKLzGyKLFJfVequnFW9ZvnMLN",
    "1AoeP37TmHdFh8uN72fu9AqgtLrUwcv2wJ",
    "1FTpAbQa4h8trvhQXjXnmNhqdiGBd1oraE",
    "14JHoRAdmJg3XR4RjMDh6Wed6ft6hzbQe9",
    "19z6waranEf8CcP8FqNgdwUe1QRxvUNKBG",
    "14u4nA5sugaswb6SZgn5av2vuChdMnD9E5"
]

# Transformation string with 159 characters
FULL_STRING = "BC9EEPMMCLPDPEQBHGN4CLr5J28HLFPWBi4HE2CNE3NPFD2N5a7cAKMJHNgBPM9PK6zNCFJBDK5qG8H2JNG4zKrUD6RAbFQM58gCKEHGP28CNMAEyQ7K6C8s2G" # String needs to be 159 chars long

# Use the correct known keys from bitcoin_sequence_generator.py
# Convert hex strings to integers
RAW_KNOWN_KEYS = {
    1: "0000000000000000000000000000000000000000000000000000000000000001",
    2: "0000000000000000000000000000000000000000000000000000000000000003",
    3: "0000000000000000000000000000000000000000000000000000000000000007",
    4: "0000000000000000000000000000000000000000000000000000000000000008",
    5: "0000000000000000000000000000000000000000000000000000000000000015",
    6: "0000000000000000000000000000000000000000000000000000000000000031",
    7: "000000000000000000000000000000000000000000000000000000000000004c",
    8: "00000000000000000000000000000000000000000000000000000000000000e0",
    9: "00000000000000000000000000000000000000000000000000000000000001d3",
    10: "0000000000000000000000000000000000000000000000000000000000000202",
    11: "0000000000000000000000000000000000000000000000000000000000000483",
    12: "0000000000000000000000000000000000000000000000000000000000000a7b",
    13: "0000000000000000000000000000000000000000000000000000000000001460",
    14: "0000000000000000000000000000000000000000000000000000000000002930",
    15: "00000000000000000000000000000000000000000000000000000000000068f3",
    16: "000000000000000000000000000000000000000000000000000000000000c936",
    17: "000000000000000000000000000000000000000000000000000000000001764f",
    18: "000000000000000000000000000000000000000000000000000000000003080d",
    19: "000000000000000000000000000000000000000000000000000000000005749f",
    20: "00000000000000000000000000000000000000000000000000000000000d2c55",
    21: "00000000000000000000000000000000000000000000000000000000001ba534",
    22: "00000000000000000000000000000000000000000000000000000000002de40f",
    23: "0000000000000000000000000000000000000000000000000000000000556e52",
    24: "0000000000000000000000000000000000000000000000000000000000dc2a04",
    25: "0000000000000000000000000000000000000000000000000000000001fa5ee5",
    26: "000000000000000000000000000000000000000000000000000000000340326e",
    27: "0000000000000000000000000000000000000000000000000000000006ac3875",
    28: "000000000000000000000000000000000000000000000000000000000d916ce8",
    29: "0000000000000000000000000000000000000000000000000000000017e2551e",
    30: "000000000000000000000000000000000000000000000000000000003d94cd64",
    31: "000000000000000000000000000000000000000000000000000000007d4fe747",
    32: "00000000000000000000000000000000000000000000000000000000b862a62e",
    33: "00000000000000000000000000000000000000000000000000000001a96ca8d8",
    34: "000000000000000000000000000000000000000000000000000000034a65911d",
    35: "00000000000000000000000000000000000000000000000000000004aed21170",
    36: "00000000000000000000000000000000000000000000000000000009de820a7c",
    37: "0000000000000000000000000000000000000000000000000000001757756a93",
    38: "00000000000000000000000000000000000000000000000000000022382facd0",
    39: "0000000000000000000000000000000000000000000000000000004b5f8303e9",
    40: "000000000000000000000000000000000000000000000000000000e9ae4933d6",
    41: "00000000000000000000000000000000000000000000000000000153869acc5b",
    42: "000000000000000000000000000000000000000000000000000002a221c58d8f",
    43: "000000000000000000000000000000000000000000000000000006bd3b27c591",
    44: "00000000000000000000000000000000000000000000000000000e02b35a358f",
    45: "0000000000000000000000000000000000000000000000000000122fca143c05",
    46: "00000000000000000000000000000000000000000000000000002ec18388d544",
    47: "00000000000000000000000000000000000000000000000000006cd610b53cba",
    48: "0000000000000000000000000000000000000000000000000000ade6d7ce3b9b",
    49: "000000000000000000000000000000000000000000000000000174176b015f4d",
    50: "00000000000000000000000000000000000000000000000000022bd43c2e9354",
    51: "00000000000000000000000000000000000000000000000000075070a1a009d4",
    52: "000000000000000000000000000000000000000000000000000efae164cb9e3c",
    53: "00000000000000000000000000000000000000000000000000180788e47e326c",
    54: "00000000000000000000000000000000000000000000000000236fb6d5ad1f43",
    55: "000000000000000000000000000000000000000000000000006abe1f9b67e114",
    56: "000000000000000000000000000000000000000000000000009d18b63ac4ffdf",
    57: "00000000000000000000000000000000000000000000000001eb25c90795d61c",
    58: "00000000000000000000000000000000000000000000000002c675b852189a21",
    59: "00000000000000000000000000000000000000000000000007496cbb87cab44f",
    60: "0000000000000000000000000000000000000000000000000fc07a1825367bbe",
    61: "00000000000000000000000000000000000000000000000013c96a3742f64906",
    62: "000000000000000000000000000000000000000000000000363d541eb611abee",
    63: "0000000000000000000000000000000000000000000000007cce5efdaccf6808",
    64: "000000000000000000000000000000000000000000000000f7051f27b09112d4",
    65: "000000000000000000000000000000000000000000000001a838b13505b26867",
    66: "000000000000000000000000000000000000000000000002832ed74f2b5e35ee",
    # ... (add the rest of the known keys here)
}
KNOWN_SOLUTIONS = {k: int(v, 16) for k, v in RAW_KNOWN_KEYS.items()}

class BitcoinTools:
    """Class for secp256k1 elliptic curve operations."""
    _p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    _n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    _Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    _Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

    @staticmethod
    def point_add(p1: Optional[tuple], p2: Optional[tuple]) -> Optional[tuple]:
        """Add two points on the secp256k1 curve."""
        if p1 is None:
            return p2
        if p2 is None:
            return p1
        x1, y1 = p1
        x2, y2 = p2
        if x1 == x2 and y1 != y2:
            return None
        if x1 == x2:
            # Check for point at infinity (y1=0)
            if y1 == 0: return None
            slope = (3 * x1 * x1 * pow(2 * y1, BitcoinTools._p - 2, BitcoinTools._p)) % BitcoinTools._p
        else:
            # Check for division by zero
            if (x2 - x1) % BitcoinTools._p == 0: return None
            slope = ((y2 - y1) * pow(x2 - x1, BitcoinTools._p - 2, BitcoinTools._p)) % BitcoinTools._p
        x3 = (slope * slope - x1 - x2) % BitcoinTools._p
        y3 = (slope * (x1 - x3) - y1) % BitcoinTools._p
        return (x3, y3)

    @staticmethod
    def point_mul(k: int, point: tuple) -> Optional[tuple]:
        """Multiply a point by a scalar using double-and-add algorithm."""
        if k % BitcoinTools._n == 0 or k == 0: # Check if k is a multiple of n or zero
             return None
        result = None
        addend = point
        while k:
            if k & 1:
                result = BitcoinTools.point_add(result, addend)
            addend = BitcoinTools.point_add(addend, addend)
            # Check if addend becomes point at infinity during doubling
            if addend is None:
                 # This case can happen if the order of the point divides k
                 # For the base point G, this shouldn't happen unless k is a multiple of n
                 # which is checked above. For other points, it might.
                 break
            k >>= 1
        return result

    @staticmethod
    def privkey_to_pubkey(privkey: int, compressed: bool = False) -> Optional[bytes]:
        """Convert a private key to a public key (compressed or uncompressed)."""
        if not 1 <= privkey < BitcoinTools._n:
            # print(f"Error: Private key {hex(privkey)} out of range.") # Reduce noise
            return None
        point = BitcoinTools.point_mul(privkey, (BitcoinTools._Gx, BitcoinTools._Gy))
        if point is None:
            # print(f"Error: Point multiplication resulted in None for privkey {hex(privkey)}.") # Reduce noise
            return None
        x, y = point
        if compressed:
            prefix = b'\x02' if (y % 2 == 0) else b'\x03'
            pubkey_bytes = prefix + x.to_bytes(32, byteorder='big')
        else:
            pubkey_bytes = b'\x04' + x.to_bytes(32, byteorder='big') + y.to_bytes(32, byteorder='big')
        return pubkey_bytes

def pubkey_to_address(pubkey_bytes: bytes, version_byte: bytes = b'\x00') -> Optional[str]:
    """Derive a Bitcoin address from a public key using CUSTOM RIPEMD160."""
    try:
        sha = hashlib.sha256(pubkey_bytes).digest()
        # Use the custom RIPEMD160 implementation
        ripe = custom_ripemd160(sha)
        versioned = version_byte + ripe
        checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
        binary_address = versioned + checksum
        address = base58_encode(binary_address)
        return address
    except Exception as e:
        # print(f"Error deriving address from pubkey {pubkey_bytes.hex()}: {e}") # Reduce noise
        return None

def base58_encode(data: bytes) -> str:
    """Encode bytes to a Base58 string."""
    num = int.from_bytes(data, byteorder='big')
    encode = ''
    while num > 0:
        num, rem = divmod(num, 58)
        encode = BASE58_ALPHABET[rem] + encode
    leading_zeros = len(data) - len(data.lstrip(b'\x00'))
    encode = '1' * leading_zeros + encode
    return encode

def check_balance(address: str) -> Optional[int]:
    """Check the balance of a Bitcoin address using Blockchair API."""
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
            # print(f"    Could not retrieve balance for {address} (API response format changed?)") # Reduce noise
            return None
    except requests.exceptions.RequestException as e:
        # print(f"    Error querying Blockchair API for balance of {address}: {e}") # Reduce noise
        return None
    except Exception as e:
        # print(f"    An unexpected error occurred during balance check for {address}: {e}") # Reduce noise
        return None

# Helper to get Base58 index
def get_base58_index(char: str) -> Optional[int]:
    try:
        return BASE58_ALPHABET.index(char)
    except ValueError:
        return None

# Transformation rules based on analysis and KNOWN_SOLUTIONS
# Mapping: Character at FULL_STRING[i-1] -> Rule to get Key[i] from Key[i-1]
TRANSFORMATIONS = {
    # Transition 1->2 (char FULL_STRING[0]='B', Key1=0x1 -> Key2=0x3). Rule: k+2
    'B': lambda key, _: (key + 2) % BitcoinTools._n,

    # Transition 2->3 (char FULL_STRING[1]='C', Key2=0x3 -> Key3=0x7). Rule: k*2+1
    'C': lambda key, _: (key << 1 | 1) % BitcoinTools._n,

    # Transition 3->4 (char FULL_STRING[2]='9', Key3=0x7 -> Key4=0x8). Rule: k+1
    '9': lambda key, _: (key + 1) % BitcoinTools._n,

    # Transition 4->5 (char FULL_STRING[3]='E', Key4=0x8 -> Key5=0x15). Rule: k+13 (k+base58_idx)
    # Transition 5->6 (char FULL_STRING[4]='E', Key5=0x15 -> Key6=0x31). Need rule.
    # Note: Multiple chars might map to the same lambda, or have different rules based on position?
    'E': lambda key, base58_idx: (key + base58_idx) % BitcoinTools._n if base58_idx is not None else (key * 2) % BitcoinTools._n, # Keeping k+base58_idx for 'E' for now

    # ... Add more specific rules as identified ...

    # Tentative default rule (can be refined)
    'default': lambda key, base58_idx: (key + base58_idx) % BitcoinTools._n if base58_idx is not None else (key * 2) % BitcoinTools._n,
}

def apply_transformation(current_key: int, char: str) -> int:
    """Apply a transformation to the current private key based on the character."""
    base58_idx = get_base58_index(char)
    rule = TRANSFORMATIONS.get(char, TRANSFORMATIONS['default'])

    # Pass base58_idx to the lambda if it's defined for the rule
    try:
        # Check if the lambda accepts the base58_idx argument
        import inspect
        sig = inspect.signature(rule)
        if len(sig.parameters) == 2:
            new_key = rule(current_key, base58_idx)
        else: # Assume older lambda format or one that doesn't need index
            new_key = rule(current_key)
    except TypeError: # Fallback if inspect fails or signature mismatch
         print(f"Warning: Rule for '{char}' might not accept base58_idx. Falling back.")
         new_key = rule(current_key) # Try calling with just key
    except Exception as e:
         print(f"Error applying rule for '{char}': {e}. Using default.")
         default_rule = TRANSFORMATIONS['default']
         new_key = default_rule(current_key, base58_idx)


    # Basic fallback if rule failed or returned None (shouldn't happen with modulo N)
    if new_key is None:
        print(f"Warning: Transformation for '{char}' resulted in None. Using default (k*2 % n).")
        return (current_key * 2) % BitcoinTools._n

    return new_key

def generate_key_sequence():
    """Generate the sequence of private keys, derive addresses, and check matches."""
    print("Starting key sequence generation...")
    current_key = 0x1
    # Ensure FULL_STRING has enough characters
    # if len(FULL_STRING) < 159:
    #     print(f"Error: FULL_STRING only has {len(FULL_STRING)} characters, expected at least 159.")
    #     return

    for i in range(1, 160): # Generate keys for indices 1 to 159
        if i >= len(EXPECTED_ADDRESSES):
            print(f"Stopping at index {i} as it exceeds expected addresses array length ({len(EXPECTED_ADDRESSES)}).")
            break

        # Apply transformation for index i (using char from index i-1)
        if i > 1: 
            if i-1 < len(FULL_STRING):
                 # Get char for transition from i-1 to i
                 char = FULL_STRING[i-1] 
                 print(f"DEBUG: Index={i}, PrevKey={hex(current_key)}, Char='{char}'") 
                 # Apply transformation using char[i-1]
                 current_key = apply_transformation(current_key, char) 
                 print(f"DEBUG: Index={i}, NewKey={hex(current_key)}") 
            else:
                 # Handle out of bounds for FULL_STRING
                 print(f"Warning: Index {i-1} out of bounds...")
                 print(f"DEBUG: Index={i}, PrevKey={hex(current_key)}, Char='' (Out of bounds)")
                 # Apply default transformation
                 current_key = apply_transformation(current_key, '') 
                 print(f"DEBUG: Index={i}, NewKey (Default)={hex(current_key)}")
        # Index 1 uses the initial current_key = 0x1

        # Verify the newly calculated current_key (which should be Key[i]) against Known[i]
        if i in KNOWN_SOLUTIONS:
            if current_key == KNOWN_SOLUTIONS[i]:
                pass
            else:
                print(f"WARNING: Index {i}: Generated key {hex(current_key)} != Known solution {hex(KNOWN_SOLUTIONS[i])}")
        
        # Derive public key and address (using compressed keys)
        pubkey = BitcoinTools.privkey_to_pubkey(current_key, compressed=True)
        if not pubkey:
            # print(f"Failed to derive public key for index {i}, key {hex(current_key)}") # Reduce noise
            continue
        address = pubkey_to_address(pubkey)
        if not address:
            # print(f"Failed to derive address for index {i}") # Reduce noise
            continue

        # Check against expected address
        expected = EXPECTED_ADDRESSES[i-1]
        # print(f"Index {i}: PrivKey {hex(current_key)}, Derived: {address}, Expected: {expected}") # Reduce noise
        if address == expected:
            print(f"*** MATCH at Index {i}: Address {address} ***")
            balance = check_balance(address)
            if balance is not None and balance > 0:
                print(f"    !!! Positive Balance: {balance} satoshis !!!")
            # time.sleep(0.1) # Shorter sleep
        # else:
            # print("No match") # Reduce noise

if __name__ == "__main__":
    generate_key_sequence()