import ecdsa
import hashlib
import base58

input_file = 'all_wolfram_rules_combined.txt'
output_file = 'dec_to_btc_address.txt'

def decimal_to_padded_hex(decimal_str):
    hex_str = hex(int(decimal_str))[2:]  # Remove '0x'
    return hex_str.zfill(64)

def private_key_to_compressed_address(hex_key):
    private_key_bytes = bytes.fromhex(hex_key)
    sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    x = vk.pubkey.point.x()
    y = vk.pubkey.point.y()
    prefix = b'\x02' if y % 2 == 0 else b'\x03'
    compressed_pubkey = prefix + x.to_bytes(32, 'big')
    sha256 = hashlib.sha256(compressed_pubkey).digest()
    ripemd160 = hashlib.new('ripemd160', sha256).digest()
    network_byte = b'\x00'  # Mainnet
    payload = network_byte + ripemd160
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    address = base58.b58encode(payload + checksum).decode()
    return address

with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    for line in infile:
        if 'Decimall:' in line:
            parts = line.split('Decimall:')
            after = parts[1].strip()
            num_str = ''
            for c in after:
                if c.isdigit():
                    num_str += c
                else:
                    break
            if num_str:
                padded_hex = decimal_to_padded_hex(num_str)
                try:
                    btc_address = private_key_to_compressed_address(padded_hex)
                except Exception as e:
                    btc_address = f'ERROR: {e}'
                outfile.write(f"{num_str},{padded_hex},{btc_address}\n") 