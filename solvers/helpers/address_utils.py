import hashlib
import base58
import bech32
from Crypto.Hash import RIPEMD160
from secp256k1 import PrivateKey

def private_key_to_address(private_key_hex: str, compressed: bool = True) -> str:
    """Generate legacy P2PKH address (1...) from private key"""
    if len(private_key_hex) != 64:
        return "Invalid private key length"
        
    try:
        privkey = PrivateKey(bytes.fromhex(private_key_hex))
        pubkey = privkey.pubkey.serialize(compressed=compressed)
        
        sha = hashlib.sha256(pubkey).digest()
        ripemd = RIPEMD160.new()
        ripemd.update(sha)
        hash160 = ripemd.digest()
        
        version = b'\x00'
        payload = version + hash160
        checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        
        return base58.b58encode(payload + checksum).decode('utf-8')
    except Exception as e:
        return f"Address generation error: {str(e)}"

def private_key_to_wif(private_key_hex: str, compressed: bool = True) -> str:
    """Convert hex private key to Wallet Import Format (WIF)"""
    extended = bytes.fromhex('80' + private_key_hex)
    if compressed:
        extended += b'\x01'
    
    first_sha = hashlib.sha256(extended).digest()
    checksum = hashlib.sha256(first_sha).digest()[:4]
    return base58.b58encode(extended + checksum).decode('utf-8') 