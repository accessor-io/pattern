from decode_ascii_keys import decode_hex_key, CONTROL_CHAR_MAP
import hashlib
import base58
from bitcoin.core.key import PrivateKey
from bitcoin.core.script import RIPEMD160

def parse_decrypted_seed(seed_data):
    """Process decrypted seed using existing decode logic"""
    version = seed_data[0]
    control_chars = seed_data[1:4]  # ESC,FS,GS
    entropy = seed_data[4:68]
    checksum = seed_data[68:72]
    
    # Use existing decode_hex_key to process
    decoded = decode_hex_key(entropy.hex())
    return {
        'version': version,
        'control_chars': [CONTROL_CHAR_MAP[b] for b in control_chars],
        'entropy': decoded,
        'checksum': checksum.hex()
    } 

def generate_address(entropy):
    """Use existing puzzle solver logic to generate address"""
    # Reuse code from bitcoin_puzzle67_pro_solver.py
    private_key = bytes.fromhex(entropy)
    privkey = PrivateKey(private_key, raw=True)
    pubkey = privkey.pubkey.serialize(compressed=True)
    
    sha = hashlib.sha256(pubkey).digest()
    ripemd = RIPEMD160.new(sha).digest()
    return base58.b58encode_check(b'\x00' + ripemd).decode() 

def process_wallet(wallet_path):
    """Complete processing pipeline"""
    # Decrypt seed
    seed_data = decrypt_wallet(wallet_path)
    
    # Parse using existing decode_ascii_keys logic
    parsed = parse_decrypted_seed(seed_data)
    
    # Generate address using existing solver code
    address = generate_address(parsed['entropy'])
    
    return {
        'private_key': seed_data.hex(),
        'control_chars': parsed['control_chars'],
        'address': address,
        'checksum_valid': validate_checksum(seed_data)
    } 