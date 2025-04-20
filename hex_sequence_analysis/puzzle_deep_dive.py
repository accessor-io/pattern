#!/usr/bin/env python3
"""
Bitcoin Puzzle Deep Dive Analysis
-------------------------------
This script performs deeper analysis based on the decoded patterns:
1. Analyzes segments of the 159-character Base58 string delimited by '8' (BEL).
2. Analyzes the RIPEMD-160 payloads of the 159 target addresses.
3. Searches for transactions involving 21.50 BTC potentially linked to the puzzle.
4. Derives address from combined segment data.
5. Derives address from the embedded WIF-like key.
6. Compares actual vs expected checksum for the embedded WIF-like key.
"""

import base64
import binascii
import requests
import re
import hashlib
from typing import Tuple, List, Dict, Optional # Added for BitcoinTools typing

# Import addresses from the verifier script - **REMOVED IMPORT**
# from bitcoin_puzzle_verifier import EXPECTED_ADDRESSES

# **ADDED ADDRESS LIST DIRECTLY**
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

# Base58 alphabet (used for decoding addresses)
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

# The full 159-character Base58 string
FULL_STRING = "BC9EEPMMCLPDPEQBHGN4CLr5J28HLFPWBi4HE2CNE3NPFD2N5a7cAKMJHNgBPM9PK6zNCFJBDK5qG8H2JNG4zKrUD6RAbFQM58gCKEHGP28CNMAEyQ7K6C8s2G"

# Roman numeral mapping
ROMAN_MAP = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}

# **ADDED custom_ripemd160 function**
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

# **ADDED base58_encode function**
def base58_encode(data: bytes) -> str:
    """Encode data in Base58Check format"""
    # Base58 character set
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    
    # Convert to integer
    num = int.from_bytes(data, byteorder='big')
    
    # Encode to Base58
    encode = ''
    while num > 0:
        num, rem = divmod(num, 58)
        encode = alphabet[rem] + encode
    
    # Add leading zeros (1 in Base58)
    for byte in data:
        if byte == 0:
            encode = '1' + encode
        else:
            break
    
    return encode

# **ADDED pubkey_to_address function**
def pubkey_to_address(pubkey_hex: str) -> str:
    """Convert public key hex to Bitcoin address using custom RIPEMD160."""
    try:
        pubkey_bytes = bytes.fromhex(pubkey_hex)
        
        # Hash public key
        sha = hashlib.sha256(pubkey_bytes).digest()
        ripe = custom_ripemd160(sha) # Use custom RIPEMD160
        
        # Add version byte (0x00 for Bitcoin mainnet)
        versioned = b'\x00' + ripe
        
        # Double SHA-256 for checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
        
        # Concatenate versioned hash and checksum
        binary_address = versioned + checksum
        
        # Base58 encode
        address = base58_encode(binary_address)
        
        return address
    except Exception as e:
        print(f"Error deriving address: {e}")
        return None

def base58_decode(s):
    """Decodes a Base58Check encoded string to bytes, returning ONLY payload."""
    num = 0
    for char in s:
        num *= 58
        if char not in BASE58_ALPHABET:
            raise ValueError(f"Invalid Base58 character: {char}")
        num += BASE58_ALPHABET.index(char)
    
    decoded = num.to_bytes((num.bit_length() + 7) // 8, 'big')
    
    pad = 0
    for char in s:
        if char == '1': pad += 1
        else: break
    
    full_decoded = b'\x00' * pad + decoded
    
    if len(full_decoded) < 5: raise ValueError("Base58Check string too short")
         
    payload = full_decoded[:-4]
    checksum = full_decoded[-4:]
    
    h1 = hashlib.sha256(payload).digest()
    h2 = hashlib.sha256(h1).digest()
    
    if h2[:4] != checksum:
        print(f"Warning: Base58 checksum mismatch for {s}")
        
    return payload # Return only payload

# **ADDED function to get FULL decoded bytes including checksum**
def base58_decode_full(s):
    """Decodes a Base58Check encoded string, returns FULL bytes (payload+checksum)."""
    num = 0
    for char in s:
        num *= 58
        if char not in BASE58_ALPHABET:
            raise ValueError(f"Invalid Base58 character: {char}")
        num += BASE58_ALPHABET.index(char)
    
    decoded = num.to_bytes((num.bit_length() + 7) // 8, 'big')
    
    pad = 0
    for char in s:
        if char == '1': pad += 1
        else: break
        
    full_decoded = b'\x00' * pad + decoded
    
    if len(full_decoded) < 5: raise ValueError("Base58Check string too short")
    
    # We don't validate checksum here, just return the full bytes
    return full_decoded

def roman_to_int(s):
    """Convert a Roman numeral string to an integer."""
    result = 0
    prev_value = 0
    for char in reversed(s):
        value = ROMAN_MAP.get(char.upper())
        if value is None:
            return None  # Not a valid Roman numeral character
        if value < prev_value:
            result -= value
        else:
            result += value
        prev_value = value
    return result

def decode_hex_key(hex_string):
    """Placeholder for the decode_hex_key function - attempts ASCII decoding."""
    try:
        return bytes.fromhex(hex_string).decode('ascii', errors='replace')
    except ValueError:
        return "[Invalid Hex]"
    except Exception as e:
        return f"[Decoding Error: {e}]"

def analyze_segments(full_string):
    """Splits the string by '8' (BEL) and analyzes each segment."""
    print("\n===== 1. Segment Analysis (Splitting by '8' / BEL) =====")
    segments = full_string.split("8")
    print(f"Found {len(segments)} segments:")
    
    for i, segment in enumerate(segments):
        print(f"\n--- Segment {i+1}: '{segment}' ---")
        
        # Test 1: Decode as Base64
        try:
            # Attempt decoding even if padding seems wrong for puzzle strings
            padding_needed = (4 - len(segment) % 4) % 4
            padded_segment = segment + '=' * padding_needed
            decoded_b64 = base64.b64decode(padded_segment, validate=False)
            print(f"  - Base64 Decoded (Hex): {decoded_b64.hex()}")
            try:
                 print(f"  - Base64 Decoded (ASCII): {decoded_b64.decode('ascii', errors='replace')}")
            except Exception:
                 print("  - Base64 Decoded (ASCII): Contains non-ASCII or invalid sequence")
        except (binascii.Error, ValueError) as e:
            print(f"  - Base64 Decode Error: {e}")
            
        # Test 2: Decode as Hex
        try:
            decoded_hex = bytes.fromhex(segment)
            print(f"  - Hex Decoded (ASCII): {decoded_hex.decode('ascii', errors='replace')}")
        except ValueError:
            print("  - Hex Decode: Not valid hex")
            
        # Test 3: Check for Roman numerals
        roman_chars = ''.join(filter(lambda char: char.upper() in ROMAN_MAP, segment))
        if roman_chars:
            print(f"  - Roman Numeral Chars Found: '{roman_chars}'")
            value = roman_to_int(roman_chars)
            if value is not None:
                 print(f"    - Interpreted Value: {value}")
            else:
                 print("    - Invalid sequence for direct interpretation")
        else:
            print("  - Roman Numerals: None found")

def analyze_payloads():
    """Analyzes the RIPEMD-160 payloads of the target addresses."""
    print("\n===== 2. Address Payload Analysis ====")
    print("Decoding RIPEMD-160 payloads (first 20 bytes after version) from addresses:")
    
    found_patterns = 0
    for i, addr in enumerate(EXPECTED_ADDRESSES):
        try:
            decoded_addr = base58_decode(addr)
            # Payload is typically bytes 1-21 (excluding version byte)
            if len(decoded_addr) >= 21:
                 payload = decoded_addr[1:21]
                 payload_hex = payload.hex()
                 decoded_payload_ascii = decode_hex_key(payload_hex)
                 
                 # Look for interesting patterns (e.g., control chars, printable ASCII)
                 control_chars_found = any(0 <= byte < 32 or byte == 127 for byte in payload)
                 printable_found = any(32 <= byte < 127 for byte in payload)
                 
                 if control_chars_found or printable_found:
                      print(f"  - {addr} (Idx {i+1}):")
                      print(f"    - Payload Hex: {payload_hex}")
                      print(f"    - Payload Decoded ASCII: {decoded_payload_ascii}")
                      if control_chars_found:
                          print(f"      * Contains control characters.")
                      if printable_found:
                           print(f"      * Contains printable ASCII.")
                      found_patterns += 1
            else:
                 print(f"  - {addr} (Idx {i+1}): Error - Decoded address too short ({len(decoded_addr)} bytes)")
                 
        except ValueError as e:
            print(f"  - {addr} (Idx {i+1}): Error decoding Base58 - {e}")
            
    if found_patterns == 0:
         print("No obvious patterns (like control characters or printable ASCII) found in payloads.")
    else:
         print(f"Found potential patterns in {found_patterns} address payloads.")

def search_transactions():
    """Searches for transactions involving 21.50 BTC."""
    print("\n===== 3. Transaction Search (21.50 BTC) =====")
    target_satoshi_value = 2150000000
    print(f"Searching for transactions with output value {target_satoshi_value} satoshis...")
    
    try:
        # Refined query to look for outputs with the specific value
        url = f"https://api.blockchair.com/bitcoin/outputs?q=value({target_satoshi_value})&limit=10"
        response = requests.get(url, timeout=15)
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json()
        
        found_count = 0
        if data and 'data' in data and data['data']:
            print(f"Found {len(data['data'])} outputs with value 21.50 BTC (showing up to 10):")
            for output in data['data']:
                 recipient = output.get('recipient')
                 tx_hash = output.get('transaction_hash')
                 print(f"  - TX Hash: {tx_hash}, Recipient: {recipient}")
                 if recipient in EXPECTED_ADDRESSES:
                     print(f"    *** MATCH FOUND: Recipient {recipient} is in the puzzle list! ***")
                     found_count += 1
                 else:
                     # Optional: Check if recipient is related (e.g., derived differently)
                     pass 
            if found_count == 0:
                 print("None of the recipients in the first 10 results match the puzzle addresses.")
        else:
            print("No outputs found matching the exact value query (or API limitations).")
            
    except requests.exceptions.RequestException as e:
        print(f"Error querying Blockchair API: {e}")
    except Exception as e:
        print(f"An error occurred during transaction search: {e}")

# **ADDED function to test combined key**
def analyze_combined_key():
    """Derives address from combined hex of segments 1 & 2."""
    print("\n===== 4. Combined Segment Key Analysis =====")
    # Hex from Segments 1 & 2 (Base64 decoded), minus last byte ('a8')
    potential_pubkey_hex = "042f4410f30c08b3c33c44011c637808baf9271cb14f5818b81c4d82344dcd3c50f63796bb70028c24736004f33d3caeb33421490432b9"
    print(f"Potential Pubkey (65 bytes): {potential_pubkey_hex}")
    
    derived_address = pubkey_to_address(potential_pubkey_hex)
    
    if derived_address:
        print(f"Derived Address: {derived_address}")
        if derived_address in EXPECTED_ADDRESSES:
            idx = EXPECTED_ADDRESSES.index(derived_address)
            print(f"*** MATCH FOUND: This address is Index {idx+1} in the puzzle list! ***")
        else:
            print("This address is NOT in the puzzle list.")
    else:
        print("Failed to derive address from this key.")

# **ADDED BitcoinTools class for privkey_to_pubkey**
# Based on implementation from bitcoin_puzzle_verifier.py
class BitcoinTools:
    _p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    _n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    _Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    _Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

    @staticmethod
    def point_add(p1: Optional[Tuple[int, int]], p2: Optional[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        if p1 is None: return p2
        if p2 is None: return p1
        x1, y1 = p1
        x2, y2 = p2
        if x1 == x2 and y1 != y2: return None
        if x1 == x2:
            slope = (3 * x1 * x1) * pow(2 * y1, BitcoinTools._p - 2, BitcoinTools._p) % BitcoinTools._p
        else:
            slope = (y2 - y1) * pow(x2 - x1, BitcoinTools._p - 2, BitcoinTools._p) % BitcoinTools._p
        x3 = (slope * slope - x1 - x2) % BitcoinTools._p
        y3 = (slope * (x1 - x3) - y1) % BitcoinTools._p
        return (x3, y3)

    @staticmethod
    def point_mul(k: int, point: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        result = None
        addend = point
        while k:
            if k & 1: result = BitcoinTools.point_add(result, addend)
            addend = BitcoinTools.point_add(addend, addend)
            k >>= 1
        return result

    @staticmethod
    def privkey_to_pubkey(privkey: int, compressed: bool = False) -> Optional[str]: # Default to uncompressed for this puzzle
        if not 1 <= privkey < BitcoinTools._n: return None
        point = BitcoinTools.point_mul(privkey, (BitcoinTools._Gx, BitcoinTools._Gy))
        if point is None: return None
        x, y = point
        if compressed:
            prefix = b'\x02' if y % 2 == 0 else b'\x03'
            pubkey = prefix + x.to_bytes(32, byteorder='big')
        else:
            pubkey = b'\x04' + x.to_bytes(32, byteorder='big') + y.to_bytes(32, byteorder='big')
        return pubkey.hex()

# **ADDED function to test embedded WIF key**
def analyze_embedded_wif():
    """Derives address from the embedded WIF-like key found in the string."""
    print("\n===== 5. Embedded WIF Key Analysis =====")
    # Private key hex discovered from WIF string at index 23
    private_key_hex = "1ae227d5e80d1da318223a11a42e667782df93eeb4f4d759ffa56cfaca06fcb3"
    print(f"Potential Private Key (Hex): {private_key_hex}")
    
    try:
        private_key_int = int(private_key_hex, 16)
        
        # Derive uncompressed public key
        pubkey_hex = BitcoinTools.privkey_to_pubkey(private_key_int, compressed=False)
        
        if pubkey_hex:
            print(f"Derived Uncompressed Pubkey: {pubkey_hex}")
            derived_address = pubkey_to_address(pubkey_hex)
            if derived_address:
                print(f"Derived Address: {derived_address}")
                if derived_address in EXPECTED_ADDRESSES:
                    idx = EXPECTED_ADDRESSES.index(derived_address)
                    print(f"*** MATCH FOUND: This address is Index {idx+1} in the puzzle list! ***")
                else:
                    print("This address is NOT in the puzzle list.")
            else:
                print("Failed to derive address from public key.")
        else:
            print("Failed to derive public key from private key.")
            
    except ValueError as e:
        print(f"Error converting private key hex: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# **ADDED function to analyze WIF checksum**
def analyze_wif_checksum():
    """Compares actual vs expected checksum for the embedded WIF key."""
    print("\n===== 6. Embedded WIF Checksum Analysis =====")
    wif_candidate = "5J28HLFPWBi4HE2CNE3NPFD2N5a7cAKMJHNgBPM9PK6zNCFJBDK"
    print(f"Analyzing WIF candidate: {wif_candidate}")
    
    try:
        full_decoded_bytes = base58_decode_full(wif_candidate)
        
        if len(full_decoded_bytes) == 37: # 1 byte version + 32 key + 4 checksum
            payload = full_decoded_bytes[:-4]
            actual_checksum = full_decoded_bytes[-4:]
            
            # Calculate expected checksum
            h1 = hashlib.sha256(payload).digest()
            expected_checksum = hashlib.sha256(h1).digest()[:4]
            
            print(f"  Payload (Hex): {payload.hex()}")
            print(f"  Actual Checksum (Hex):   {actual_checksum.hex()}")
            print(f"  Expected Checksum (Hex): {expected_checksum.hex()}")
            
            if actual_checksum == expected_checksum:
                print("  Checksum MATCHES (Unexpected based on previous warning!)")
            else:
                print("  Checksum MISMATCH confirmed.")
                # Calculate XOR difference
                xor_diff = bytes(a ^ b for a, b in zip(actual_checksum, expected_checksum))
                print(f"  Checksum Difference (XOR): {xor_diff.hex()}")

                # --- Apply XOR difference to the private key ---
                if len(payload) == 33 and payload[0] == 0x80: # Check payload length and version byte
                    private_key_bytes = payload[1:] # Get the 32 bytes of the private key
                    xor_mask = (xor_diff * 8) # Repeat the 4-byte XOR diff 8 times

                    # Apply XOR
                    new_private_key_bytes = bytes(a ^ b for a, b in zip(private_key_bytes, xor_mask))
                    new_private_key_int = int.from_bytes(new_private_key_bytes, 'big')

                    print(f"  Applying Checksum XOR to Private Key...")
                    print(f"    Original Private Key (Hex): {private_key_bytes.hex()}")
                    print(f"    XOR Mask (Checksum Diff * 8): {xor_mask.hex()}")
                    print(f"    New Potential Private Key (Hex): {new_private_key_bytes.hex()}")

                    # Derive new pubkey and address
                    new_pubkey_hex = BitcoinTools.privkey_to_pubkey(new_private_key_int, compressed=False)
                    if new_pubkey_hex:
                        print(f"    Derived New Uncompressed Pubkey: {new_pubkey_hex}")
                        new_derived_address = pubkey_to_address(new_pubkey_hex)
                        if new_derived_address:
                            print(f"    Derived New Address: {new_derived_address}")
                            if new_derived_address in EXPECTED_ADDRESSES:
                                idx = EXPECTED_ADDRESSES.index(new_derived_address)
                                print(f"    *** MATCH FOUND: This address is Index {idx+1} in the puzzle list! ***")
                            else:
                                print("    This address is NOT in the puzzle list.")
                        else:
                            print("    Failed to derive address from new public key.")
                    else:
                        print("    Failed to derive new public key from new private key.")
                else:
                    print("  Error: Payload format unexpected, cannot extract private key for XOR.")
                # --- End of XOR application ---

        else:
            print(f"  Error: Decoded length is {len(full_decoded_bytes)}, expected 37 for WIF.")
            
    except ValueError as e:
        print(f"  Error decoding Base58: {e}")
    except Exception as e:
        print(f"  An unexpected error occurred: {e}")

def main():
    """Run all analysis steps."""
    analyze_segments(FULL_STRING)
    analyze_payloads()
    search_transactions()
    analyze_combined_key()
    analyze_embedded_wif()
    analyze_wif_checksum() # **ADDED call to new function**

if __name__ == "__main__":
    main() 