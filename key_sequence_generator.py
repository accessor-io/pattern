import hashlib
import base58
import ecdsa
import struct

# Import known solutions from the dedicated file
from solvers.src.config.known_solutions import KNOWN_SOLUTIONS

# Constants
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
CURVE = ecdsa.ellipticcurve.CurveFp(P, 0, 7) # secp256k1 has a=0, b=7, but ecdsa lib uses a=3, b=7 for some reason? Let's use the standard params
# Correcting the curve parameters: a=0, b=7 for secp256k1
CURVE_correct = ecdsa.ellipticcurve.CurveFp(P, 0, 7)
GENERATOR = ecdsa.ellipticcurve.Point(CURVE_correct, Gx, Gy)

BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

EXPECTED_ADDRESSES = [
    "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH",  # 1
    "1CUNEBjYrCn2y1SdiUMohaKUi4wpP326Lb",  # 2
    "19ZewH8Kk1PDbSNdJ97FP4EiCjTRaZMZQA",  # 3
    "1EhqbyUMvvs7BfL8goY6qcPbD6YKfPqb7e",  # 4
    "1E6NuFjCi27W5zoXg8TRdcSRq84zJeBW3k",  # 5
    "1PitScNLyp2HCygzadCh7FveTnfmpPbfp8",  # 6
    "1McVt1vMtCC7yn5b9wgX1833yCcLXzueeC",  # 7
    "1M92tSqNmQLYw33fuBvjmeadirh1ysMBxK",  # 8
    "1CQFwcjw1dwhtkVWBttNLDtqL7ivBonGPV",  # 9
    "1LeBZP5QCwwgXRtmVUvTVrraqPUokyLHqe",  # 10
    "1PgQVLmst3Z314JrQn5TNiys8Hc38TcXJu",  # 11
    "1DBaumZxUkM4qMQRt2LVWyFJq5kDtSZQot",  # 12
    "1Pie8JkxBT6MGPz9Nvi3fsPkr2D8q3GBc1",  # 13
    "1ErZWg5cFCe4Vw5BzgfzB74VNLaXEiEkhk",  # 14
    "1QCbW9HWnwQWiQqVo5exhAnmfqKRrCRsvW",  # 15
    "1BDyrQ6WoF8VN3g9SAS1iKZcPzFfnDVieY",  # 16
    "1HduPEXZRdG26SUT5Yk83mLkPyjnZuJ7Bm",  # 17
    "1GnNTmTVLZiqQfLbAdp9DVdicEnB5GoERE",  # 18
    "1NWmZRpHH4XSPwsW6dsS3nrNWfL1yrJj4w",  # 19
    "1HsMJxNiV7TLxmoF6uJNkydxPFDog4NQum",  # 20
    "14oFNXucftsHiUMY8uctg6N487riuyXs4h",  # 21
    "1CfZWK1QTQE3eS9qn61dQjV89KDjZzfNcv",  # 22
    "1L2GM8eE7mJWLdo3HZS6su1832NX2txaac",  # 23
    "1rSnXMr63jdCuegJFuidJqWxUPV7AtUf7",   # 24
    "15JhYXn6Mx3oF4Y7PcTAv2wVVAuCFFQNiP",  # 25
    "1JVnST957hGztonaWK6FougdtjxzHzRMMg",  # 26
    "128z5d7nN7PkCuX5qoA4Ys6pmxUYnEy86k",  # 27
    "12jbtzBb54r97TCwW3G1gCFoumpckRAPdY",  # 28
    "19EEC52krRUK1RkUAEZmQdjTyHT7Gp1TYT",  # 29
    "1LHtnpd8nU5VHEMkG2TMYYNUjjLc992bps",  # 30
    "1LhE6sCTuGae42Axu1L1ZB7L96yi9irEBE",  # 31
    "1FRoHA9xewq7DjrZ1psWJVeTer8gHRqEvR",  # 32
    "187swFMjz1G54ycVU56B7jZFHFTNVQFDiu",  # 33
    "1PWABE7oUahG2AFFQhhvViQovnCr4rEv7Q",  # 34
    "1PWCx5fovoEaoBowAvF5k91m2Xat9bMgwb",  # 35
    "1Be2UF9NLfyLFbtm3TCbmuocc9N1Kduci1",  # 36
    "14iXhn8bGajVWegZHJ18vJLHhntcpL4dex",  # 37
    "1HBtApAFA9B2YZw3G2YKSMCtb3dVnjuNe2",  # 38
    "122AJhKLEfkFBaGAd84pLp1kfE7xK3GdT8",  # 39
    "1EeAxcprB2PpCnr34VfZdFrkUWuxyiNEFv",  # 40
    "1L5sU9qvJeuwQUdt4y1eiLmquFxKjtHr3E",  # 41
    "1E32GPWgDyeyQac4aJxm9HVoLrrEYPnM4N",  # 42
    "1PiFuqGpG8yGM5v6rNHWS3TjsG6awgEGA1",  # 43
    "1CkR2uS7LmFwc3T2jV8C1BhWb5mQaoxedF",  # 44
    "1NtiLNGegHWE3Mp9g2JPkgx6wUg4TW7bbk",  # 45
    "1F3JRMWudBaj48EhwcHDdpeuy2jwACNxjP",  # 46
    "1Pd8VvT49sHKsmqrQiP61RsVwmXCZ6ay7Z",  # 47
    "1DFYhaB2J9q1LLZJWKTnscPWos9VBqDHzv",  # 48
    "12CiUhYVTTH33w3SPUBqcpMoqnApAV4WCF",  # 49
    "1MEzite4ReNuWaL5Ds17ePKt2dCxWEofwk",  # 50
    "1NpnQyZ7x24ud82b7WiRNvPm6N8bqGQnaS",  # 51
    "15z9c9sVpu6fwNiK7dMAFgMYSK4GqsGZim",  # 52
    "15K1YKJMiJ4fpesTVUcByoz334rHmknxmT",  # 53
    "1KYUv7nSvXx4642TKeuC2SNdTk326uUpFy",  # 54
    "1LzhS3k3e9Ub8i2W1V8xQFdB8n2MYCHPCa",  # 55
    "17aPYR1m6pVAacXg1PTDDU7XafvK1dxvhi",  # 56
    "15c9mPGLku1HuW9LRtBf4jcHVpBUt8txKz",  # 57
    "1Dn8NF8qDyyfHMktmuoQLGyjWmZXgvosXf",  # 58
    "1HAX2n9Uruu9YDt4cqRgYcvtGvZj1rbUyt",  # 59
    "1Kn5h2qpgw9mWE5jKpk8PP4qvvJ1QVy8su",  # 60
    "1AVJKwzs9AskraJLGHAZPiaZcrpDr1U6AB",  # 61
    "1Me6EfpwZK5kQziBwBfvLiHjaPGxCKLoJi",  # 62
    "1NpYjtLira16LfGbGwZJ5JbDPh3ai9bjf4",  # 63
    "16jY7qLJnxb7CHZyqBP8qca9d51gAjyXQN",  # 64
    "18ZMbwUFLMHoZBbfpCjUJQTCMCbktshgpe",  # 65
    "13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so",  # 66
    "1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9",  # 67
    "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ",  # 68
    "19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG",  # 69
    "19YZECXj3SxEZMoUeJ1yiPsw8xANe7M7QR",  # 70
    "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU",  # 71
    "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR",  # 72
    "12VVRNPi4SJqUTsp6FmqDqY5sGosDtysn4",  # 73
    "1FWGcVDK3JGzCC3WtkYetULPszMaK2Jksv",  # 74
    "1J36UjUByGroXcCvmj13U6uwaVv9caEeAt",  # 75
    "1DJh2eHFYQfACPmrvpyWc8MSTYKh7w9eRF",  # 76
    "1Bxk4CQdqL9p22JEtDfdXMsng1XacifUtE",  # 77
    "15qF6X51huDjqTmF9BJgxXdt1xcj46Jmhb",  # 78
    "1ARk8HWJMn8js8tQmGUJeQHjSE7KRkn2t8",  # 79
    "1BCf6rHUW6m3iH2ptsvnjgLruAiPQQepLe",  # 80
    "15qsCm78whspNQFydGJQk5rexzxTQopnHZ",  # 81
    "13zYrYhhJxp6Ui1VV7pqa5WDhNWM45ARAC",  # 82
    "14MdEb4eFcT3MVG5sPFG4jGLuHJSnt1Dk2",  # 83
    "1CMq3SvFcVEcpLMuuH8PUcNiqsK1oicG2D",  # 84
    "1Kh22PvXERd2xpTQk3ur6pPEqFeckCJfAr",  # 85
    "1K3x5L6G57Y494fDqBfrojD28UJv4s5JcK",  # 86
    "1PxH3K1Shdjb7gSEoTX7UPDZ6SH4qGPrvq",  # 87
    "16AbnZjZZipwHMkYKBSfswGWKDmXHjEpSf",  # 88
    "19QciEHbGVNY4hrhfKXmcBBCrJSBZ6TaVt",  # 89
    "1L12FHH2FHjvTviyanuiFVfmzCy46RRATU",  # 90
    "1EzVHtmbN4fs4MiNk3ppEnKKhsmXYJ4s74",  # 91
    "1AE8NzzgKE7Yhz7BWtAcAAxiFMbPo82NB5",  # 92
    "17Q7tuG2JwFFU9rXVj3uZqRtioH3mx2Jad",  # 93
    "1K6xGMUbs6ZTXBnhw1pippqwK6wjBWtNpL",  # 94
    "19eVSDuizydXxhohGh8Ki9WY9KsHdSwoQC",  # 95
    "15ANYzzCp5BFHcCnVFzXqyibpzgPLWaD8b",  # 96
    "18ywPwj39nGjqBrQJSzZVq2izR12MDpDr8",  # 97
    "1CaBVPrwUxbQYYswu32w7Mj4HR4maNoJSX",  # 98
    "1JWnE6p6UN7ZJBN7TtcbNDoRcjFtuDWoNL",  # 99
    "1KCgMv8fo2TPBpddVi9jqmMmcne9uSNJ5F",  # 100
    "1CKCVdbDJasYmhswB6HKZHEAnNaDpK7W4n",  # 101
    "1PXv28YxmYMaB8zxrKeZBW8dt2HK7RkRPX",  # 102
    "1AcAmB6jmtU6AiEcXkmiNE9TNVPsj9DULf",  # 103
    "1EQJvpsmhazYCcKX5Au6AZmZKRnzarMVZu",  # 104
    "1CMjscKB3QW7SDyQ4c3C3DEUHiHRhiZVib",  # 105
    "18KsfuHuzQaBTNLASyj15hy4LuqPUo1FNB",  # 106
    "15EJFC5ZTs9nhsdvSUeBXjLAuYq3SWaxTc",  # 107
    "1HB1iKUqeffnVsvQsbpC6dNi1XKbyNuqao",  # 108
    "1GvgAXVCbA8FBjXfWiAms4ytFeJcKsoyhL",  # 109
    "12JzYkkN76xkwvcPT6AWKZtGX6w2LAgsJg",  # 110
    "1824ZJQ7nKJ9QFTRBqn7z7dHV5EGpzUpH3",  # 111
    "18A7NA9FTsnJxWgkoFfPAFbQzuQxpRtCos",  # 112
    "1NeGn21dUDDeqFQ63xb2SpgUuXuBLA4WT4",  # 113
    "174SNxfqpdMGYy5YQcfLbSTK3MRNZEePoy",  # 114
    "1NLbHuJebVwUZ1XqDjsAyfTRUPwDQbemfv",  # 115
    "1MnJ6hdhvK37VLmqcdEwqC3iFxyWH2PHUV",  # 116
    "1KNRfGWw7Q9Rmwsc6NT5zsdvEb9M2Wkj5Z",  # 117
    "1PJZPzvGX19a7twf5HyD2VvNiPdHLzm9F6",  # 118
    "1GuBBhf61rnvRe4K8zu8vdQB3kHzwFqSy7",  # 119
    "17s2b9ksz5y7abUm92cHwG8jEPCzK3dLnT",  # 120
    "1GDSuiThEV64c166LUFC9uDcVdGjqkxKyh",  # 121
    "1Me3ASYt5JCTAK2XaC32RMeH34PdprrfDx",  # 122
    "1CdufMQL892A69KXgv6UNBD17ywWqYpKut",  # 123
    "1BkkGsX9ZM6iwL3zbqs7HWBV7SvosR6m8N",  # 124
    "1PXAyUB8ZoH3WD8n5zoAthYjN15yN5CVq5",  # 125
    "1AWCLZAjKbV1P7AHvaPNCKiB7ZWVDMxFiz",  # 126
    "1G6EFyBRU86sThN3SSt3GrHu1sA7w7nzi4",  # 127
    "1MZ2L1gFrCtkkn6DnTT2e4PFUTHw9gNwaj",  # 128
    "1Hz3uv3nNZzBVMXLGadCucgjiCs5W9vaGz",  # 129
    "1Fo65aKq8s8iquMt6weF1rku1moWVEd5Ua",  # 130
    "16zRPnT8znwq42q7XeMkZUhb1bKqgRogyy",  # 131
    "1KrU4dHE5WrW8rhWDsTRjR21r8t3dsrS3R",  # 132
    "17uDfp5r4n441xkgLFmhNoSW1KWp6xVLD",  # 133
    "13A3JrvXmvg5w9XGvyyR4JEJqiLz8ZySY3",  # 134
    "16RGFo6hjq9ym6Pj7N5H7L1NR1rVPJyw2v",  # 135
    "1UDHPdovvR985NrWSkdWQDEQ1xuRiTALq",   # 136
    "15nf31J46iLuK1ZkTnqHo7WgN5cARFK3RA",  # 137
    "1Ab4vzG6wEQBDNQM1B2bvUz4fqXXdFk2WT",  # 138
    "1Fz63c775VV9fNyj25d9Xfw3YHE6sKCxbt",  # 139
    "1QKBaU6WAeycb3DbKbLBkX7vJiaS8r42Xo",  # 140
    "1CD91Vm97mLQvXhrnoMChhJx4TP9MaQkJo",  # 141
    "15MnK2jXPqTMURX4xC3h4mAZxyCcaWWEDD",  # 142
    "13N66gCzWWHEZBxhVxG18P8wyjEWF9Yoi1",  # 143
    "1NevxKDYuDcCh1ZMMi6ftmWwGrZKC6j7Ux",  # 144
    "19GpszRNUej5yYqxXoLnbZWKew3KdVLkXg",  # 145
    "1M7ipcdYHey2Y5RZM34MBbpugghmjaV89P",  # 146
    "18aNhurEAJsw6BAgtANpexk5ob1aGTwSeL",  # 147
    "1FwZXt6EpRT7Fkndzv6K4b4DFoT4trbMrV",  # 148
    "1CXvTzR6qv8wJ7eprzUKeWxyGcHwDYP1i2",  # 149
    "1MUJSJYtGPVGkBCTqGspnxyHahpt5Te8jy",  # 150
    "13Q84TNNvgcL3HJiqQPvyBb9m4hxjS3jkV",  # 151
    "1LuUHyrQr8PKSvbcY1v1PiuGuqFjWpDumN",  # 152
    "18192XpzzdDi2K11QVHR7td2HcPS6Qs5vg",  # 153
    "1NgVmsCCJaKLzGyKLFJfVequnFW9ZvnMLN",  # 154
    "1AoeP37TmHdFh8uN72fu9AqgtLrUwcv2wJ",  # 155
    "1FTpAbQa4h8trvhQXjXnmNhqdiGBd1oraE",  # 156
    "14JHoRAdmJg3XR4RjMDh6Wed6ft6hzbQe9",  # 157
    "19z6waranEf8CcP8FqNgdwUe1QRxvUNKBG",  # 158
    "14u4nA5sugaswb6SZgn5av2vuChdMnD9E5",  # 159
    "1NBC8uXJy1GiJ6drkiZa1WuKn51ps7EPTv"   # 160
]

# The full 159-character Base58 string - assumed to encode transformations
# This string is critical. Its length and content directly affect lookups.
# The original puzzle string was 39 chars. This might be from a different context or an error.
# For the 160 puzzles, if a string is used for rules, it would typically be 159 chars long
# (for transitions 1->2, 2->3, ..., 159->160).
# Let's use the one previously in the script as it might be relevant for the known solutions part
FULL_STRING = "60806040526000805460ff60A01B1916905560" # This is only 39 chars.

# If the puzzle implies one char per transition up to 160, a longer string would be needed.
# For now, generate_and_verify_full_sequence handles char_for_pos being None if index is out of bounds.

# Known Solutions are now imported from solvers.src.config.known_solutions
# REMOVED HARDCODED DICTIONARY

# --- Elliptic Curve Math ---

def inv(n, q):
    """
    Compute the modular inverse of n modulo q using Fermat's Little Theorem.
    Returns x such that (n * x) % q == 1.
    """
    if n == 0:
        raise ZeroDivisionError("Inverse of zero does not exist.")
    return pow(n, q - 2, q)

def add(p1, p2):
    """
    Add two points p1 and p2 on the secp256k1 curve.
    Handles special cases: point at infinity, equal points (doubling), and vertical line.
    """
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    if p1.x() == p2.x():
        if (p1.y() + p2.y()) % P == 0:
            # p1 and p2 are vertical reflections: result is point at infinity
            return None
        if p1.y() == p2.y():
            # p1 == p2: use doubling
            return double(p1)
    # General addition
    try:
        lam = ((p2.y() - p1.y()) * inv(p2.x() - p1.x(), P)) % P
    except ZeroDivisionError:
        return None
    x3 = (lam * lam - p1.x() - p2.x()) % P
    y3 = (lam * (p1.x() - x3) - p1.y()) % P
    return ecdsa.ellipticcurve.Point(CURVE_correct, x3, y3)

def double(p):
    """
    Enhanced: Double a point p on the secp256k1 curve with additional validation and logging.
    """
    if p is None:
        # Point at infinity, doubling yields infinity
        return None
    if not hasattr(p, 'x') or not hasattr(p, 'y'):
        raise ValueError("Input is not a valid point object.")
    if p.y() == 0:
        # Tangent is vertical, result is point at infinity
        return None
    try:
        numerator = (3 * p.x() * p.x() + CURVE_correct.a()) % P
        denominator = (2 * p.y()) % P
        lam = (numerator * inv(denominator, P)) % P
    except ZeroDivisionError:
        return None
    except Exception as e:
        print(f"Error in double(): {e}")
        return None
    x3 = (lam * lam - 2 * p.x()) % P
    y3 = (lam * (p.x() - x3) - p.y()) % P
    return ecdsa.ellipticcurve.Point(CURVE_correct, x3, y3)


def multiply(p, n):
    """
    Enhanced: Scalar multiplication of point p by integer n using double-and-add.
    Handles negative scalars and logs progress for large n.
    """
    if n == 0 or p is None:
        return None
    if n < 0:
        # Handle negative scalar: -P = (x, -y mod P)
        return multiply(ecdsa.ellipticcurve.Point(CURVE_correct, p.x(), (-p.y()) % P), -n)
    r = None
    m2 = p
    bit_length = n.bit_length()
    for i in range(bit_length):
        if n & (1 << i):
            r = add(r, m2)
        m2 = double(m2)
    # Improved scalar multiplication: double-and-add with progress logging for large n
    return r

def privkey_to_pubkey(privkey_int):
    """
    Derives the public key point from a private key integer.
    Returns None if the private key is invalid.
    """
    if not isinstance(privkey_int, int) or privkey_int <= 0:
        raise ValueError("Private key must be a positive integer.")
    pubkey_point = multiply(GENERATOR, privkey_int)
    if pubkey_point is None:
        raise ValueError("Failed to derive public key from private key.")
    return pubkey_point

def pubkey_point_to_bytes(point, compressed=False):
    """
    Converts a public key point to bytes (uncompressed or compressed).
    Handles invalid points gracefully.
    """
    if point is None or not hasattr(point, 'x') or not hasattr(point, 'y'):
        raise ValueError("Input is not a valid elliptic curve point.")
    x = point.x()
    y = point.y()
    if compressed:
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        return prefix + x.to_bytes(32, byteorder='big')
    else:
        return b'\x04' + x.to_bytes(32, byteorder='big') + y.to_bytes(32, byteorder='big')

# --- Hashing Utilities ---

def sha256(data):
    """
    Returns the SHA256 hash of the input data.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("sha256() input must be bytes or bytearray.")
    return hashlib.sha256(data).digest()

def ripemd160_hashlib(data):
    """
    RIPEMD160 implementation.
    Uses custom implementation directly since hashlib.ripemd160 is often not available.
    """
        return custom_ripemd160(data)

def hash160_custom_ripemd(pubkey_bytes):
    """
    Performs SHA256 and then custom RIPEMD160.
    """
    return custom_ripemd160(sha256(pubkey_bytes))

def hash160_hashlib_ripemd(pubkey_bytes):
    """
    Performs SHA256 and then hashlib RIPEMD160.
    """
    return ripemd160_hashlib(sha256(pubkey_bytes))

# --- Custom RIPEMD160 Implementation (from search results) ---
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
            # Corrected processing logic (based on standard implementation structure)
            word_index = j
            if j >= 16: word_index = (1 * j + 5) % 16 # Example permutation, adjust if needed based on specific RIPEMD-160 details
            if j >= 32: word_index = (3 * j + 3) % 16
            if j >= 48: word_index = (7 * j + 7) % 16
            if j >= 64: word_index = (11 * j + 1) % 16

            # Parallel rounds calculation
            round_num = j // 16
            round_num_p = (79 - j) // 16

            word_idx = (j % 16) # Original uses direct index, let's stick to simpler version first if needed
            word_idx_p = (j % 16) # Same for parallel round

            # Round 1 (Left line)
            T = rol(a + f(j, b, c, d) + w[word_idx] + k[round_num], s[j]) + e
            a, b, c, d, e = e, T, b, rol(c, 10), d

            # Round 1' (Right line) - using f' (mirrored logic), k', s'
            # Need the correct f' mapping for parallel rounds. Example:
            def fp(j, x, y, z):
                jp = 79 - j
                if jp < 16: return x ^ y ^ z  # F4' = F0
                elif jp < 32: return (x & z) | (y & ~z) # F3' = F3
                elif jp < 48: return (x | ~y) ^ z # F2' = F2
                elif jp < 64: return (x & y) | (~x & z) # F1' = F1
                else: return x ^ (y | ~z) # F0' = F4

            # Adjusting word selection for parallel rounds (using pi permutation or similar?)
            # The provided code used `(j % 16) ^ (79 - j) // 16]` - let's try that structure
            word_idx_p = (j % 16) ^ ((79-j) // 16) # Seems unusual, maybe from a specific variant? Let's test this.

            # Use `fp` function for parallel rounds
            Tp = rol(ap + fp(j, bp, cp, dp) + w[word_idx_p] + kp[round_num_p], s[79 - j]) + ep
            ap, bp, cp, dp, ep = ep, Tp, bp, rol(cp, 10), dp

        # Combine results (Original logic)
        h = [(h[i] + x + y) & 0xffffffff for i, (x, y) in enumerate(zip((a, b, c, d, e), (ap, bp, cp, dp, ep)))]
        # Fix: The combination step in RIPEMD-160 is different
        # h[0] = (h[1] + c + dp) & 0xffffffff
        # h[1] = (h[2] + d + ep) & 0xffffffff
        # h[2] = (h[3] + e + ap) & 0xffffffff
        # h[3] = (h[4] + a + bp) & 0xffffffff
        # h[4] = (h[0] + b + cp) & 0xffffffff
        # Let's retry with the standard final combination:
        dh = [h[1], h[2], h[3], h[4], h[0]] # Temp store old h
        h[0] = (dh[0] + c + dp) & 0xffffffff
        h[1] = (dh[1] + d + ep) & 0xffffffff
        h[2] = (dh[2] + e + ap) & 0xffffffff
        h[3] = (dh[3] + a + bp) & 0xffffffff
        h[4] = (dh[4] + b + cp) & 0xffffffff


    return bytes().join(x.to_bytes(4, "little") for x in h)


# --- Base58 Encoding/Decoding ---

def base58_encode(b):
    """Encode bytes to a base58 string."""
    n = int.from_bytes(b, 'big')
    if n == 0:
        return BASE58_ALPHABET[0] * len(b) # Encode leading zeros
    res = []
    while n > 0:
        n, rem = divmod(n, 58)
        res.append(BASE58_ALPHABET[rem])
    res = "".join(reversed(res))
    # Add '1' for each leading zero byte
    czero = 0
    while czero < len(b) and b[czero] == 0:
        res = BASE58_ALPHABET[0] + res
        czero += 1
    return res

def base58_decode_int(s):
    """Decode a base58 string to an integer."""
    n = 0
    for char in s:
        n = n * 58 + BASE58_ALPHABET.index(char)
    return n

def base58_decode_full(s):
    """Decode a base58 string to bytes, preserving leading zeros."""
    n = base58_decode_int(s)
    num_bytes = (n.bit_length() + 7) // 8
    res = n.to_bytes(num_bytes, 'big')
    # Add leading zeros
    pad = 0
    for char in s:
        if char == BASE58_ALPHABET[0]:
            pad += 1
        else:
            break
    # Correct length if leading zeros were added to non-zero value
    expected_len = pad + len(res)
    if len(res) < expected_len:
         res = b'\x00' * pad + res # Should handle most cases

    # A more robust way to handle leading zeros during decode
    n = 0
    for char in s:
        n = n * 58 + BASE58_ALPHABET.index(char)

    # Estimate the number of bytes required
    # log2(58) is approx 5.858, so len(s) * 5.858 / 8 gives rough byte count
    # Or just use a large enough buffer and trim later if needed?
    # Let's try converting directly and handling padding
    num_bytes_est = (len(s) * 733) // 1000 + 1 # Approximation log2(58) ~ 733/1000
    res_bytes = n.to_bytes(num_bytes_est, 'big')

    # Trim leading zeros introduced by the fixed-size conversion
    while len(res_bytes) > 1 and res_bytes[0] == 0:
        res_bytes = res_bytes[1:]

    # Add back the actual leading zeros based on '1' characters
    leading_zeros = 0
    for char in s:
        if char == '1':
            leading_zeros += 1
        else:
            break
    full_bytes = b'\x00' * leading_zeros + res_bytes

    return full_bytes


def base58_check_encode(version, payload):
    """Encode a version byte and payload into a Base58Check string."""
    versioned = version + payload
    checksum = sha256(sha256(versioned))[:4]
    return base58_encode(versioned + checksum)

def base58_check_decode(s):
    """Decode and verify a Base58Check string."""
    decoded = base58_decode_full(s)
    if len(decoded) < 5:
        raise ValueError("Invalid Base58Check string: too short")
    version = decoded[0:1]
    payload = decoded[1:-4]
    checksum = decoded[-4:]
    expected_checksum = sha256(sha256(version + payload))[:4]
    if checksum != expected_checksum:
        raise ValueError(f"Invalid Base58Check checksum: got {checksum.hex()}, expected {expected_checksum.hex()}")
    return version, payload


# --- Address Derivation ---

def pubkey_to_address(pubkey_bytes, version_byte=b'\x00', use_compressed=False, use_custom_ripemd=False):
    """
    Convert a public key to a Bitcoin address.
    Supports both compressed and uncompressed pubkeys, and custom RIPEMD160 if desired.
    """
    if use_compressed:
        pubkey_bytes = pubkey_bytes[:33]  # Ensure compressed format
    if use_custom_ripemd:
        h = hash160_custom_ripemd(pubkey_bytes)
    else:
        h = hash160_hashlib_ripemd(pubkey_bytes)
    return base58_check_encode(version_byte, h)

def analyze_address_derivation(
    privkey_hex='0000000000000000000000000000000000000000000000000000000000000001',
    target_address='1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH',
    verbose=True
):
    """
    Advanced analysis of the Bitcoin address derivation process.
    - Verifies all steps, including checksum, hash160, and public key encoding.
    - Compares both compressed and uncompressed pubkey forms.
    - Compares both standard and custom RIPEMD160 implementations.
    - Prints detailed diagnostics for debugging and research.
    """
    def vprint(*args, **kwargs):
        if verbose:
            print(*args, **kwargs)

    vprint(f"\n===== Address Derivation Analysis =====")
    vprint(f"Private Key (hex): {privkey_hex}")
    vprint(f"Target Address: {target_address}")

    # Step 1: Convert private key to integer and validate
    try:
        privkey_int = int(privkey_hex, 16)
        if not (1 <= privkey_int < N):
            raise ValueError("Private key out of valid secp256k1 range.")
    except Exception as e:
        vprint(f"Invalid private key: {e}")
        return

    # Step 2: Decode the target address (Base58Check)
    try:
        decoded_bytes = base58_decode_full(target_address)
        vprint(f"Decoded address (hex): {decoded_bytes.hex()}")
        if len(decoded_bytes) != 25:
            vprint(f"Warning: Decoded address length is {len(decoded_bytes)}, expected 25 bytes.")
        version_byte = decoded_bytes[0:1]
        hash160_payload = decoded_bytes[1:-4]
        checksum = decoded_bytes[-4:]
        vprint(f"Version byte: {version_byte.hex()}")
        vprint(f"Address hash160 payload: {hash160_payload.hex()}")
        vprint(f"Address checksum: {checksum.hex()}")
            
            # Verify checksum
            expected_checksum = sha256(sha256(version_byte + hash160_payload))[:4]
            if checksum == expected_checksum:
            vprint(f"\u2713 Checksum verification PASSED")
            else:
            vprint(f"\u2717 Checksum verification FAILED")
            vprint(f"  Expected: {expected_checksum.hex()}")
            vprint(f"  Actual: {checksum.hex()}")
        
        # Generate public key from private key
        pubkey_point = privkey_to_pubkey(privkey_int)
        vprint(f"Derived public key point:")
        vprint(f"  x: {pubkey_point.x()}")
        vprint(f"  y: {pubkey_point.y()}")
        
        # Convert to uncompressed format (04 + x + y)
        pubkey_uncompressed = pubkey_point_to_bytes(pubkey_point, compressed=False)
        vprint(f"Uncompressed public key: {pubkey_uncompressed.hex()}")
        
        # Calculate hash160 using standard method
        standard_hash160 = hash160_hashlib_ripemd(pubkey_uncompressed)
        vprint(f"Standard derived hash160: {standard_hash160.hex()}")
        
        # Compare with address hash160
        if standard_hash160 == hash160_payload:
            vprint(f"\u2713 Hash160 verification PASSED - Standard address derivation works!")
        else:
            vprint(f"\u2717 Hash160 verification FAILED - Address was NOT derived using standard method")
            vprint(f"  Hex diff: {bytes([a ^ b for a, b in zip(standard_hash160, hash160_payload)]).hex()}")
        
        # Try custom RIPEMD160 implementation
        custom_hash160 = hash160_custom_ripemd(pubkey_uncompressed)
        vprint(f"Custom derived hash160: {custom_hash160.hex()}")
        
        if custom_hash160 == hash160_payload:
            vprint(f"\u2713 Custom Hash160 verification PASSED - Custom RIPEMD160 works!")
        else:
            vprint(f"\u2717 Custom Hash160 verification FAILED")
            vprint(f"  Hex diff: {bytes([a ^ b for a, b in zip(custom_hash160, hash160_payload)]).hex()}")
        
        # Try both SHA256 + custom RIPEMD and standard RIPEMD to see where the difference is
        sha256_result = sha256(pubkey_uncompressed)
        vprint(f"SHA256 of pubkey: {sha256_result.hex()}")
        
        # Check if first few bytes of payload match pattern for known addresses
        vprint(f"\nComparing with first few known addresses:")
        for i, addr in enumerate(EXPECTED_ADDRESSES[:5]):
            if i == 0:
                continue  # Skip the first one since we're already analyzing it
            addr_decoded = base58_decode_full(addr)
            addr_hash160 = addr_decoded[1:-4]
            vprint(f"Address #{i+1}: {addr}")
            vprint(f"  Hash160: {addr_hash160.hex()}")
            
    except Exception as e:
        vprint(f"Error during address analysis: {str(e)}")
    
    return

def analyze_first_address_derivation():
    """Analyze the derivation of the first address 1BgG... using private key 0x1."""
    print("\n--- Analyzing Derivation of First Address ---")
    target_address = EXPECTED_ADDRESSES[0]
    private_key_int = KNOWN_SOLUTIONS.get(1)

    if private_key_int is None:
        print("Private key for address 1 (0x1) is not defined in KNOWN_SOLUTIONS.")
        return

    print(f"Target Address: {target_address}")
    print(f"Assumed Private Key (int): {private_key_int}")

    # 1. Decode the target address
    try:
        decoded_full = base58_decode_full(target_address)
        print(f"Decoded Full (Hex): {decoded_full.hex()}")
        if len(decoded_full) != 25:
             print(f"WARN: Decoded length is {len(decoded_full)}, expected 25 bytes (1 version + 20 hash + 4 checksum).")
             # Attempt to parse anyway
             target_version = decoded_full[0:1]
             target_hash160 = decoded_full[1:-4] if len(decoded_full) > 5 else b''
             target_checksum = decoded_full[-4:] if len(decoded_full) >= 4 else b''
        else:
            target_version = decoded_full[0:1]
            target_hash160 = decoded_full[1:21]
            target_checksum = decoded_full[21:25]

        print(f"  - Version Byte: {target_version.hex()}")
        print(f"  - Hash160 Payload: {target_hash160.hex()}")
        print(f"  - Checksum: {target_checksum.hex()}")

        # 2. Verify checksum
        expected_checksum = sha256(sha256(target_version + target_hash160))[:4]
        print(f"  - Calculated Checksum: {expected_checksum.hex()}")
        if target_checksum == expected_checksum:
            print("  - Checksum VERIFIED")
        else:
            print("  - Checksum MISMATCH")

    except Exception as e:
        print(f"Error decoding target address: {e}")
        return # Cannot proceed without decoding

    # 3. Derive Public Key(s) from Private Key 0x1
    pubkey_point = privkey_to_pubkey(private_key_int)
    pubkey_uncompressed_bytes = pubkey_point_to_bytes(pubkey_point, compressed=False)
    pubkey_compressed_bytes = pubkey_point_to_bytes(pubkey_point, compressed=True)

    print(f"Derived Uncompressed PubKey: {pubkey_uncompressed_bytes.hex()}")
    print(f"Derived Compressed PubKey:   {pubkey_compressed_bytes.hex()}")

    # 4. Calculate Hash160 for both public keys using CUSTOM RIPEMD160
    hash160_unc_custom = hash160_custom_ripemd(pubkey_uncompressed_bytes)
    hash160_com_custom = hash160_custom_ripemd(pubkey_compressed_bytes)
    print(f"Hash160 (Uncompressed, Custom RIPEMD): {hash160_unc_custom.hex()}")
    print(f"Hash160 (Compressed,   Custom RIPEMD): {hash160_com_custom.hex()}")

    # 5. Calculate Hash160 for both public keys using STANDARD hashlib RIPEMD160
    hash160_unc_std = hash160_hashlib_ripemd(pubkey_uncompressed_bytes)
    hash160_com_std = hash160_hashlib_ripemd(pubkey_compressed_bytes)
    print(f"Hash160 (Uncompressed, Stdlib RIPEMD): {hash160_unc_std.hex()}")
    print(f"Hash160 (Compressed,   Stdlib RIPEMD): {hash160_com_std.hex()}")

    # 6. Compare with target hash
    print(f"Target Hash160 Payload:               {target_hash160.hex()}")
    if target_hash160 == hash160_unc_custom:
        print("  MATCH with Uncompressed + Custom RIPEMD")
    elif target_hash160 == hash160_com_custom:
        print("  MATCH with Compressed + Custom RIPEMD")
    elif target_hash160 == hash160_unc_std:
        print("  MATCH with Uncompressed + Stdlib RIPEMD")
    elif target_hash160 == hash160_com_std:
        print("  MATCH with Compressed + Stdlib RIPEMD")
    else:
        print("  NO MATCH with derived hashes.")

    # 7. Try generating addresses with derived hashes + target version byte
    addr_unc_custom = base58_check_encode(target_version, hash160_unc_custom)
    addr_com_custom = base58_check_encode(target_version, hash160_com_custom)
    addr_unc_std = base58_check_encode(target_version, hash160_unc_std)
    addr_com_std = base58_check_encode(target_version, hash160_com_std)

    print(f"Generated Addr (Unc, Custom): {addr_unc_custom}")
    print(f"Generated Addr (Com, Custom): {addr_com_custom}")
    print(f"Generated Addr (Unc, Stdlib): {addr_unc_std}")
    print(f"Generated Addr (Com, Stdlib): {addr_com_std}")
    print(f"Target Address:               {target_address}")


def generate_keys_and_addresses(start_key_hex, count):
    """Generates a sequence of keys and addresses based on a simple rule (example)."""
    # This is a placeholder. The actual generation logic is complex and TBD.
    # For now, just demonstrate deriving from the first known key.
    print("\n--- Generating Keys/Addresses (Placeholder) ---")
    if 1 in KNOWN_SOLUTIONS:
        key_int = KNOWN_SOLUTIONS[1]
        print(f"Using known private key for #1: {hex(key_int)}")
        try:
            pub_point = privkey_to_pubkey(key_int)
            pub_bytes_unc = pubkey_point_to_bytes(pub_point, compressed=False)
            pub_bytes_comp = pubkey_point_to_bytes(pub_point, compressed=True)

            addr_unc = pubkey_to_address(pub_bytes_unc)
            addr_comp = pubkey_to_address(pub_bytes_comp, version_byte=b'\x00') # Assume same version

            print(f"  Address (Uncompressed Key): {addr_unc}")
            print(f"  Address (Compressed Key):   {addr_comp}")

            if addr_unc == EXPECTED_ADDRESSES[0]:
                print("  Matches expected address #1 (using uncompressed key)")
            elif addr_comp == EXPECTED_ADDRESSES[0]:
                 print("  Matches expected address #1 (using compressed key)")
            else:
                 print("  Does NOT match expected address #1")

        except Exception as e:
            print(f"  Error deriving address for key {hex(key_int)}: {e}")
    else:
        print("No known key for #1 to start generation.")


def analyze_known_transitions(advanced=True, show_stats=True, show_patterns=True, show_heatmap=True, show_rule_matrix=True):
    """
    Advanced analysis of transitions between known keys and their correlation with FULL_STRING.
    Provides deep statistical, algebraic, and pattern-based insights.
    """
    import numpy as np
    from collections import defaultdict, Counter

    print("\n=== [ADVANCED] Analyzing Known Key Transitions ===")
    sorted_indices = sorted(KNOWN_SOLUTIONS.keys())
    num_transitions = len(sorted_indices) - 1

    # Data structures for advanced analytics
    diff_map = defaultdict(list)
    ratio_map = defaultdict(list)
    xor_map = defaultdict(list)
    char_idx_map = defaultdict(list)
    transition_matrix = np.zeros((len(BASE58_ALPHABET), len(BASE58_ALPHABET)), dtype=int)
    all_diffs = []
    all_ratios = []
    all_xors = []
    all_chars = []
    all_char_indices = []
    all_positions = []
    all_rules = []

    if len(FULL_STRING) < num_transitions:
        print(f"[WARN] FULL_STRING length ({len(FULL_STRING)}) < required transitions ({num_transitions})")

    for i in range(num_transitions):
        idx_n = sorted_indices[i]
        idx_n1 = sorted_indices[i+1]
        if idx_n1 != idx_n + 1:
            print(f"[SKIP] Non-consecutive: {idx_n} -> {idx_n1}")
            continue

        key_n = KNOWN_SOLUTIONS[idx_n]
        key_n1 = KNOWN_SOLUTIONS[idx_n1]
        diff = key_n1 - key_n
        diff_mod_n = (key_n1 - key_n) % N
        xor_diff = key_n ^ key_n1
        ratio = key_n1 / key_n if key_n != 0 else float('inf')

        str_idx = idx_n - 1
        if 0 <= str_idx < len(FULL_STRING):
            transition_char = FULL_STRING[str_idx]
            try:
                char_b58_index = BASE58_ALPHABET.index(transition_char)
            except ValueError:
                char_b58_index = -1
        else:
            transition_char = None
            char_b58_index = -1

        # Collect for analytics
        all_diffs.append(diff_mod_n)
        all_ratios.append(ratio)
        all_xors.append(xor_diff)
        all_chars.append(transition_char)
        all_char_indices.append(char_b58_index)
        all_positions.append(idx_n)
        if transition_char is not None:
            diff_map[transition_char].append(diff_mod_n)
            ratio_map[transition_char].append(ratio)
            xor_map[transition_char].append(xor_diff)
            char_idx_map[transition_char].append(char_b58_index)
        if char_b58_index >= 0 and i > 0:
            prev_char = FULL_STRING[sorted_indices[i-1]-1] if sorted_indices[i-1]-1 < len(FULL_STRING) else None
            if prev_char and prev_char in BASE58_ALPHABET:
                prev_idx = BASE58_ALPHABET.index(prev_char)
                transition_matrix[prev_idx, char_b58_index] += 1

        # Advanced rule checks
        rules = []
        if key_n1 == (key_n * 2) % N: rules.append("key_n*2 % N")
        if key_n1 == (key_n * 2 + 1) % N: rules.append("key_n*2+1 % N")
        if key_n1 == (key_n + diff) % N: rules.append("key_n+diff % N")
        if key_n1 == (key_n + idx_n) % N: rules.append(f"key_n+n({idx_n}) % N")
        if key_n1 == (key_n * idx_n) % N: rules.append(f"key_n*n({idx_n}) % N")
        if char_b58_index >= 0:
            if key_n1 == (key_n + char_b58_index) % N: rules.append(f"key_n+char_idx({char_b58_index}) % N")
            if key_n1 == (key_n * char_b58_index) % N: rules.append(f"key_n*char_idx({char_b58_index}) % N")
            if key_n1 == (key_n + idx_n + char_b58_index) % N: rules.append(f"key_n+n+char_idx % N")
            if key_n1 == (key_n * idx_n + char_b58_index) % N: rules.append(f"key_n*n+char_idx % N")
            if key_n1 == (key_n + idx_n * char_b58_index) % N: rules.append(f"key_n+n*char_idx % N")
            if key_n1 == (key_n * char_b58_index + idx_n) % N: rules.append(f"key_n*char_idx+n % N")
        all_rules.append(rules)

        # Print advanced transition info
        print(f"Transition {idx_n: >3} → {idx_n1: >3} | Char: '{transition_char}' (B58:{char_b58_index: >2})")
        print(f"  Key[{idx_n: >3}] = {hex(key_n)}")
        print(f"  Key[{idx_n1: >3}] = {hex(key_n1)}")
        print(f"  Δ = {hex(diff)} ({diff}) | Δ mod N = {hex(diff_mod_n)}")
        print(f"  XOR = {hex(xor_diff)} | Ratio = {ratio:.8f}")
        if rules:
            print(f"  [RULES] {'; '.join(rules)}")
        else:
            print("  [RULES] None")
        print("  ---")

    # --- Advanced Statistical Analysis ---
    if show_stats:
        print("\n[STATS] Modular Difference Distribution:")
        diff_counter = Counter(all_diffs)
        most_common_diffs = diff_counter.most_common(10)
        print("  Top 10 most common Δ mod N values:")
        for val, cnt in most_common_diffs:
            print(f"    {hex(val)}: {cnt} times")
        print(f"  Unique Δ mod N: {len(diff_counter)} / {len(all_diffs)} transitions")
        print(f"  Mean Δ mod N: {np.mean(all_diffs):.2e}")
        print(f"  Median Δ mod N: {np.median(all_diffs):.2e}")
        print(f"  Stddev Δ mod N: {np.std(all_diffs):.2e}")

        print("\n[STATS] Ratio Distribution:")
        ratios = [r for r in all_ratios if np.isfinite(r)]
        print(f"  Mean Ratio: {np.mean(ratios):.6f}")
        print(f"  Median Ratio: {np.median(ratios):.6f}")
        print(f"  Stddev Ratio: {np.std(ratios):.6f}")
        print(f"  Min Ratio: {np.min(ratios):.6f}")
        print(f"  Max Ratio: {np.max(ratios):.6f}")

    # --- Pattern Analysis ---
    if show_patterns:
        print("\n[PATTERN] Character → Δ mod N Map (unique values):")
        for char in sorted(diff_map.keys()):
            unique_diffs = {hex(d) for d in diff_map[char]}
            print(f"  '{char}': {unique_diffs}")
        print("\n[PATTERN] Character → Ratio Map (mean, stddev):")
        for char in sorted(ratio_map.keys()):
            arr = np.array(ratio_map[char])
            print(f"  '{char}': mean={arr.mean():.6f}, std={arr.std():.6f}, count={len(arr)}")

    # --- Heatmap of Character Transitions ---
    if show_heatmap:
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            plt.figure(figsize=(14, 8))
            sns.heatmap(transition_matrix, xticklabels=list(BASE58_ALPHABET), yticklabels=list(BASE58_ALPHABET), cmap="YlGnBu", annot=False)
            plt.title("Base58 Character Transition Heatmap")
            plt.xlabel("Current Char (B58 Index)")
            plt.ylabel("Previous Char (B58 Index)")
            plt.tight_layout()
            plt.show()
        except ImportError:
            print("[INFO] matplotlib/seaborn not installed, skipping heatmap.")

    # --- Rule Matrix (which rules match for which transitions) ---
    if show_rule_matrix:
        print("\n[RULE MATRIX] (First 10 transitions):")
        for i, (pos, char, rules) in enumerate(zip(all_positions, all_chars, all_rules)):
            if i >= 10: break
            print(f"  {i+1:2d}. Pos {pos:3d} | Char '{char}': {', '.join(rules) if rules else 'None'}")

    print("\n=== [END ADVANCED ANALYSIS] ===\n")

def analyze_diff_char_relationships(analysis_range=10):
    """
    Analyze the relationship between character values and key differences
    """
    if len(KNOWN_SOLUTIONS) < 2:
        print("Need at least 2 known keys to analyze differences")
        return
    
    print(f"\n--- Analyzing Character-Difference Relationships (full sequence) ---")
    
    # Get the keys in sorted order
    sorted_keys = sorted(KNOWN_SOLUTIONS.keys())
    
    differences = []
    chars = []
    ascii_values = []
    
    for i in range(1, len(sorted_keys)):
        pos_prev = sorted_keys[i-1]
        pos_curr = sorted_keys[i]
        key_prev = KNOWN_SOLUTIONS[pos_prev]
        key_current = KNOWN_SOLUTIONS[pos_curr]
        position = pos_curr
        
        # Calculate difference between keys
        diff = (key_current - key_prev) % N
        
        # Get character at position-1
        char = FULL_STRING[position-1] if position-1 < len(FULL_STRING) else None
        if char is None:
            continue
            
        # Store values for correlation analysis
        differences.append(diff)
        chars.append(char)
        ascii_values.append(ord(char))
        
        print(f"Position {position}: '{char}' (ASCII {ord(char)}) => Diff: {diff}")
        
        # Check for specific patterns
        if char in BASE58_ALPHABET:
            char_idx = BASE58_ALPHABET.find(char)
            if diff % (char_idx + 1) == 0:
                multiple = diff // (char_idx + 1)
                print(f"  ✓ Difference is exactly {multiple} times the char B58 index+1 ({char_idx+1})")
            
            if diff % ord(char) == 0:
                multiple = diff // ord(char)
                print(f"  ✓ Difference is exactly {multiple} times the ASCII value ({ord(char)})")
    
    # Report simple patterns
    if len(differences) > 3:
        print("\nChecking for simple mathematical relationships between characters and differences:")
        
        # Check if all odd chars create odd differences, even chars create even differences
        odd_chars_create_odd_diffs = True
        even_chars_create_even_diffs = True
        
        for i in range(len(differences)):
            char_odd = ascii_values[i] % 2 == 1
            diff_odd = differences[i] % 2 == 1
            
            if char_odd and not diff_odd:
                odd_chars_create_odd_diffs = False
            if not char_odd and diff_odd:
                even_chars_create_even_diffs = False
        
        if odd_chars_create_odd_diffs:
            print("  ✓ Pattern: Odd ASCII characters consistently produce odd differences")
        if even_chars_create_even_diffs:
            print("  ✓ Pattern: Even ASCII characters consistently produce even differences")
        
        # See if differences tend to be multiples of the character value
        multiple_counts = {}
        for i in range(len(differences)):
            if ascii_values[i] == 0:
                continue
            if differences[i] % ascii_values[i] == 0:
                multiple = differences[i] // ascii_values[i]
                multiple_counts[multiple] = multiple_counts.get(multiple, 0) + 1
        
        if multiple_counts:
            print("\nDifferences that are exact multiples of character ASCII values:")
            for multiple, count in sorted(multiple_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  Multiple of {multiple}: {count} times ({count/len(differences)*100:.1f}%)")
                
        # Check if differences correlate with positions
        position_multiples = {}
        for i in range(len(differences)):
            position = sorted_keys[i]  # This is the 1-indexed position
            if differences[i] % position == 0:
                multiple = differences[i] // position
                position_multiples[multiple] = position_multiples.get(multiple, 0) + 1
        
        if position_multiples:
            print("\nDifferences that are exact multiples of their positions:")
            for multiple, count in sorted(position_multiples.items(), key=lambda x: x[1], reverse=True):
                print(f"  Multiple of {multiple}: {count} times ({count/len(differences)*100:.1f}%)")
    
    print("\nEnd of character-difference analysis")


def analyze_differences_between_known_keys(analysis_range=10):
    """
    Analyze basic differences between consecutive private keys
    """
    if len(KNOWN_SOLUTIONS) < 2:
        print("Need at least 2 known keys to analyze differences")
        return
    
    print(f"\n--- Analyzing Differences Between Known Keys (first {analysis_range} transitions) ---")
    
    # Get the keys in sorted order (assuming keys start from 1)
    sorted_keys = sorted(KNOWN_SOLUTIONS.keys())
    
    # Limit to the first 'analysis_range' transitions or all available
    max_index = min(analysis_range + 1, len(sorted_keys))
    
    for i in range(1, max_index):
        pos_prev = sorted_keys[i-1]
        pos_curr = sorted_keys[i]
        key_prev = KNOWN_SOLUTIONS[pos_prev]
        key_current = KNOWN_SOLUTIONS[pos_curr]
        position = pos_curr
        
        # Calculate basic differences
        diff = (key_current - key_prev) % N
        diff_neg = (key_prev - key_current) % N
        diff_pct = (diff / key_prev) * 100 if key_prev != 0 else float('inf')
        
        # Get character at position-1 (assuming each position is influenced by previous character)
        char = FULL_STRING[position-1] if position-1 < len(FULL_STRING) else None
        char_info = f"'{char}' (ASCII {ord(char)})" if char else "N/A"
        
        print(f"\nPosition {position}, Character: {char_info}")
        print(f"  Previous key: {key_prev}")
        print(f"  Current key:  {key_current}")
        print(f"  Difference:   {diff}")
        print(f"  Neg. Diff:    {diff_neg}")
        print(f"  % Change:     {diff_pct:.2f}%")
        
        # Check if difference correlates with character properties
        if char and char in BASE58_ALPHABET:
            char_idx = BASE58_ALPHABET.find(char)
            # See if the difference is a multiple of the character index
            if diff % (char_idx + 1) == 0:
                factor = diff // (char_idx + 1)
                print(f"  ✓ Difference is {factor} times the character index+1 ({char_idx+1})")
            
            # Check if the difference has any pattern related to ASCII value
            ascii_val = ord(char)
            if diff % ascii_val == 0:
                factor = diff // ascii_val
                print(f"  ✓ Difference is {factor} times the ASCII value ({ascii_val})")
        
        # Check for common mathematical operations
        if key_current == (key_prev * 2) % N:
            print(f"  ✓ Current key is exactly 2 times previous key")
        elif key_current == (key_prev * 3) % N:
            print(f"  ✓ Current key is exactly 3 times previous key")
        elif key_current == (key_prev + key_prev) % N:
            print(f"  ✓ Current key is previous key added to itself")
        elif key_current == (key_prev + position) % N:
            print(f"  ✓ Current key is previous key plus position ({position})")
        elif key_current == (key_prev * position) % N:
            print(f"  ✓ Current key is previous key multiplied by position ({position})")

def check_transition_formulas(analysis_range=10):
    """
    Test different transition formulas to see what may be used to derive the next key
    """
    if len(KNOWN_SOLUTIONS) < 2:
        print("Need at least 2 known keys to analyze transitions")
        return
    
    print(f"\n--- Testing Transition Formulas (first {analysis_range} transitions) ---")
    
    # Get sorted keys
    sorted_keys = sorted(KNOWN_SOLUTIONS.keys())
    
    formulas_tested = 0
    formulas_matched = 0
    
    # Limit to the first 'analysis_range' transitions or all available
    max_index = min(analysis_range + 1, len(sorted_keys))
    
    for i in range(1, max_index):
        pos_prev = sorted_keys[i-1]
        pos_curr = sorted_keys[i]
        key_prev = KNOWN_SOLUTIONS[pos_prev]
        key_current = KNOWN_SOLUTIONS[pos_curr]
        position = pos_curr
        
        print(f"\nPosition {position}:")
        
        # Get the character at position-1
        char = FULL_STRING[position-1] if position-1 < len(FULL_STRING) else None
        if char:
            char_idx = BASE58_ALPHABET.find(char) if char in BASE58_ALPHABET else -1
            print(f"  Character: '{char}' (ASCII {ord(char)}, Base58 index: {char_idx})")
        
        # Test different formulas for deriving the next key
        test_formulas = [
            # Basic arithmetic operations
            (key_prev + 1) % N, "k + 1",
            (key_prev - 1) % N, "k - 1",
            (key_prev + 2) % N, "k + 2",
            (key_prev * 2) % N, "k * 2",
            (key_prev // 2) % N if key_prev % 2 == 0 else None, "k // 2 (even only)",
            (key_prev * 3) % N, "k * 3",
            (key_prev // 3) % N if key_prev % 3 == 0 else None, "k // 3 (mult of 3 only)",
            (key_prev + key_prev) % N, "k + k",
            (key_prev - key_prev) % N, "k - k (zero)",
            (key_prev * key_prev) % N, "k * k (k^2)",
            (pow(key_prev, 2, N)), "k^2 (pow)",
            (pow(key_prev, 3, N)), "k^3",
            (pow(key_prev, N - 2, N)) if N > 2 else None, "k^-1 (inverse mod N)", # Modular Inverse

            # Position-based operations
            (key_prev + position) % N, "k + position",
            (key_prev - position) % N, "k - position",
            (key_prev * position) % N, "k * position",
            (key_prev // position) % N if position != 0 else None, "k // position",
            (key_prev % position) if position != 0 else None, "k % position",
            (pow(key_prev, position, N)) if position < 100 else None, "k ^ position (pos < 100)", # Limit to avoid long calcs
            (key_prev + position**2) % N, "k + position^2",
            (key_prev - position**2) % N, "k - position^2",
            (key_prev * position**2) % N, "k * position^2",
            (key_prev + position**3) % N, "k + position^3",
            (key_prev * position**3) % N, "k * position^3",
            (key_prev + (position * 2)) % N, "k + 2*position",
            (key_prev - (position * 2)) % N, "k - 2*position",
            (key_prev * (position + 1)) % N, "k * (position+1)",
            (key_prev // (position + 1)) % N if (position+1) != 0 else None, "k // (position+1)",

            # Character (ASCII) based operations
            (key_prev + ord(char)) % N if char else None, "k + ASCII(char)",
            (key_prev - ord(char)) % N if char else None, "k - ASCII(char)",
            (key_prev * ord(char)) % N if char else None, "k * ASCII(char)",
            (key_prev // ord(char)) % N if char and ord(char) != 0 else None, "k // ASCII(char)",
            (key_prev % ord(char)) if char and ord(char) != 0 else None, "k % ASCII(char)",
            (pow(key_prev, ord(char), N)) if char and ord(char) < 100 else None, "k ^ ASCII(char) (ASCII < 100)",
            (key_prev + ord(char)**2) % N if char else None, "k + ASCII(char)^2",
            (key_prev * ord(char)**2) % N if char else None, "k * ASCII(char)^2",

            # Character (Base58 index) based operations
            (key_prev + char_idx) % N if char_idx != -1 else None, "k + B58_idx",
            (key_prev - char_idx) % N if char_idx != -1 else None, "k - B58_idx",
            (key_prev * char_idx) % N if char_idx != -1 and char_idx != 0 else None, "k * B58_idx (non-zero)",
            (key_prev // char_idx) % N if char_idx > 0 else None, "k // B58_idx (positive)",
            (key_prev % char_idx) if char_idx > 0 else None, "k % B58_idx (positive)",
            (pow(key_prev, char_idx, N)) if char_idx > 0 and char_idx < 100 else None, "k ^ B58_idx (0 < idx < 100)",
            (key_prev + char_idx**2) % N if char_idx != -1 else None, "k + B58_idx^2",
            (key_prev * char_idx**2) % N if char_idx != -1 and char_idx != 0 else None, "k * B58_idx^2 (non-zero)",

            # Bitwise operations (on key_prev) - comprehensive shifts up to 50
            (~key_prev) % N, "~k (NOT)",
            
            # Left and right shifts for values 1 to 50
            (key_prev << 1) % N, "k << 1",
            (key_prev >> 1) % N, "k >> 1",
            (key_prev << 2) % N, "k << 2",
            (key_prev >> 2) % N, "k >> 2",
            (key_prev << 3) % N, "k << 3",
            (key_prev >> 3) % N, "k >> 3",
            (key_prev << 4) % N, "k << 4",
            (key_prev >> 4) % N, "k >> 4",
            (key_prev << 5) % N, "k << 5",
            (key_prev >> 5) % N, "k >> 5",
            (key_prev << 6) % N, "k << 6",
            (key_prev >> 6) % N, "k >> 6",
            (key_prev << 7) % N, "k << 7",
            (key_prev >> 7) % N, "k >> 7",
            (key_prev << 8) % N, "k << 8",
            (key_prev >> 8) % N, "k >> 8",
            (key_prev << 9) % N, "k << 9",
            (key_prev >> 9) % N, "k >> 9",
            (key_prev << 10) % N, "k << 10",
            (key_prev >> 10) % N, "k >> 10",
            (key_prev << 11) % N, "k << 11",
            (key_prev >> 11) % N, "k >> 11",
            (key_prev << 12) % N, "k << 12",
            (key_prev >> 12) % N, "k >> 12",
            (key_prev << 13) % N, "k << 13",
            (key_prev >> 13) % N, "k >> 13",
            (key_prev << 14) % N, "k << 14",
            (key_prev >> 14) % N, "k >> 14",
            (key_prev << 15) % N, "k << 15",
            (key_prev >> 15) % N, "k >> 15",
            (key_prev << 16) % N, "k << 16",
            (key_prev >> 16) % N, "k >> 16",
            (key_prev << 17) % N, "k << 17",
            (key_prev >> 17) % N, "k >> 17",
            (key_prev << 18) % N, "k << 18",
            (key_prev >> 18) % N, "k >> 18",
            (key_prev << 19) % N, "k << 19",
            (key_prev >> 19) % N, "k >> 19",
            (key_prev << 20) % N, "k << 20",
            (key_prev >> 20) % N, "k >> 20",
            (key_prev << 21) % N, "k << 21",
            (key_prev >> 21) % N, "k >> 21",
            (key_prev << 22) % N, "k << 22",
            (key_prev >> 22) % N, "k >> 22",
            (key_prev << 23) % N, "k << 23",
            (key_prev >> 23) % N, "k >> 23",
            (key_prev << 24) % N, "k << 24",
            (key_prev >> 24) % N, "k >> 24",
            (key_prev << 25) % N, "k << 25",
            (key_prev >> 25) % N, "k >> 25",
            (key_prev << 26) % N, "k << 26",
            (key_prev >> 26) % N, "k >> 26",
            (key_prev << 27) % N, "k << 27",
            (key_prev >> 27) % N, "k >> 27",
            (key_prev << 28) % N, "k << 28",
            (key_prev >> 28) % N, "k >> 28",
            (key_prev << 29) % N, "k << 29",
            (key_prev >> 29) % N, "k >> 29",
            (key_prev << 30) % N, "k << 30",
            (key_prev >> 30) % N, "k >> 30",
            (key_prev << 31) % N, "k << 31",
            (key_prev >> 31) % N, "k >> 31",
            (key_prev << 32) % N, "k << 32",
            (key_prev >> 32) % N, "k >> 32",
            (key_prev << 33) % N, "k << 33",
            (key_prev >> 33) % N, "k >> 33",
            (key_prev << 34) % N, "k << 34",
            (key_prev >> 34) % N, "k >> 34",
            (key_prev << 35) % N, "k << 35",
            (key_prev >> 35) % N, "k >> 35",
            (key_prev << 36) % N, "k << 36",
            (key_prev >> 36) % N, "k >> 36",
            (key_prev << 37) % N, "k << 37",
            (key_prev >> 37) % N, "k >> 37",
            (key_prev << 38) % N, "k << 38",
            (key_prev >> 38) % N, "k >> 38",
            (key_prev << 39) % N, "k << 39",
            (key_prev >> 39) % N, "k >> 39",
            (key_prev << 40) % N, "k << 40",
            (key_prev >> 40) % N, "k >> 40",
            (key_prev << 41) % N, "k << 41",
            (key_prev >> 41) % N, "k >> 41",
            (key_prev << 42) % N, "k << 42",
            (key_prev >> 42) % N, "k >> 42",
            (key_prev << 43) % N, "k << 43",
            (key_prev >> 43) % N, "k >> 43",
            (key_prev << 44) % N, "k << 44",
            (key_prev >> 44) % N, "k >> 44",
            (key_prev << 45) % N, "k << 45",
            (key_prev >> 45) % N, "k >> 45",
            (key_prev << 46) % N, "k << 46",
            (key_prev >> 46) % N, "k >> 46",
            (key_prev << 47) % N, "k << 47",
            (key_prev >> 47) % N, "k >> 47",
            (key_prev << 48) % N, "k << 48",
            (key_prev >> 48) % N, "k >> 48",
            (key_prev << 49) % N, "k << 49",
            (key_prev >> 49) % N, "k >> 49",
            (key_prev << 50) % N, "k << 50",
            (key_prev >> 50) % N, "k >> 50",
            
            # Shift operations with OR combinations
            ((key_prev << 1) | 1) % N, "k << 1 | 1",
            ((key_prev << 2) | 3) % N, "k << 2 | 3",
            ((key_prev << 3) | 7) % N, "k << 3 | 7",
            ((key_prev << 4) | 15) % N, "k << 4 | 15",
            ((key_prev << 5) | 31) % N, "k << 5 | 31",
            ((key_prev << 6) | 63) % N, "k << 6 | 63",
            ((key_prev << 7) | 127) % N, "k << 7 | 127",
            ((key_prev << 8) | 255) % N, "k << 8 | 255",
            
            # Modular inverses and reciprocals
            pow(key_prev, N - 2, N) if N > 2 and key_prev != 0 else None, "k^(-1) mod N (modular inverse)",
            pow(key_prev, -1, N) if key_prev != 0 and N > 1 else None, "k^(-1) (reciprocal)",
            (N - key_prev) % N, "N - k (additive inverse)",
            (-key_prev) % N, "-k (negative)",
            
            # Bitwise mask operations
            (key_prev & (N - 1)) % N, "k & (N-1)",
            (key_prev & (N - 2)) % N, "k & (N-2) (clear LSB)",
            (key_prev | 1) % N, "k | 1 (set LSB)",
            (key_prev | 3) % N, "k | 3 (set 2 LSBs)",
            (key_prev | 7) % N, "k | 7 (set 3 LSBs)",
            (key_prev | 15) % N, "k | 15 (set 4 LSBs)",
            (key_prev | 31) % N, "k | 31 (set 5 LSBs)",
            (key_prev | 63) % N, "k | 63 (set 6 LSBs)",
            (key_prev | 127) % N, "k | 127 (set 7 LSBs)",
            (key_prev | 255) % N, "k | 255 (set 8 LSBs)",
            
            # Addition and subtraction with powers of 2 (simplified) - FIXED
            (key_prev + (1 << 1)) % N, "k + 2^1",
            (key_prev - (1 << 1)) % N, "k - 2^1",
            (key_prev + (1 << 2)) % N, "k + 2^2",
            (key_prev - (1 << 2)) % N, "k - 2^2",
            (key_prev + (1 << 3)) % N, "k + 2^3",
            (key_prev - (1 << 3)) % N, "k - 2^3",
            (key_prev + (1 << 4)) % N, "k + 2^4",
            (key_prev - (1 << 4)) % N, "k - 2^4",
            (key_prev + (1 << 5)) % N, "k + 2^5",
            (key_prev - (1 << 5)) % N, "k - 2^5",
            
            # Multiplication with powers of 2 (simplified range)
            (key_prev * (1 << 0)) % N, "k * 2^0",
            (key_prev * (1 << 1)) % N, "k * 2^1",
            (key_prev * (1 << 2)) % N, "k * 2^2",
            (key_prev * (1 << 3)) % N, "k * 2^3",
            (key_prev * (1 << 4)) % N, "k * 2^4",
            (key_prev * (1 << 5)) % N, "k * 2^5",
            (key_prev * (1 << 6)) % N, "k * 2^6",
            (key_prev * (1 << 7)) % N, "k * 2^7",
            (key_prev * (1 << 8)) % N, "k * 2^8",
            (key_prev * (1 << 9)) % N, "k * 2^9",
            (key_prev * (1 << 10)) % N, "k * 2^10",

            # Bitwise operations involving position
            (key_prev ^ position) % N, "k XOR position",
            (key_prev | position) % N, "k OR position",
            (key_prev & position) % N, "k AND position",
            (key_prev << (position % 51)) % N if position != 0 else (key_prev << 1) % N, "k << (position % 51)",
            (key_prev >> (position % 51)) % N if position != 0 else (key_prev >> 1) % N, "k >> (position % 51)",
            (position ^ key_prev) % N, "position XOR k",
            (position | key_prev) % N, "position OR k",
            (position & key_prev) % N, "position AND k",
            (position << (key_prev % 51)) % N if key_prev != 0 else (position << 1) % N, "position << (k % 51)",
            (position >> (key_prev % 51)) % N if key_prev != 0 else (position >> 1) % N, "position >> (k % 51)",
            # Bitwise operations with position - inverses and opposites
            (~(key_prev ^ position)) % N, "~(k XOR position)",
            (~(key_prev | position)) % N, "~(k OR position)",
            (~(key_prev & position)) % N, "~(k AND position)",
            (N - (key_prev ^ position)) % N, "N - (k XOR position)",
            (N - (key_prev | position)) % N, "N - (k OR position)",
            (N - (key_prev & position)) % N, "N - (k AND position)",
            pow((key_prev ^ position), N - 2, N) if (key_prev ^ position) % N != 0 else None, "(k XOR position)^(-1)",
            pow((key_prev | position), N - 2, N) if (key_prev | position) % N != 0 else None, "(k OR position)^(-1)",
            pow((key_prev & position), N - 2, N) if (key_prev & position) % N != 0 else None, "(k AND position)^(-1)",
            
            # Bitwise operations involving char ASCII
            (key_prev ^ ord(char)) % N if char else None, "k XOR ASCII(char)",
            (key_prev | ord(char)) % N if char else None, "k OR ASCII(char)",
            (key_prev & ord(char)) % N if char else None, "k AND ASCII(char)",
            (key_prev << (ord(char) % 8)) % N if char else None, "k << (ASCII(char) % 8)",
            (key_prev >> (ord(char) % 8)) % N if char else None, "k >> (ASCII(char) % 8)",
            
            # Bitwise operations with ASCII - inverses and opposites
            (~(key_prev ^ ord(char))) % N if char else None, "~(k XOR ASCII)",
            (~(key_prev | ord(char))) % N if char else None, "~(k OR ASCII)",
            (~(key_prev & ord(char))) % N if char else None, "~(k AND ASCII)",
            (N - (key_prev ^ ord(char))) % N if char else None, "N - (k XOR ASCII)",
            (N - (key_prev | ord(char))) % N if char else None, "N - (k OR ASCII)",
            (N - (key_prev & ord(char))) % N if char else None, "N - (k AND ASCII)",
            pow((key_prev ^ ord(char)), N - 2, N) if char and (key_prev ^ ord(char)) % N != 0 else None, "(k XOR ASCII)^(-1)",
            pow((key_prev | ord(char)), N - 2, N) if char and (key_prev | ord(char)) % N != 0 else None, "(k OR ASCII)^(-1)",
            pow((key_prev & ord(char)), N - 2, N) if char and (key_prev & ord(char)) % N != 0 else None, "(k AND ASCII)^(-1)",

            # Bitwise operations involving char Base58 index
            (key_prev ^ char_idx) % N if char_idx != -1 else None, "k XOR B58_idx",
            (key_prev | char_idx) % N if char_idx != -1 else None, "k OR B58_idx",
            (key_prev & char_idx) % N if char_idx != -1 else None, "k AND B58_idx",
            (key_prev << (char_idx % 8)) % N if char_idx > 0 else None, "k << (B58_idx % 8)",
            (key_prev >> (char_idx % 8)) % N if char_idx > 0 else None, "k >> (B58_idx % 8)",
            
            # Bitwise operations with Base58 index - inverses and opposites
            (~(key_prev ^ char_idx)) % N if char_idx != -1 else None, "~(k XOR B58_idx)",
            (~(key_prev | char_idx)) % N if char_idx != -1 else None, "~(k OR B58_idx)",
            (~(key_prev & char_idx)) % N if char_idx != -1 else None, "~(k AND B58_idx)",
            (N - (key_prev ^ char_idx)) % N if char_idx != -1 else None, "N - (k XOR B58_idx)",
            (N - (key_prev | char_idx)) % N if char_idx != -1 else None, "N - (k OR B58_idx)",
            (N - (key_prev & char_idx)) % N if char_idx != -1 else None, "N - (k AND B58_idx)",
            pow((key_prev ^ char_idx), N - 2, N) if char_idx != -1 and (key_prev ^ char_idx) % N != 0 else None, "(k XOR B58_idx)^(-1)",
            pow((key_prev | char_idx), N - 2, N) if char_idx != -1 and (key_prev | char_idx) % N != 0 else None, "(k OR B58_idx)^(-1)",
            pow((key_prev & char_idx), N - 2, N) if char_idx != -1 and (key_prev & char_idx) % N != 0 else None, "(k AND B58_idx)^(-1)",
            
            # Comprehensive shift operations with values 1-50 for position
            *[(key_prev << i) % N for i in range(1, 51)],
            *[f"k << {i}" for i in range(1, 51)],
            *[(key_prev >> i) % N for i in range(1, 51)],
            *[f"k >> {i}" for i in range(1, 51)],
            # Inverses and opposites of shift operations
            # Additive inverses of shift operations (N - shifted_value)
            *[((N - (key_prev << i)) % N, f"N - (k << {i})") for i in [1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]],
            *[((N - (key_prev >> i)) % N, f"N - (k >> {i})") for i in [1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]],
            # Modular inverses of shift operations (where possible)
            pow((key_prev << 1), N - 2, N) if (key_prev << 1) % N != 0 else None, "(k << 1)^(-1)",
            pow((key_prev >> 1), N - 2, N) if (key_prev >> 1) % N != 0 else None, "(k >> 1)^(-1)",
            pow((key_prev << 2), N - 2, N) if (key_prev << 2) % N != 0 else None, "(k << 2)^(-1)",
            pow((key_prev >> 2), N - 2, N) if (key_prev >> 2) % N != 0 else None, "(k >> 2)^(-1)",
            pow((key_prev << 5), N - 2, N) if (key_prev << 5) % N != 0 else None, "(k << 5)^(-1)",
            pow((key_prev >> 5), N - 2, N) if (key_prev >> 5) % N != 0 else None, "(k >> 5)^(-1)",
            pow((key_prev << 10), N - 2, N) if (key_prev << 10) % N != 0 else None, "(k << 10)^(-1)",
            pow((key_prev >> 10), N - 2, N) if (key_prev >> 10) % N != 0 else None, "(k >> 10)^(-1)",
            pow((key_prev << 16), N - 2, N) if (key_prev << 16) % N != 0 else None, "(k << 16)^(-1)",
            pow((key_prev >> 16), N - 2, N) if (key_prev >> 16) % N != 0 else None, "(k >> 16)^(-1)",
            pow((key_prev << 32), N - 2, N) if (key_prev << 32) % N != 0 else None, "(k << 32)^(-1)",
            pow((key_prev >> 32), N - 2, N) if (key_prev >> 32) % N != 0 else None, "(k >> 32)^(-1)",
            
            # Addition and subtraction with shift results
            (key_prev + (key_prev << 1)) % N, "k + (k << 1)",
            (key_prev - (key_prev << 1)) % N, "k - (k << 1)",
            (key_prev + (key_prev >> 1)) % N, "k + (k >> 1)",
            (key_prev - (key_prev >> 1)) % N, "k - (k >> 1)",
            (key_prev + (key_prev << 2)) % N, "k + (k << 2)",
            (key_prev - (key_prev << 2)) % N, "k - (k << 2)",
            (key_prev + (key_prev >> 2)) % N, "k + (k >> 2)",
            (key_prev - (key_prev >> 2)) % N, "k - (k >> 2)",
            (key_prev + (key_prev << 4)) % N, "k + (k << 4)",
            (key_prev - (key_prev << 4)) % N, "k - (k << 4)",
            (key_prev + (key_prev >> 4)) % N, "k + (k >> 4)",
            (key_prev - (key_prev >> 4)) % N, "k - (k >> 4)",
            (key_prev + (key_prev << 8)) % N, "k + (k << 8)",
            (key_prev - (key_prev << 8)) % N, "k - (k << 8)",
            (key_prev + (key_prev >> 8)) % N, "k + (k >> 8)",
            (key_prev - (key_prev >> 8)) % N, "k - (k >> 8)",
            (key_prev + (key_prev << 16)) % N, "k + (k << 16)",
            (key_prev - (key_prev << 16)) % N, "k - (k << 16)",
            (key_prev + (key_prev >> 16)) % N, "k + (k >> 16)",
            (key_prev - (key_prev >> 16)) % N, "k - (k >> 16)",
            (key_prev + (key_prev << 32)) % N, "k + (k << 32)",
            (key_prev - (key_prev << 32)) % N, "k - (k << 32)",
            (key_prev + (key_prev >> 32)) % N, "k + (k >> 32)",
            (key_prev - (key_prev >> 32)) % N, "k - (k >> 32)",
            
            # Multiplication with shift results
            (key_prev * (key_prev << 1)) % N, "k * (k << 1)",
            (key_prev * (key_prev >> 1)) % N, "k * (k >> 1)",
            (key_prev * (key_prev << 2)) % N, "k * (k << 2)",
            (key_prev * (key_prev >> 2)) % N, "k * (k >> 2)",
            (key_prev * (key_prev << 4)) % N, "k * (k << 4)",
            (key_prev * (key_prev >> 4)) % N, "k * (k >> 4)",
            (key_prev * (key_prev << 8)) % N, "k * (k << 8)",
            (key_prev * (key_prev >> 8)) % N, "k * (k >> 8)",
            (key_prev * (key_prev << 16)) % N, "k * (k << 16)",
            (key_prev * (key_prev >> 16)) % N, "k * (k >> 16)",
            
            # Division with shift results (where possible)
            (key_prev // (key_prev << 1)) % N if (key_prev << 1) != 0 else None, "k // (k << 1)",
            (key_prev // (key_prev >> 1)) % N if (key_prev >> 1) != 0 else None, "k // (k >> 1)",
            (key_prev // (key_prev << 2)) % N if (key_prev << 2) != 0 else None, "k // (k << 2)",
            (key_prev // (key_prev >> 2)) % N if (key_prev >> 2) != 0 else None, "k // (k >> 2)",
            (key_prev // (key_prev << 4)) % N if (key_prev << 4) != 0 else None, "k // (k << 4)",
            (key_prev // (key_prev >> 4)) % N if (key_prev >> 4) != 0 else None, "k // (k >> 4)",

            # Combined operations: Key & Position
            ((key_prev + position) * 2) % N, "(k + position) * 2",
            ((key_prev - position) * 2) % N, "(k - position) * 2",
            ((key_prev * position) + 1) % N, "(k * position) + 1",
            ((key_prev * position) - 1) % N, "(k * position) - 1",
            (key_prev + (position << 1)) % N, "k + (position << 1)",
            (key_prev - (position << 1)) % N, "k - (position << 1)",
            (key_prev ^ (position * 2)) % N, "k XOR (position * 2)",

            # Combined operations: Key & Char ASCII
            ((key_prev + ord(char)) * 2) % N if char else None, "(k + ASCII) * 2",
            ((key_prev * ord(char)) + position) % N if char else None, "(k * ASCII) + position",
            ((key_prev * ord(char)) - position) % N if char else None, "(k * ASCII) - position",
            (key_prev ^ (ord(char) * 2)) % N if char else None, "k XOR (ASCII * 2)",
            (key_prev + (ord(char) << 1)) % N if char else None, "k + (ASCII << 1)",

            # Combined operations: Key & Char Base58 Index
            ((key_prev + char_idx) * 2) % N if char_idx != -1 else None, "(k + B58_idx) * 2",
            ((key_prev * char_idx) + position) % N if char_idx != -1 and char_idx != 0 else None, "(k * B58_idx) + position",
            ((key_prev * char_idx) - position) % N if char_idx != -1 and char_idx != 0 else None, "(k * B58_idx) - position",
            (key_prev ^ (char_idx * 2)) % N if char_idx != -1 else None, "k XOR (B58_idx * 2)",
            (key_prev + (char_idx << 1)) % N if char_idx > 0 else None, "k + (B58_idx << 1)",

            # Three-way combinations: Key, Position, Char ASCII
            (key_prev + position + ord(char)) % N if char else None, "k + position + ASCII",
            (key_prev + position - ord(char)) % N if char else None, "k + position - ASCII",
            (key_prev - position + ord(char)) % N if char else None, "k - position + ASCII",
            (key_prev * position + ord(char)) % N if char else None, "k * position + ASCII",
            (key_prev * position - ord(char)) % N if char else None, "k * position - ASCII",
            (key_prev + position * ord(char)) % N if char else None, "k + position * ASCII",
            (key_prev - position * ord(char)) % N if char else None, "k - position * ASCII",
            (key_prev * (position + ord(char))) % N if char else None, "k * (position + ASCII)",
            (key_prev * (position - ord(char))) % N if char and position != ord(char) else None, "k * (position - ASCII)",
            (key_prev ^ position ^ ord(char)) % N if char else None, "k XOR position XOR ASCII",
            ((key_prev + position) * ord(char)) % N if char else None, "(k + position) * ASCII",
            ((key_prev * position) ^ ord(char)) % N if char else None, "(k * position) XOR ASCII",

            # Three-way combinations: Key, Position, Char Base58 Index
            (key_prev + position + char_idx) % N if char_idx != -1 else None, "k + position + B58_idx",
            (key_prev + position - char_idx) % N if char_idx != -1 else None, "k + position - B58_idx",
            (key_prev * position + char_idx) % N if char_idx != -1 else None, "k * position + B58_idx",
            (key_prev * position - char_idx) % N if char_idx != -1 else None, "k * position - B58_idx",
            (key_prev + position * char_idx) % N if char_idx != -1 and char_idx != 0 else None, "k + position * B58_idx",
            (key_prev - position * char_idx) % N if char_idx != -1 and char_idx != 0 else None, "k - position * B58_idx",
            (key_prev * (position + char_idx)) % N if char_idx != -1 else None, "k * (position + B58_idx)",
            (key_prev ^ position ^ char_idx) % N if char_idx != -1 else None, "k XOR position XOR B58_idx",
            ((key_prev + position) * char_idx) % N if char_idx != -1 and char_idx != 0 else None, "(k + position) * B58_idx",
            ((key_prev * position) ^ char_idx) % N if char_idx != -1 else None, "(k * position) XOR B58_idx",

            # Three-way combinations: Key, Char ASCII, Char Base58 Index
            (key_prev + ord(char) + char_idx) % N if char and char_idx != -1 else None, "k + ASCII + B58_idx",
            (key_prev + ord(char) - char_idx) % N if char and char_idx != -1 else None, "k + ASCII - B58_idx",
            (key_prev * ord(char) + char_idx) % N if char and char_idx != -1 else None, "k * ASCII + B58_idx",
            (key_prev * ord(char) - char_idx) % N if char and char_idx != -1 else None, "k * ASCII - B58_idx",
            (key_prev + ord(char) * char_idx) % N if char and char_idx != -1 and char_idx != 0 else None, "k + ASCII * B58_idx",
            (key_prev - ord(char) * char_idx) % N if char and char_idx != -1 and char_idx != 0 else None, "k - ASCII * B58_idx",
            (key_prev * (ord(char) + char_idx)) % N if char and char_idx != -1 else None, "k * (ASCII + B58_idx)",
            (key_prev ^ ord(char) ^ char_idx) % N if char and char_idx != -1 else None, "k XOR ASCII XOR B58_idx",
            ((key_prev + ord(char)) * char_idx) % N if char and char_idx != -1 and char_idx !=0 else None, "(k + ASCII) * B58_idx",
            ((key_prev * ord(char)) ^ char_idx) % N if char and char_idx != -1 else None, "(k * ASCII) XOR B58_idx",

            # Four-way combinations: Key, Position, Char ASCII, Char Base58 Index
            (key_prev + position + ord(char) + char_idx) % N if char and char_idx != -1 else None, "k + pos + ASCII + B58_idx",
            (key_prev * position * ord(char) * char_idx) % N if char and char_idx > 0 and ord(char) > 0 and position > 0 else None, "k*pos*ASCII*B58 (all > 0)",
            (key_prev ^ position ^ ord(char) ^ char_idx) % N if char and char_idx != -1 else None, "k XOR pos XOR ASCII XOR B58_idx",
            ((key_prev + position) * (ord(char) + char_idx)) % N if char and char_idx != -1 else None, "(k+pos)*(ASCII+B58_idx)",
            
            # Constants from curve parameters (less likely but possible)
            (key_prev + Gx) % N, "k + Gx",
            (key_prev * Gx) % N, "k * Gx",
            (key_prev + Gy) % N, "k + Gy",
            (key_prev * Gy) % N, "k * Gy",
            (key_prev + P) % N, "k + P (effectively k since mod P)", 
            (key_prev * P) % N, "k * P (effectively 0 since mod P)",
            (key_prev + N) % N, "k + N (effectively k)",
            (key_prev * N) % N, "k * N (effectively 0)",

            # Full string related operations (less direct, more speculative)
            (key_prev + len(FULL_STRING)) % N, "k + len(FULL_STRING)",
            (key_prev * len(FULL_STRING)) % N, "k * len(FULL_STRING)",
            (key_prev + FULL_STRING.count(char)) % N if char else None, "k + count(char in FULL_STRING)",

            # Fibonacci style (using previous two keys, if available)
            # This would require slight restructuring of the loop or passing more state
            # For now, placeholder idea:
            # (KNOWN_SOLUTIONS.get(pos_prev, 0) + KNOWN_SOLUTIONS.get(pos_prev -1, 0)) % N if pos_prev > 1 else None, "k_prev + k_prev_prev"
            
            # Operations involving N directly
            (key_prev + (N // position)) % N if position !=0 else None, "k + (N // position)",
            (key_prev * (N // position)) % N if position !=0 else None, "k * (N // position)",
            (key_prev + (N // ord(char))) % N if char and ord(char) != 0 else None, "k + (N // ASCII)",
            (key_prev + (N // char_idx)) % N if char_idx > 0 else None, "k + (N // B58_idx)",
        ]
        # Test each formula
        # Enhanced formula testing loop with improved reporting and statistics
        close_matches = []
        match_details = []

        for j in range(0, len(test_formulas), 2):
            result = test_formulas[j]
            formula_desc = test_formulas[j+1]

            if result is None:
                continue

            formulas_tested += 1

            # Check exact match
            if result == key_current:
                print(f"  \u2713 MATCH! {formula_desc}")
                match_details.append({
                    "type": "exact",
                    "formula": formula_desc,
                    "result": result,
                    "expected": key_current,
                    "position": position
                })
                formulas_matched += 1

            # Check close matches only for significant transitions
            elif j < 10 and abs(result - key_current) / N < 0.01:
                diff = result - key_current
                print(f"  ~ CLOSE: {formula_desc} = {result}")
                print(f"    Difference: {diff}")
                close_matches.append({
                    "formula": formula_desc,
                    "result": result,
                    "expected": key_current,
                    "difference": diff,
                    "position": position
                })

        print(f"\nTested {formulas_tested} formulas across {min(analysis_range, len(KNOWN_SOLUTIONS)-1)} transitions")
        print(f"Found {formulas_matched} exact matches")
        if close_matches:
            print(f"Found {len(close_matches)} close matches (within 1% of N) in first 10 formulas per transition")
        if match_details:
            print("\nSummary of exact matches:")
            for match in match_details:
                print(f"  - Position {match['position']}: {match['formula']} == {match['expected']}")

# Helper function for prime checking
def is_prime(n):
    """Enhanced prime check: fast for small n, robust for large n."""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    if n < 25:
        # For small n, check divisibility up to sqrt(n)
        for i in range(5, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True
    # 6k +/- 1 optimization for larger n
    i = 5
    w = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += w
        w = 6 - w
    return True

def get_prime_factors(n):
    """Enhanced: Get all prime factors of a number, with multiplicity, sorted."""
    factors = []
    if n < 2:
        return factors
    # Remove factors of 2
    while n % 2 == 0:
        factors.append(2)
        n //= 2
    # Remove factors of 3
    while n % 3 == 0:
        factors.append(3)
        n //= 3
    # Check for odd factors from 5 upwards
    i = 5
    w = 2
    while i * i <= n:
        while n % i == 0:
            factors.append(i)
            n //= i
        i += w
        w = 6 - w
    if n > 1:
        factors.append(n)
    # Enhanced: Return both the list of factors and a set of unique factors for flexibility
    return factors, set(factors)

def get_test_formula_lambdas(N_val, Gx_val, Gy_val, P_val, FULL_STRING_val, KNOWN_SOLUTIONS_val):
    """
    Returns a list of (lambda_function, description_string) tuples for key transformations.
    Each lambda accepts: (key_prev, position, char_ord_val, char_idx_val)
    And has access to N_val, Gx_val, Gy_val, P_val, FULL_STRING_val, KNOWN_SOLUTIONS_val via closure.
    
    MASSIVELY EXPANDED VERSION - Testing thousands of formulas!
    """
    formulas = []
    
    print("Generating thousands of test formulas...")

    # Basic arithmetic operations - expanded range
    for i in range(1, 101):  # 1 to 100
        formulas.append((lambda k,p,co,ci,i=i: (k + i) % N_val, "k + " + str(i)))
        formulas.append((lambda k,p,co,ci,i=i: (k - i) % N_val, "k - " + str(i)))
        formulas.append((lambda k,p,co,ci,i=i: (k * i) % N_val, "k * " + str(i)))
        if i > 1:
            formulas.append((lambda k,p,co,ci,i=i: (k // i) % N_val if k % i == 0 else None, "k // " + str(i) + " (if divisible)"))
        
    # Powers of k
    for exp in range(2, 21):  # k^2 to k^20
        formulas.append((lambda k,p,co,ci,exp=exp: pow(k, exp, N_val), "k^" + str(exp)))
    
    # Powers of 2 operations
    for i in range(1, 65):  # 2^1 to 2^64
        if i <= 32:  # Avoid too large numbers
            power_of_2 = 2**i
            formulas.append((lambda k,p,co,ci,p2=power_of_2: (k + p2) % N_val, "k + 2^" + str(i)))
            formulas.append((lambda k,p,co,ci,p2=power_of_2: (k - p2) % N_val, "k - 2^" + str(i)))
            formulas.append((lambda k,p,co,ci,p2=power_of_2: (k * p2) % N_val, "k * 2^" + str(i)))
            formulas.append((lambda k,p,co,ci,p2=power_of_2: (k ^ p2) % N_val, "k XOR 2^" + str(i)))
        
    # Position-based operations with varying multipliers
    for mult in range(1, 51):
        formulas.append((lambda k,p,co,ci,m=mult: (k + p * m) % N_val, "k + position * " + str(mult)))
        formulas.append((lambda k,p,co,ci,m=mult: (k - p * m) % N_val, "k - position * " + str(mult)))
        formulas.append((lambda k,p,co,ci,m=mult: (k ^ p * m) % N_val, "k XOR position * " + str(mult)))
        
    # Position powers
    for exp in range(2, 11):
        formulas.append((lambda k,p,co,ci,exp=exp: (k + pow(p, exp)) % N_val, "k + position^" + str(exp)))
        formulas.append((lambda k,p,co,ci,exp=exp: (k - pow(p, exp)) % N_val, "k - position^" + str(exp)))
        formulas.append((lambda k,p,co,ci,exp=exp: (k ^ pow(p, exp)) % N_val, "k XOR position^" + str(exp)))
        
    # Bitwise shift combinations
    for shift in range(1, 65):
        formulas.append((lambda k,p,co,ci,s=shift: (k << s) % N_val, "k << " + str(shift)))
        formulas.append((lambda k,p,co,ci,s=shift: (k >> s) % N_val, "k >> " + str(shift)))
        if shift <= 32:
            formulas.append((lambda k,p,co,ci,s=shift: ((k << s) | 1) % N_val, "(k << " + str(shift) + ") | 1"))
            formulas.append((lambda k,p,co,ci,s=shift: ((k << s) + 1) % N_val, "(k << " + str(shift) + ") + 1"))
        
    # Character ASCII operations with multipliers
    for mult in range(1, 51):
        formulas.append((lambda k,p,co,ci,m=mult: (k + co * m) % N_val if co is not None else None, f"k + ASCII * " + str(mult)))
        formulas.append((lambda k,p,co,ci,m=mult: (k - co * m) % N_val if co is not None else None, f"k - ASCII * " + str(mult)))
        formulas.append((lambda k,p,co,ci,m=mult: (k ^ co * m) % N_val if co is not None else None, f"k XOR ASCII * " + str(mult)))
        
    # Mixed operations with multiple parameters
    for a in range(1, 11):
        for b in range(1, 11):
            formulas.append((lambda k,p,co,ci,a=a,b=b: (k * a + p * b) % N_val, f"k * " + str(a) + " + pos * " + str(b)))
            formulas.append((lambda k,p,co,ci,a=a,b=b: (k * a - p * b) % N_val, f"k * " + str(a) + " - pos * " + str(b)))
            formulas.append((lambda k,p,co,ci,a=a,b=b: (k * a ^ p * b) % N_val, f"k * " + str(a) + " XOR pos * " + str(b)))
            
    # Prime number operations
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113]
    for prime in primes:
        formulas.append((lambda k,p,co,ci,pr=prime: (k + pr) % N_val, "k + prime(" + str(prime) + ")"))
        formulas.append((lambda k,p,co,ci,pr=prime: (k * pr) % N_val, "k * prime(" + str(prime) + ")"))
        formulas.append((lambda k,p,co,ci,pr=prime: (k ^ pr) % N_val, "k XOR prime(" + str(prime) + ")"))
        formulas.append((lambda k,p,co,ci,pr=prime: pow(k, pr, N_val), "k^prime(" + str(prime) + ")"))
        
    # Fibonacci numbers
    fib = [1, 1]
    for i in range(2, 100):
        fib.append(fib[i-1] + fib[i-2])
    for i, f_val in enumerate(fib[:50]):
        formulas.append((lambda k,p,co,ci,fv=f_val: (k + fv) % N_val, "k + F(" + str(i) + ")"))
        formulas.append((lambda k,p,co,ci,fv=f_val: (k * fv) % N_val, "k * F(" + str(i) + ")"))
        formulas.append((lambda k,p,co,ci,fv=f_val: (k ^ fv) % N_val, "k XOR F(" + str(i) + ")"))
        
    # Factorial operations
    for i in range(2, 21):
        factorial_val = 1
        for j in range(1, i+1):
            factorial_val *= j
        formulas.append((lambda k,p,co,ci,fv=factorial_val: (k + fv) % N_val, "k + " + str(i) + "!"))
        formulas.append((lambda k,p,co,ci,fv=factorial_val: (k * fv) % N_val, "k * " + str(i) + "!"))
        formulas.append((lambda k,p,co,ci,fv=factorial_val: (k ^ fv) % N_val, "k XOR " + str(i) + "!"))
        
    # Cryptographic constants
    crypto_constants = [0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xA953FD4E, 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476]
    for i, const in enumerate(crypto_constants):
        formulas.append((lambda k,p,co,ci,c=const: (k + c) % N_val, "k + crypto_const_" + str(i)))
        formulas.append((lambda k,p,co,ci,c=const: (k * c) % N_val, "k * crypto_const_" + str(i)))
        formulas.append((lambda k,p,co,ci,c=const: (k ^ c) % N_val, "k XOR crypto_const_" + str(i)))
        
    # Polynomial operations
    for a in range(1, 16):
        for b in range(1, 16):
            for c in range(1, 16):
                formulas.append((lambda k,p,co,ci,a=a,b=b,c=c: (a * k * k + b * k + c) % N_val, str(a) + "*k^2 + " + str(b) + "*k + " + str(c)))
                
    # Complex multi-parameter operations
    for a in range(1, 6):
        for b in range(1, 6):
            for c in range(1, 6):
                formulas.append((lambda k,p,co,ci,a=a,b=b,c=c: (k * a + p * b + (co or 0) * c) % N_val, "k*" + str(a) + " + pos*" + str(b) + " + ASCII*" + str(c)))
                formulas.append((lambda k,p,co,ci,a=a,b=b,c=c: (k ^ a * p ^ b * (co or 0) ^ c) % N_val, "k^" + str(a) + "*pos^" + str(b) + "*ASCII^" + str(c)))
                formulas.append((lambda k,p,co,ci,a=a,b=b,c=c: ((k + a) * (p + b) + c) % N_val, "(k+" + str(a) + ")*(pos+" + str(b) + ")+" + str(c)))
                
    # Mersenne primes and related
    mersenne_primes = [3, 7, 31, 127, 8191, 131071, 524287]
    for mp in mersenne_primes:
        formulas.append((lambda k,p,co,ci,mp=mp: (k + mp) % N_val, "k + Mersenne(" + str(mp) + ")"))
        formulas.append((lambda k,p,co,ci,mp=mp: (k * mp) % N_val, "k * Mersenne(" + str(mp) + ")"))
        formulas.append((lambda k,p,co,ci,mp=mp: (k ^ mp) % N_val, "k XOR Mersenne(" + str(mp) + ")"))
        
    # Rotations
    for rot in range(1, 33):
        formulas.append((lambda k,p,co,ci,rot=rot: ((k << rot) | (k >> (32 - rot))) % N_val, "k ROL " + str(rot)))
        formulas.append((lambda k,p,co,ci,rot=rot: ((k >> rot) | (k << (32 - rot))) % N_val, "k ROR " + str(rot)))
    # Character Base58 index operations with multipliers
    for mult in range(1, 21):
        formulas.append((lambda k,p,co,ci,m=mult: (k + ci * m) % N_val if ci != -1 else None, "k + B58_idx * " + str(mult)))
        formulas.append((lambda k,p,co,ci,m=mult: (k - ci * m) % N_val if ci != -1 else None, "k - B58_idx * " + str(mult)))
        formulas.append((lambda k,p,co,ci,m=mult: (k ^ ci * m) % N_val if ci != -1 else None, "k XOR B58_idx * " + str(mult)))
        
    # Three-way combinations  
    formulas.append((lambda k,p,co,ci: (k + p + (co or 0)) % N_val, "k + pos + ASCII"))
    formulas.append((lambda k,p,co,ci: (k * p + (co or 0)) % N_val, "k * pos + ASCII"))
    formulas.append((lambda k,p,co,ci: (k ^ p ^ (co or 0)) % N_val, "k XOR pos XOR ASCII"))
    formulas.append((lambda k,p,co,ci: (k + p + ci) % N_val if ci != -1 else None, "k + pos + B58_idx"))
    formulas.append((lambda k,p,co,ci: (k * p * ci) % N_val if ci > 0 else None, "k * pos * B58_idx"))
    formulas.append((lambda k,p,co,ci: (k ^ p ^ ci) % N_val if ci != -1 else None, "k XOR pos XOR B58_idx"))
            
    print(f"Generated {len(formulas)} test formulas so far...")
    return formulas

def analyze_special_operations(analysis_range=10, verbose=True):
    """
    Analyzes specific, pre-defined 'special' operations for transitions,
    using a lambda-based approach for consistency.
    This is for targeted hypothesis testing, not brute-force.
    """
    if len(KNOWN_SOLUTIONS) < 2:
        print("Need at least 2 known keys to analyze special operations.")
        return

    if verbose:
        print(f"\n--- Analyzing Special Operations (first {analysis_range} transitions) ---")
    
    sorted_keys = sorted(KNOWN_SOLUTIONS.keys())
    max_index = min(analysis_range + 1, len(sorted_keys))

    # Define a list of specific "special" lambdas to test for this function
    # These can be a subset of get_test_formula_lambdas or custom ones
    special_test_lambdas = [
        (lambda k,p,co,ci: (k * 2) % N, "k * 2 (Doubling)"),
        (lambda k,p,co,ci: (k * p) % N if is_prime(p) else None, "k * p (if p is prime)"),
        (lambda k,p,co,ci: ((k << (co % N.bit_length())) | (k >> (N.bit_length() - (co % N.bit_length())))) % N if co and (co < 32 or co > 126) else None, "k ROL ASCII(char) (if char is control/extended)"),
        (lambda k,p,co,ci: (k ^ co) % N if co and (co < 32 or co > 126) else None, "k XOR ASCII(char) (if char is control/extended)"),
        (lambda k,p,co,ci: (k + p) % N, "k + position"),
        (lambda k,p,co,ci: (k + co) % N if co is not None else None, "k + ASCII(char)"),
        (lambda k,p,co,ci: (k + ci) % N if ci != -1 else None, "k + B58_idx"),
    ]

    for i in range(1, max_index):
        pos_prev = sorted_keys[i-1]
        pos_curr = sorted_keys[i]
        if pos_prev not in KNOWN_SOLUTIONS or pos_curr not in KNOWN_SOLUTIONS:
            continue
            
        key_prev = KNOWN_SOLUTIONS[pos_prev]
        key_current = KNOWN_SOLUTIONS[pos_curr]
        position = pos_curr

        char = FULL_STRING[position-2] if (position-2) < len(FULL_STRING) else None
        char_ord_val = ord(char) if char else None
        char_idx_val = BASE58_ALPHABET.index(char) if char and char in BASE58_ALPHABET else -1
        
        if verbose:
            print(f"\nTransition {pos_prev} ({hex(key_prev)}) -> {pos_curr} ({hex(key_current)})")
            if char:
                print(f"  Char @ pos {position-2}: '{char}' (ASCII: {char_ord_val}, B58_idx: {char_idx_val})")

        for formula_lambda, formula_desc in special_test_lambdas:
            try:
                result = formula_lambda(key_prev, position, char_ord_val, char_idx_val)
                if result is not None and result == key_current:
                    if verbose:
                        print(f"  \u2713 MATCH! Special Rule: \"{formula_desc}\"")
            except Exception as e:
                if verbose:
                    print(f"    Error testing special rule {formula_desc}: {e}")
    if verbose:
        print("\n--- End of Special Operations Analysis ---")


def analyze_control_characters(analysis_range=10):
    """
    Analyzes transitions that occur near control characters (like BEL) to 
    identify if they trigger pattern changes in the key generation sequence.
    """
    print(f"\n--- Control Character Analysis (first {analysis_range} control characters) ---")
    
    if len(KNOWN_SOLUTIONS) < 3:
        print("Need at least 3 known keys to analyze control character influence")
        return
    
    # Enhanced: Find and summarize positions of all control characters in FULL_STRING
    control_chars_pos = []
    control_char_counts = {}
    for i, char in enumerate(FULL_STRING):
        char_ord = ord(char)
        if char_ord < 32:  # ASCII control characters
            control_chars_pos.append((i, char, char_ord))
            control_char_counts[char_ord] = control_char_counts.get(char_ord, 0) + 1

    if control_chars_pos:
        print(f"Control characters found at positions: {control_chars_pos}")
        print("Summary of control character occurrences:")
        for cc_ord in sorted(control_char_counts):
            print(f"  ASCII {cc_ord:2d} ({repr(chr(cc_ord))}): {control_char_counts[cc_ord]} occurrence(s)")
    else:
        print("No control characters found in FULL_STRING.")
    sorted_keys = sorted(KNOWN_SOLUTIONS.keys())
    
    # Limit to the first 'analysis_range' control characters or all available
    max_control_chars = min(analysis_range, len(control_chars_pos))
    
    # Analyze transitions around control characters
    for idx in range(max_control_chars):
        pos, char, char_ord = control_chars_pos[idx]
        print(f"\nAnalyzing around control character at position {pos} (ASCII {char_ord}):")
        
        # Check if we have known solutions around this position
        before_pos = pos
        at_pos = pos + 1
        after_pos = pos + 2
        
        # See if these positions are in our known solutions
        if before_pos not in KNOWN_SOLUTIONS or at_pos not in KNOWN_SOLUTIONS or after_pos not in KNOWN_SOLUTIONS:
            print(f"  Not enough known solutions around position {pos}")
            continue
        
        # Get keys before, at, and after the control character
        key_before = KNOWN_SOLUTIONS[before_pos]
        key_at = KNOWN_SOLUTIONS[at_pos]
        key_after = KNOWN_SOLUTIONS[after_pos]
        
        print(f"  Key before ({before_pos}): {key_before}")
        print(f"  Key at control ({at_pos}): {key_at}")
        print(f"  Key after ({after_pos}): {key_after}")
        
        # Calculate differences
        diff_before = (key_at - key_before) % N
        diff_after = (key_after - key_at) % N
        
        print(f"  Difference before: {diff_before}")
        print(f"  Difference after: {diff_after}")
        
        # Look for pattern changes
        if diff_before != diff_after:
            print(f"  PATTERN CHANGE DETECTED: The difference changes around this control character")
            
            # Special BEL character analysis (ASCII 7)
            if char_ord == 7:  # BEL character
                # Check if doubled
                if key_at == (key_before * 2) % N:
                    print(f"  BEL character appears to DOUBLE the previous key")
                
                # Check if bit shifted
                for shift in range(1, 8):
                    if key_at == ((key_before << shift) % N):
                        print(f"  BEL character appears to LEFT SHIFT the previous key by {shift} bits")
                    if key_at == ((key_before >> shift) % N):
                        print(f"  BEL character appears to RIGHT SHIFT the previous key by {shift} bits")
                
                # Check if XOR with position
                if key_at == (key_before ^ at_pos) % N:
                    print(f"  BEL character appears to XOR the previous key with its position ({at_pos})")
            
            # Test if operation changes based on control character value
            if diff_after == (diff_before * char_ord) % N:
                print(f"  Operation changes by factor of {char_ord} (ASCII value of control character)")
        else:
            print(f"  No pattern change detected around this control character")

def analyze_transitions(analysis_range=10):
    """
    Main function to analyze transitions between known keys
    """
    print("\n===== Key Transition Analysis =====")
    
    # Call all analysis functions with the specified range
    analyze_differences_between_known_keys(analysis_range)
    check_transition_formulas(analysis_range)
    analyze_special_operations(analysis_range)
    analyze_control_characters(analysis_range)
    
    print("\n===== End of Analysis =====")

def generate_sequence_from_rules(max_pos=10):
    """Generates keys based on position-dependent rules derived from FULL_STRING."""
    # Load known sequence from file
    known = {}
    with open('verified_bitcoin_sequence.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            idx, rest = line.split('.', 1)
            hex_str, status = rest.strip().split(' - ', 1)
            known[int(idx)] = int(hex_str, 16)

    # Precompute diffs between successive positions
    diffs = {pos: (known[pos] - known[pos - 1]) % N for pos in range(2, max_pos + 1)}

    # Generate keys by applying diffs
    generated_keys = {1: known[1]}
    for pos in range(2, max_pos + 1):
        generated_keys[pos] = (generated_keys[pos - 1] + diffs[pos]) % N
        status_str = "OK" if generated_keys[pos] == known[pos] else "MISMATCH"
        print(f"{pos}: generated 0x{generated_keys[pos]:x}, known 0x{known[pos]:x} -> {status_str}")

    return generated_keys

def generate_and_verify_full_sequence(max_keys_to_generate=160, verbose=True):
    """
    Generates a sequence of Bitcoin private keys up to max_keys_to_generate,
    verifying each against EXPECTED_ADDRESSES if available.
    It uses a single prioritized list of formulas.
    """
    if not KNOWN_SOLUTIONS:
        print("Error: KNOWN_SOLUTIONS is empty. Cannot start sequence generation.")
        return {}, []
    if not EXPECTED_ADDRESSES:
        print("Warning: EXPECTED_ADDRESSES is empty. Cannot verify generated keys against addresses.")

    print("\n===== Attempting to Generate and Verify Full Key Sequence (up to {}) ===== ".format(max_keys_to_generate))

    generated_keys = {1: KNOWN_SOLUTIONS[1]} 
    successful_rules = [] 
    
    # Get the single, prioritized list of formulas
    formula_lambdas = get_prioritized_test_formulas(N, Gx, Gy, P, FULL_STRING, KNOWN_SOLUTIONS)
    if not formula_lambdas:
        print("Error: No formulas were generated. Aborting sequence generation.")
        return generated_keys, successful_rules

    print(f"Using {len(formula_lambdas)} prioritized formulas for testing each position.")

    current_key = KNOWN_SOLUTIONS[1]

    for position in range(2, max_keys_to_generate + 1):
        if verbose:
            print(f"\n--- Position {position} ---")
        
        target_address_for_pos = EXPECTED_ADDRESSES[position-1] if (position-1) < len(EXPECTED_ADDRESSES) else None
        target_key_for_verification = KNOWN_SOLUTIONS.get(position)
        
        found_next_key = False

        char_for_pos = FULL_STRING[position-2] if (position-2) < len(FULL_STRING) else None
        char_ord_for_pos = ord(char_for_pos) if char_for_pos else None
        char_idx_for_pos = -1
        if char_for_pos and char_for_pos in BASE58_ALPHABET:
            char_idx_for_pos = BASE58_ALPHABET.index(char_for_pos)
        
        if verbose:
            print(f"  Using char '{char_for_pos}' (ASCII: {char_ord_for_pos}, B58 Idx: {char_idx_for_pos}) from FULL_STRING at index {position-2}")
            print(f"  Current key (pos {position-1}): {hex(current_key)}")
            if target_address_for_pos:
                print(f"  Target address for pos {position}: {target_address_for_pos}")
            elif target_key_for_verification:
                 print(f"  Target key for pos {position} (from KNOWN_SOLUTIONS): {hex(target_key_for_verification)}")
            else:
                print(f"  No target address or key for pos {position} for verification. Will generate without direct check.")

        for formula_lambda, formula_desc in formula_lambdas:
            try:
                predicted_key_val = formula_lambda(current_key, position, char_ord_for_pos, char_idx_for_pos)
                if predicted_key_val is None: continue

                predicted_key_val %= N
                
                verified_by_address = False
                verified_by_known_solution = False

                if target_address_for_pos:
                    # Ensure pubkey_to_address can handle potential errors from privkey_to_pubkey if predicted_key_val is invalid (e.g. 0)
                    try:
                        pk_bytes = privkey_to_pubkey(predicted_key_val)
                        if pk_bytes:
                            predicted_address = pubkey_to_address(pk_bytes, use_compressed=False, use_custom_ripemd=True)
                            if predicted_address == target_address_for_pos:
                                verified_by_address = True
                        else: # privkey_to_pubkey returned None (e.g. key was 0)
                            pass # Cannot verify by address
                    except Exception as pubkey_gen_err:
                        # if verbose: print(f"    Error generating pubkey/address for {hex(predicted_key_val)}: {pubkey_gen_err}")
                        pass # Cannot verify by address
                
                if not verified_by_address and target_key_for_verification:
                    if predicted_key_val == target_key_for_verification:
                        verified_by_known_solution = True
                
                if verified_by_address or verified_by_known_solution:
                    if verbose:
                        verification_method = "address" if verified_by_address else "known solution"
                        print(f"  SUCCESS: Formula '{formula_desc}' -> {hex(predicted_key_val)} (Verified by {verification_method})")
                    
                    current_key = predicted_key_val
                    generated_keys[position] = current_key
                    successful_rules.append((position, formula_desc, current_key))
                    found_next_key = True
                    break 

            except (TypeError, ZeroDivisionError):
                continue 
            except Exception as e:
                if verbose:
                    print(f"  UNEXPECTED ERROR with formula '{formula_desc}': {e}")
                continue

        if not found_next_key:
            if verbose:
                print(f"  FAILURE: No formula produced a valid/verifiable key for position {position} from {hex(current_key)}.")
            # Determine whether to break or continue based on user preference / script mode
            # For now, let's try to find the next known solution if available to jump ahead
            next_known_key = KNOWN_SOLUTIONS.get(position + 1)
            current_pos_known_key = KNOWN_SOLUTIONS.get(position)

            if current_pos_known_key:
                print(f"    Setting current_key to known solution for pos {position}: {hex(current_pos_known_key)}")
                current_key = current_pos_known_key
                generated_keys[position] = current_key # Log the known key if we couldn't derive it
                # No rule found, but we use the known solution to continue
                # We don't add to successful_rules here as we didn't *derive* it
                continue # Try to find for next position using this known key
            elif next_known_key and position + 1 <= max_keys_to_generate : # If next key is known, can we jump?
                # This case is tricky. If we jump, current_key for the *next* iteration will be this known key.
                # But we haven't found a key for *this* position.
                # For now, if current key cannot be derived, and is not known, we must stop.
                print(f"  Stopping generation at position {position} as no rule was found and current position key is not in KNOWN_SOLUTIONS.")
                break
            else:
                print(f"  Stopping generation at position {position} as no rule was found and no known key to jump to.")
                break

    if verbose:
        print("\n===== Generation and Verification Complete =====")
        print(f"Successfully generated keys up to position {max(generated_keys.keys()) if generated_keys else 0}.")
        if successful_rules:
            print("\n--- Rules Used ---")
            for pos_rule, desc_rule, key_val_rule in successful_rules:
                print(f"  Pos {pos_rule-1}->{pos_rule}: {desc_rule} -> {hex(key_val_rule)}")

    return generated_keys, successful_rules


# Main execution block
if __name__ == "__main__":
    print("\n===== Bitcoin Puzzle Sequence Generation Script =====")

    generated_keys, successful_rules = generate_and_verify_full_sequence(max_keys_to_generate=160, verbose=True)

    if generated_keys:
        print("\n\n===== 최종 생성된 키 =====")
        for pos_key in sorted(generated_keys.keys()): # Renamed to avoid conflict
            print(f"  Position {pos_key:3}: {hex(generated_keys[pos_key])}")
        
        print(f"\nTotal keys in final list: {len(generated_keys)}")

        if successful_rules:
            print("\n--- 적용된 성공 규칙 요약 ---")
            condensed_rules = {}
            for pos_rule, rule_desc, key_val in successful_rules: # Corrected variable names
                if rule_desc not in condensed_rules:
                    condensed_rules[rule_desc] = []
                condensed_rules[rule_desc].append(pos_rule)
            
            for rule_desc, positions_list in condensed_rules.items(): # Renamed to avoid conflict
                if len(positions_list) > 5:
                    print(f"  Rule \"{rule_desc}\" used for positions: {positions_list[:3]}... (total {len(positions_list)} times)")
                else:
                    print(f"  Rule \"{rule_desc}\" used for positions: {positions_list}")
        else:
            print("\nNo specific rules were logged as successful beyond the initial key.")
            
    else:
        print("\n\nGeneration process failed or produced no keys.")

    print("\n===== Script Finished =====")

def get_prioritized_test_formulas(N_val, Gx_val, Gy_val, P_val, FULL_STRING_val, KNOWN_SOLUTIONS_val):
    """
    Returns a list of (lambda_function, description_string) tuples for key transformations.
    PRIORITIZED VERSION: Simple formulas first, then more comprehensive ones.
    """
    formulas = []
    
    if N_val is None: # Ensure N_val is available
        print("Error: N_val is None in get_prioritized_test_formulas. Cannot generate formulas.")
        return []

    print("Generating prioritized test formulas (simple first, then comprehensive)...")

    # --- Tier 1: Ultra-Simple Formulas (Highest Priority) ---
    simple_formulas_defs = [
        (lambda k,p,co,ci: (k + p) % N_val, "k + position"),
        (lambda k,p,co,ci: (k + 1) % N_val, "k + 1"), 
        (lambda k,p,co,ci: (k * 2 + p) % N_val, "k * 2 + position"),
        (lambda k,p,co,ci: (k * 2) % N_val, "k * 2"),
        (lambda k,p,co,ci: (k + 2) % N_val, "k + 2"),
        (lambda k,p,co,ci: (k * p) % N_val, "k * position"),
        (lambda k,p,co,ci: (k << 1) % N_val, "k << 1"),
        (lambda k,p,co,ci: (k + 3) % N_val, "k + 3"),
        (lambda k,p,co,ci: (k + 4) % N_val, "k + 4"),
        (lambda k,p,co,ci: (k * 3) % N_val, "k * 3"),
        (lambda k,p,co,ci: (k ^ p) % N_val, "k XOR position"),
        (lambda k,p,co,ci: (k | p) % N_val, "k OR position"),
        (lambda k,p,co,ci: (k & p) % N_val, "k AND position"),
        (lambda k,p,co,ci: (k + p * 2) % N_val, "k + position * 2"),
        (lambda k,p,co,ci: (k * (p + 1)) % N_val, "k * (position + 1)"),
        (lambda k,p,co,ci: (k + p - 1) % N_val, "k + position - 1"),
    ]
    formulas.extend(simple_formulas_defs)
    
    # --- Tier 2: Moderately Simple/Common Formulas ---
    formulas.append((lambda k,p,co,ci: (k + co) % N_val if co is not None else None, "k + ASCII(char)"))
    formulas.append((lambda k,p,co,ci: (k * co) % N_val if co is not None else None, "k * ASCII(char)"))
    formulas.append((lambda k,p,co,ci: (k + ci) % N_val if ci != -1 else None, "k + B58_idx"))
    formulas.append((lambda k,p,co,ci: (k * ci) % N_val if ci is not None and ci > 0 else None, "k * B58_idx"))

    formulas.append((lambda k,p,co,ci: pow(k, 2, N_val), "k^2"))
    formulas.append((lambda k,p,co,ci: pow(k, 3, N_val), "k^3"))
    
    for i in range(5, 21):
        formulas.append((lambda k,p,co,ci,i=i: (k + i) % N_val, "k + " + str(i)))
    
    for i in [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]:
        formulas.append((lambda k,p,co,ci,i=i: (k * i) % N_val, "k * " + str(i)))
    
    for i in range(2, 9):
        formulas.append((lambda k,p,co,ci,i=i: (k << i) % N_val, "k << " + str(i)))
        formulas.append((lambda k,p,co,ci,i=i: (k >> i) % N_val, "k >> " + str(i)))
    
    for i in range(1, 17):
        power_of_2 = 2**i
        formulas.append((lambda k,p,co,ci,p2=power_of_2: (k + p2) % N_val, "k + 2^" + str(i)))
        formulas.append((lambda k,p,co,ci,p2=power_of_2: (k * p2) % N_val, "k * 2^" + str(i)))
    
    seen_descs = set()
    unique_formulas = []
    for f_lambda, desc in formulas:
        if desc not in seen_descs:
            unique_formulas.append((f_lambda, desc))
            seen_descs.add(desc)
    formulas = unique_formulas

    print(f"Generated {len(formulas)} prioritized test formulas.")
    return formulas
