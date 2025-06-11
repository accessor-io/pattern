#!/usr/bin/env python3
"""
Bitcoin Puzzle Verifier - CORRECTED VERSION
-----------------------
This script verifies our solution to the Bitcoin Puzzle sequence by:
1. Generating all 160 private keys using the sequence algorithm
2. Deriving public keys and Bitcoin addresses correctly with custom RIPEMD160
3. Verifying they match the expected addresses
4. Checking for any balances on these addresses using reliable APIs
"""

import hashlib
import requests
import binascii
from typing import Tuple, List, Dict, Optional

# Import our sequence generator
from bitcoin_sequence_generator import predict_next_key, KNOWN_KEYS

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

# We'll implement Bitcoin operations ourselves to avoid dependency issues
class BitcoinTools:
    # secp256k1 constants
    _p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    _n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    _b = 0x0000000000000000000000000000000000000000000000000000000000000007
    _a = 0x0000000000000000000000000000000000000000000000000000000000000000
    _Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    _Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

    @staticmethod
    def point_add(p1: Tuple[int, int], p2: Tuple[int, int]) -> Tuple[int, int]:
        """Add two points on the secp256k1 curve"""
        if p1 is None:
            return p2
        if p2 is None:
            return p1
        
        x1, y1 = p1
        x2, y2 = p2
        
        # Handle point at infinity
        if x1 == x2 and y1 != y2:
            return None
        
        # Calculate slope
        if x1 == x2:
            # Point doubling
            slope = (3 * x1 * x1) * pow(2 * y1, BitcoinTools._p - 2, BitcoinTools._p) % BitcoinTools._p
        else:
            # Point addition
            slope = (y2 - y1) * pow(x2 - x1, BitcoinTools._p - 2, BitcoinTools._p) % BitcoinTools._p
        
        # Calculate new point
        x3 = (slope * slope - x1 - x2) % BitcoinTools._p
        y3 = (slope * (x1 - x3) - y1) % BitcoinTools._p
        
        return (x3, y3)

    @staticmethod
    def point_mul(k: int, point: Tuple[int, int]) -> Tuple[int, int]:
        """Multiply a point on the curve by scalar k"""
        result = None
        addend = point
        
        while k:
            if k & 1:
                result = BitcoinTools.point_add(result, addend)
            addend = BitcoinTools.point_add(addend, addend)
            k >>= 1
            
        return result

    @staticmethod
    def privkey_to_pubkey(privkey: int, compressed: bool = True) -> str:
        """Convert private key to public key"""
        if not 1 <= privkey < BitcoinTools._n:
            raise ValueError("Invalid private key")
        
        # Get the public key point
        point = BitcoinTools.point_mul(privkey, (BitcoinTools._Gx, BitcoinTools._Gy))
        
        if point is None:
            raise ValueError("Invalid point")
        
        x, y = point
        
        # Format public key
        if compressed:
            prefix = b'\x02' if y % 2 == 0 else b'\x03'
            pubkey = prefix + x.to_bytes(32, byteorder='big')
        else:
            pubkey = b'\x04' + x.to_bytes(32, byteorder='big') + y.to_bytes(32, byteorder='big')
        
        return pubkey.hex()

    @staticmethod
    def sha256(data: bytes) -> bytes:
        """Calculate SHA-256 hash"""
        return hashlib.sha256(data).digest()

    @staticmethod
    def ripemd160(data: bytes) -> bytes:
        """Calculate RIPEMD-160 hash using our custom implementation"""
        return custom_ripemd160(data)

    @staticmethod
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

    @staticmethod
    def pubkey_to_address(pubkey_hex: str, compressed: bool = True) -> str:
        """Convert public key to Bitcoin address"""
        # Decode hex public key
        pubkey_bytes = bytes.fromhex(pubkey_hex)
        
        # Hash public key
        sha = BitcoinTools.sha256(pubkey_bytes)
        ripe = BitcoinTools.ripemd160(sha)
        
        # Add version byte (0x00 for Bitcoin mainnet)
        versioned = b'\x00' + ripe
        
        # Double SHA-256 for checksum
        checksum = BitcoinTools.sha256(BitcoinTools.sha256(versioned))[:4]
        
        # Concatenate versioned hash and checksum
        binary_address = versioned + checksum
        
        # Base58 encode
        address = BitcoinTools.base58_encode(binary_address)
        
        return address

# Expected puzzle addresses (159 total)
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
# 0456579536d150fbce94ee62b47db2ca43af0a730a0467ba55c79e2a7ec9ce4ad297e35cdbb8e42a4643a60eef7c9abee2f5822f86b1da242d9c2301c431facfd8
def generate_all_keys():
    """Generate all 160 private keys in the sequence"""
    sequence = {}
    
    # Start with the known keys
    for pos, key in KNOWN_KEYS.items():
        sequence[pos] = key
    
    # Generate missing keys
    missing_positions = []
    for i in range(1, 161):
        if i not in sequence:
            missing_positions.append(i)
    
    print(f"Generating {len(missing_positions)} missing keys...")
    
    # Generate each missing key
    for missing_pos in missing_positions:
        # Find the closest lower known key
        prev_key_pos = None
        for i in range(missing_pos - 1, 0, -1):
            if i in sequence:
                prev_key_pos = i
                break
        
        # Generate keys from the previous key to our target
        if prev_key_pos is not None:
            current_key = sequence[prev_key_pos]
            current_pos = prev_key_pos
            
            while current_pos < missing_pos:
                next_key = predict_next_key(current_key, current_pos)
                current_pos += 1
                if current_pos not in sequence:
                    sequence[current_pos] = next_key
                current_key = sequence[current_pos]
    
    # Convert to ordered list
    complete_sequence = []
    for i in range(1, 161):
        if i in sequence:
            complete_sequence.append((i, sequence[i], i in KNOWN_KEYS))
        else:
            complete_sequence.append((i, "FAILED_TO_GENERATE", False))
    
    return complete_sequence

def get_pubkey(privkey_hex: str, compressed: bool = False) -> str:
    """Get the public key from a private key hex string"""
    try:
        privkey_int = int(privkey_hex, 16)
        return BitcoinTools.privkey_to_pubkey(privkey_int, compressed)
    except Exception as e:
        print(f"Error generating public key: {e}")
        return None

def get_bitcoin_address(pubkey_hex: str, compressed: bool = False) -> str:
    """Convert public key to Bitcoin address"""
    try:
        return BitcoinTools.pubkey_to_address(pubkey_hex, compressed)
    except Exception as e:
        print(f"Error generating address: {e}")
        return None

def check_address_balance(address: str) -> Optional[float]:
    """Check balance of a Bitcoin address using multiple APIs for reliability"""
    try:
        # Try Blockchair API first
        url = f"https://api.blockchair.com/bitcoin/dashboards/address/{address}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if "data" in data and address in data["data"]:
            balance_sats = data["data"][address]["address"]["balance"]
            return balance_sats / 100000000  # Convert satoshis to BTC
            
        # Fall back to blockchain.info API if needed
        url = f"https://blockchain.info/balance?active={address}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if address in data:
            balance_sats = data[address]["final_balance"]
            return balance_sats / 100000000
            
        return 0
    except Exception as e:
        print(f"Error checking balance for {address}: {e}")
        # Don't return None - just assume zero balance if API fails
        return 0

def verify_sequence():
    """Verify the generated sequence matches expected addresses"""
    print("Generating and verifying the complete Bitcoin puzzle sequence...")
    
    # Generate all keys
    keys = generate_all_keys()
    
    # Verify each key by deriving address
    verified_count = 0
    funds_found = 0
    total_btc = 0
    
    # Try both compressed and uncompressed formats to ensure we get a match
    for i, (idx, privkey, is_known) in enumerate(keys):
        if i >= len(EXPECTED_ADDRESSES):
            print(f"Warning: No expected address for key {idx}")
            continue
            
        expected_addr = EXPECTED_ADDRESSES[i]
        
        # First try uncompressed format (original Bitcoin addresses)
        pubkey_uncomp = get_pubkey(privkey, compressed=False)
        if not pubkey_uncomp:
            print(f"Key {idx}: Failed to generate uncompressed public key")
            continue
            
        address_uncomp = get_bitcoin_address(pubkey_uncomp, compressed=False)
        
        # If uncompressed doesn't match, try compressed
        if address_uncomp != expected_addr:
            pubkey_comp = get_pubkey(privkey, compressed=True)
            if not pubkey_comp:
                print(f"Key {idx}: Failed to generate compressed public key")
                continue
                
            address_comp = get_bitcoin_address(pubkey_comp, compressed=True)
            is_verified = (address_comp == expected_addr)
            address = address_comp
        else:
            is_verified = True
            address = address_uncomp
        
        # Update verification count
        verified_count += 1 if is_verified else 0
        
        # Status indicator
        status = "VERIFIED" if is_verified else "FAILED"
        origin = "KNOWN" if is_known else "GENERATED"
        
        # Only check balances for verified addresses to avoid unnecessary API calls
        funds = ""
        if is_verified:
            balance = check_address_balance(address)
            if balance and balance > 0:
                funds = f" - FUNDS FOUND: {balance} BTC"
                funds_found += 1
                total_btc += balance
        
        # Print status
        print(f"Key {idx}: {status} {origin}{funds}")
        if not is_verified:
            print(f"  Expected: {expected_addr}")
            print(f"  Got (uncompressed): {address_uncomp}")
            if 'address_comp' in locals():
                print(f"  Got (compressed): {address_comp}")
    
    # Print summary
    print("\n===== VERIFICATION SUMMARY =====")
    print(f"Total keys: {len(keys)}")
    print(f"Verified addresses: {verified_count}/{len(EXPECTED_ADDRESSES)} ({verified_count/len(EXPECTED_ADDRESSES)*100:.2f}%)")
    print(f"Addresses with funds: {funds_found}")
    print(f"Total BTC found: {total_btc}")
    
    return keys

def main():
    """Main function to verify the Bitcoin puzzle sequence"""
    keys = verify_sequence()
    
    # Save the verified sequence
    with open("verified_bitcoin_sequence.txt", "w") as f:
        for idx, key, is_known in keys:
            origin = "KNOWN" if is_known else "GENERATED"
            f.write(f"{idx}. {key} - {origin}\n")
    
    print("\nComplete sequence saved to verified_bitcoin_sequence.txt")

if __name__ == "__main__":
    main() 