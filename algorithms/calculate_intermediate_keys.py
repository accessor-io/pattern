#!/usr/bin/env python3
"""
Calculate and verify intermediate Bitcoin puzzle keys.
These addresses were created in the famous 2015 Bitcoin puzzle transaction.
"""

import hashlib
import ecdsa

# Bitcoin elliptic curve parameters
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

# Expected Bitcoin addresses for the puzzle (positions 1-160)
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

# Custom RIPEMD160 implementation
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
            word_index = j
            round_num = j // 16
            round_num_p = (79 - j) // 16
            word_idx = (j % 16)
            word_idx_p = (j % 16)
            
            T = rol(a + f(j, b, c, d) + w[word_idx] + k[round_num], s[j]) + e
            a, b, c, d, e = e, T, b, rol(c, 10), d

            def fp(j, x, y, z):
                jp = 79 - j
                if jp < 16: return x ^ y ^ z
                elif jp < 32: return (x & z) | (y & ~z)
                elif jp < 48: return (x | ~y) ^ z
                elif jp < 64: return (x & y) | (~x & z)
                else: return x ^ (y | ~z)

            word_idx_p = (j % 16) ^ ((79-j) // 16)
            Tp = rol(ap + fp(j, bp, cp, dp) + w[word_idx_p] + kp[round_num_p], s[79 - j]) + ep
            ap, bp, cp, dp, ep = ep, Tp, bp, rol(cp, 10), dp

        dh = [h[1], h[2], h[3], h[4], h[0]]
        h[0] = (dh[0] + c + dp) & 0xffffffff
        h[1] = (dh[1] + d + ep) & 0xffffffff
        h[2] = (dh[2] + e + ap) & 0xffffffff
        h[3] = (dh[3] + a + bp) & 0xffffffff
        h[4] = (dh[4] + b + cp) & 0xffffffff

    return bytes().join(x.to_bytes(4, "little") for x in h)

# Base58 encoding
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def base58_encode(b):
    n = int.from_bytes(b, 'big')
    if n == 0:
        return BASE58_ALPHABET[0] * len(b)
    res = []
    while n > 0:
        n, rem = divmod(n, 58)
        res.append(BASE58_ALPHABET[rem])
    res = "".join(reversed(res))
    czero = 0
    while czero < len(b) and b[czero] == 0:
        res = BASE58_ALPHABET[0] + res
        czero += 1
    return res

def base58_check_encode(version, payload):
    versioned = version + payload
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    return base58_encode(versioned + checksum)

# EC operations
def multiply(p, n):
    """Scalar multiplication of point p by integer n"""
    if n == 0 or p is None:
        return None
    if n < 0:
        return multiply(ecdsa.ellipticcurve.Point(CURVE, p.x(), (-p.y()) % P), -n)
    r = None
    m2 = p
    bit_length = n.bit_length()
    for i in range(bit_length):
        if n & (1 << i):
            if r is None:
                r = m2
            else:
                # Point addition
                if r.x() == m2.x():
                    if (r.y() + m2.y()) % P == 0:
                        r = None
                        continue
                    # Point doubling
                    numerator = (3 * r.x() * r.x()) % P
                    denominator = (2 * r.y()) % P
                    lam = (numerator * pow(denominator, P - 2, P)) % P
                else:
                    lam = ((m2.y() - r.y()) * pow(m2.x() - r.x(), P - 2, P)) % P
                x3 = (lam * lam - r.x() - m2.x()) % P
                y3 = (lam * (r.x() - x3) - r.y()) % P
                r = ecdsa.ellipticcurve.Point(CURVE, x3, y3)
        # Point doubling
        if m2 is not None:
            numerator = (3 * m2.x() * m2.x()) % P
            denominator = (2 * m2.y()) % P
            if denominator != 0:
                lam = (numerator * pow(denominator, P - 2, P)) % P
                x3 = (lam * lam - 2 * m2.x()) % P
                y3 = (lam * (m2.x() - x3) - m2.y()) % P
                m2 = ecdsa.ellipticcurve.Point(CURVE, x3, y3)
            else:
                m2 = None
    return r

# Create curve and generator
CURVE = ecdsa.ellipticcurve.CurveFp(P, 0, 7)
GENERATOR = ecdsa.ellipticcurve.Point(CURVE, Gx, Gy)

def privkey_to_address(privkey_int):
    """Convert private key to Bitcoin address"""
    # Get public key
    pubkey_point = multiply(GENERATOR, privkey_int)
    if pubkey_point is None:
        return None
    
    # Uncompressed public key
    pubkey_bytes = b'\x04' + pubkey_point.x().to_bytes(32, 'big') + pubkey_point.y().to_bytes(32, 'big')
    
    # Hash160 (SHA256 then RIPEMD160)
    sha256_hash = hashlib.sha256(pubkey_bytes).digest()
    ripemd160_hash = custom_ripemd160(sha256_hash)
    
    # Create address
    return base58_check_encode(b'\x00', ripemd160_hash)

def calculate_intermediate_keys():
    """Calculate keys for intermediate positions using k + constant pattern"""
    
    # Load verified keys from file
    verified_keys = {}
    try:
        with open('verified_bitcoin_sequence.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if not line or not line[0].isdigit():
                    continue
                parts = line.split('.', 1)
                if len(parts) != 2:
                    continue
                pos = int(parts[0])
                hex_and_status = parts[1].strip()
                if ' - ' in hex_and_status:
                    hex_key = hex_and_status.split(' - ')[0].strip()
                    status = hex_and_status.split(' - ')[1].strip()
                else:
                    hex_key = hex_and_status.strip()
                    status = "UNKNOWN"
                verified_keys[pos] = {
                    'key': int(hex_key, 16),
                    'status': status
                }
    except Exception as e:
        print(f"Error loading verified keys: {e}")
        return
    
    print("=== CALCULATING INTERMEDIATE BITCOIN PUZZLE KEYS ===")
    print("These addresses were created in the famous 2015 Bitcoin puzzle transaction")
    print()
    
    # Identify gaps in the sequence
    gaps = []
    sorted_positions = sorted(verified_keys.keys())
    
    for i in range(len(sorted_positions) - 1):
        pos1 = sorted_positions[i]
        pos2 = sorted_positions[i + 1]
        if pos2 - pos1 > 1:
            for missing_pos in range(pos1 + 1, pos2):
                gaps.append(missing_pos)
    
    print(f"Found {len(gaps)} missing positions to calculate")
    print(f"Missing positions: {gaps[:20]}{'...' if len(gaps) > 20 else ''}")
    print()
    
    # Calculate missing keys
    predictions = {}
    for missing_pos in gaps:
        # Find closest known keys before this position
        prev_pos = missing_pos - 1
        while prev_pos > 0 and prev_pos not in verified_keys:
            prev_pos -= 1
        
        if prev_pos == 0:
            print(f"Cannot calculate position {missing_pos}: no previous key found")
            continue
        
        # Look for pattern in recent differences
        differences = []
        test_pos = prev_pos
        while test_pos > 1 and len(differences) < 5:
            if test_pos in verified_keys and test_pos - 1 in verified_keys:
                diff = verified_keys[test_pos]['key'] - verified_keys[test_pos - 1]['key']
                differences.append((test_pos, diff))
            test_pos -= 1
        
        if not differences:
            print(f"Cannot calculate position {missing_pos}: no differences found")
            continue
        
        # Estimate the constant for this position
        # For now, use simple growth rate estimation
        if len(differences) >= 2:
            # Calculate average growth rate
            growth_rates = []
            for i in range(1, len(differences)):
                if differences[i-1][1] > 0:
                    growth = differences[i][1] / differences[i-1][1]
                    growth_rates.append(growth)
            
            if growth_rates:
                avg_growth = sum(growth_rates) / len(growth_rates)
                # Estimate constant for missing position
                steps_ahead = missing_pos - prev_pos
                estimated_constant = int(differences[0][1] * (avg_growth ** steps_ahead))
            else:
                # Fallback: use last known difference
                estimated_constant = differences[0][1]
        else:
            # Only one difference known
            estimated_constant = differences[0][1]
        
        # Calculate predicted key
        base_key = verified_keys[prev_pos]['key']
        predicted_key = base_key + estimated_constant
        
        # Generate address
        predicted_address = privkey_to_address(predicted_key)
        
        predictions[missing_pos] = {
            'key': predicted_key,
            'constant': estimated_constant,
            'address': predicted_address,
            'base_pos': prev_pos
        }
        
        # Check if it matches expected address
        if missing_pos <= 160 and predicted_address == EXPECTED_ADDRESSES[missing_pos - 1]:
            print(f"✓ Position {missing_pos}: VERIFIED! Address matches puzzle target")
            print(f"  Key: 0x{predicted_key:064x}")
            print(f"  Constant: {estimated_constant:,} (from position {prev_pos})")
            print(f"  Address: {predicted_address}")
        else:
            print(f"❓ Position {missing_pos}: Predicted (needs verification)")
            print(f"  Key: 0x{predicted_key:064x}")
            print(f"  Constant: {estimated_constant:,} (from position {prev_pos})")
            print(f"  Address: {predicted_address}")
            if missing_pos <= 160:
                print(f"  Expected: {EXPECTED_ADDRESSES[missing_pos - 1]}")
        print()
    
    # Test some specific intermediate positions
    print("\n=== TESTING SPECIFIC INTERMEDIATE POSITIONS ===")
    test_positions = [69, 71, 72, 73, 74, 76, 77, 78, 79]
    
    for pos in test_positions:
        if pos in verified_keys:
            continue
            
        print(f"\n--- Position {pos} ---")
        
        # Method 1: Use pattern from adjacent known keys
        if pos - 1 in verified_keys and pos + 1 in verified_keys:
            # We have keys on both sides
            key_before = verified_keys[pos - 1]['key']
            key_after = verified_keys[pos + 1]['key']
            total_diff = key_after - key_before
            
            # Assume linear growth between the two
            predicted_key = key_before + total_diff // 2
            predicted_address = privkey_to_address(predicted_key)
            
            print(f"Method 1 (interpolation):")
            print(f"  Key: 0x{predicted_key:064x}")
            print(f"  Address: {predicted_address}")
            if pos <= 160:
                print(f"  Expected: {EXPECTED_ADDRESSES[pos - 1]}")
                print(f"  Match: {'YES' if predicted_address == EXPECTED_ADDRESSES[pos - 1] else 'NO'}")
        
        # Method 2: Use growth pattern
        if pos in predictions:
            pred = predictions[pos]
            print(f"\nMethod 2 (growth pattern):")
            print(f"  Key: 0x{pred['key']:064x}")
            print(f"  Address: {pred['address']}")
            if pos <= 160:
                print(f"  Expected: {EXPECTED_ADDRESSES[pos - 1]}")
                print(f"  Match: {'YES' if pred['address'] == EXPECTED_ADDRESSES[pos - 1] else 'NO'}")

if __name__ == "__main__":
    calculate_intermediate_keys() 