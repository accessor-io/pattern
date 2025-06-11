import hashlib
import base58

def sha256(data):
    """Perform SHA256 hash on data."""
    return hashlib.sha256(data).digest()

def ripemd160(data):
    """Perform RIPEMD160 hash on data."""
    ripemd = hashlib.new('ripemd160')
    ripemd.update(data)
    return ripemd.digest()

def hash160(data):
    """Perform RIPEMD160(SHA256()) on data."""
    return ripemd160(sha256(data))

def double_sha256(data):
    """Perform double SHA256 hash on data."""
    return sha256(sha256(data))

def encode_base58check(data):
    """Encode data using Base58Check encoding."""
    # Add version byte in front (0x00 for mainnet addresses)
    versioned = b'\x00' + data
    
    # Add 4 bytes of double SHA256 as checksum
    checksum = double_sha256(versioned)[:4]
    
    # Combine everything and encode to base58
    binary = versioned + checksum
    return base58.b58encode(binary).decode('ascii')

def private_key_to_compressed_public_key(private_key_int):
    """Convert a private key to its compressed public key."""
    try:
        import ecdsa
        signing_key = ecdsa.SigningKey.from_secret_exponent(private_key_int, curve=ecdsa.SECP256k1)
        verifying_key = signing_key.get_verifying_key()
        
        point_x = verifying_key.pubkey.point.x()
        point_y = verifying_key.pubkey.point.y()
        
        if point_y % 2 == 0:
            prefix = b'\x02'
        else:
            prefix = b'\x03'
        
        return prefix + point_x.to_bytes(32, byteorder='big')
    except ImportError:
        raise ImportError("Please install 'ecdsa' package: pip install ecdsa")

def private_key_to_address(private_key_int, compressed=True):
    """Convert a private key integer to a Bitcoin address."""
    try:
        # Convert private key to public key
        if compressed:
            public_key = private_key_to_compressed_public_key(private_key_int)
        else:
            raise NotImplementedError("Uncompressed addresses not implemented")
        
        # Perform RIPEMD160(SHA256()) on public key
        h160 = hash160(public_key)
        
        # Create address using Base58Check encoding
        return encode_base58check(h160)
    except Exception as e:
        print(f"Error converting private key to address: {e}")
        return None

def validate_private_key(private_key_int, expected_address):
    """Validate if a private key generates the expected Bitcoin address."""
    if private_key_int >= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141:
        return False
    
    generated_address = private_key_to_address(private_key_int)
    return generated_address == expected_address

# Dictionary mapping puzzle numbers to their expected addresses
EXPECTED_ADDRESSES = {
    1: "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH",
    2: "1CUNEBjYrCn2y1SdiUMohaKUi4wpP326Lb",
    3: "19ZewH8Kk1PDbSNdJ97FP4EiCjTRaZMZQA",
    4: "1EhqbyUMvvs7BfL8goY6qcPbD6YKfPqb7e",
    5: "1E6NuFjCi27W5zoXg8TRdcSRq84zJeBW3k",
    6: "1PitScNLyp2HCygzadCh7FveTnfmpPbfp8",
    7: "1McVt1vMtCC7yn5b9wgX1833yCcLXzueeC",
    8: "1M92tSqNmQLYw33fuBvjmeadirh1ysMBxK",
    9: "1CQFwcjw1dwhtkVWBttNLDtqL7ivBonGPV",
    10: "1LeBZP5QCwwgXRtmVUvTVrraqPUokyLHqe",
    11: "1PgQVLmst3Z314JrQn5TNiys8Hc38TcXJu",
    12: "1DBaumZxUkM4qMQRt2LVWyFJq5kDtSZQot",
    13: "1Pie8JkxBT6MGPz9Nvi3fsPkr2D8q3GBc1",
    14: "1ErZWg5cFCe4Vw5BzgfzB74VNLaXEiEkhk",
    15: "1QCbW9HWnwQWiQqVo5exhAnmfqKRrCRsvW",
    16: "1BDyrQ6WoF8VN3g9SAS1iKZcPzFfnDVieY",
    17: "1HduPEXZRdG26SUT5Yk83mLkPyjnZuJ7Bm",
    18: "1GnNTmTVLZiqQfLbAdp9DVdicEnB5GoERE",
    19: "1NWmZRpHH4XSPwsW6dsS3nrNWfL1yrJj4w",
    20: "1HsMJxNiV7TLxmoF6uJNkydxPFDog4NQum",
    21: "14oFNXucftsHiUMY8uctg6N487riuyXs4h",
    22: "1CfZWK1QTQE3eS9qn61dQjV89KDjZzfNcv",
    23: "1L2GM8eE7mJWLdo3HZS6su1832NX2txaac",
    24: "1rSnXMr63jdCuegJFuidJqWxUPV7AtUf7",
    25: "15JhYXn6Mx3oF4Y7PcTAv2wVVAuCFFQNiP",
    26: "1JVnST957hGztonaWK6FougdtjxzHzRMMg",
    27: "128z5d7nN7PkCuX5qoA4Ys6pmxUYnEy86k",
    28: "12jbtzBb54r97TCwW3G1gCFoumpckRAPdY",
    29: "19EEC52krRUK1RkUAEZmQdjTyHT7Gp1TYT",
    30: "1LHtnpd8nU5VHEMkG2TMYYNUjjLc992bps",
    31: "1LhE6sCTuGae42Axu1L1ZB7L96yi9irEBE",
    32: "1FRoHA9xewq7DjrZ1psWJVeTer8gHRqEvR",
    33: "187swFMjz1G54ycVU56B7jZFHFTNVQFDiu",
    34: "1PWABE7oUahG2AFFQhhvViQovnCr4rEv7Q",
    35: "1PWCx5fovoEaoBowAvF5k91m2Xat9bMgwb",
    36: "1Be2UF9NLfyLFbtm3TCbmuocc9N1Kduci1",
    37: "14iXhn8bGajVWegZHJ18vJLHhntcpL4dex",
    38: "1HBtApAFA9B2YZw3G2YKSMCtb3dVnjuNe2",
    39: "122AJhKLEfkFBaGAd84pLp1kfE7xK3GdT8",
    40: "1EeAxcprB2PpCnr34VfZdFrkUWuxyiNEFv",
    41: "1L5sU9qvJeuwQUdt4y1eiLmquFxKjtHr3E",
    42: "1E32GPWgDyeyQac4aJxm9HVoLrrEYPnM4N",
    43: "1PiFuqGpG8yGM5v6rNHWS3TjsG6awgEGA1",
    44: "1CkR2uS7LmFwc3T2jV8C1BhWb5mQaoxedF",
    45: "1NtiLNGegHWE3Mp9g2JPkgx6wUg4TW7bbk",
    46: "1F3JRMWudBaj48EhwcHDdpeuy2jwACNxjP",
    47: "1Pd8VvT49sHKsmqrQiP61RsVwmXCZ6ay7Z",
    48: "1DFYhaB2J9q1LLZJWKTnscPWos9VBqDHzv",
    49: "12CiUhYVTTH33w3SPUBqcpMoqnApAV4WCF",
    50: "1MEzite4ReNuWaL5Ds17ePKt2dCxWEofwk",
    51: "1NpnQyZ7x24ud82b7WiRNvPm6N8bqGQnaS",
    52: "15z9c9sVpu6fwNiK7dMAFgMYSK4GqsGZim",
    53: "15K1YKJMiJ4fpesTVUcByoz334rHmknxmT",
    54: "1KYUv7nSvXx4642TKeuC2SNdTk326uUpFy",
    55: "1LzhS3k3e9Ub8i2W1V8xQFdB8n2MYCHPCa",
    56: "17aPYR1m6pVAacXg1PTDDU7XafvK1dxvhi",
    57: "15c9mPGLku1HuW9LRtBf4jcHVpBUt8txKz",
    58: "1Dn8NF8qDyyfHMktmuoQLGyjWmZXgvosXf",
    59: "1HAX2n9Uruu9YDt4cqRgYcvtGvZj1rbUyt",
    60: "1Kn5h2qpgw9mWE5jKpk8PP4qvvJ1QVy8su",
    61: "1AVJKwzs9AskraJLGHAZPiaZcrpDr1U6AB",
    62: "1Me6EfpwZK5kQziBwBfvLiHjaPGxCKLoJi",
    63: "1NpYjtLira16LfGbGwZJ5JbDPh3ai9bjf4",
    64: "16jY7qLJnxb7CHZyqBP8qca9d51gAjyXQN",
    65: "18ZMbwUFLMHoZBbfpCjUJQTCMCbktshgpe",
    66: "13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so"
} 