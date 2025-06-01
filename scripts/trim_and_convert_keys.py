import ecdsa, base58, hashlib

keys = [
    '00000000000000000000000000000000000000000000000000000e2b35a358f122fa143c05',
    '000000000000000000000000000000000000000000000000000002ec18388d5446cd610b53cba',
    '000000000000000000000000000000000000000000000000000000ade6d7ce3b9b174176b015f4d',
    '000000000000000000000000000000000000000000000000000000075070a1a009d4efae164cb9e3c',
    '000000000000000000000000000000000000000000000000000000180788e47e326c236fb6d5ad1f43',
    '0000000000000000000000000000000000000000000000000000006abe1f9b67e1149d18b63ac4ffdf',
    '0000000000000000000000000000000000000000000000000000001eb25c90795d61c2c675b852189a21',
]

print('Key | 64-char Hex | Compressed Address')
print('-'*80)
for i, k in enumerate(keys):
    trimmed = k[-64:]
    key_int = int(trimmed, 16)
    sk = ecdsa.SigningKey.from_secret_exponent(key_int, curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    point = vk.pubkey.point
    x = point.x()
    y = point.y()
    prefix = b'\x02' if y % 2 == 0 else b'\x03'
    pubkey = prefix + x.to_bytes(32, 'big')
    h160 = hashlib.new('ripemd160', hashlib.sha256(pubkey).digest()).digest()
    addr = b'\x00' + h160
    checksum = hashlib.sha256(hashlib.sha256(addr).digest()).digest()[:4]
    compressed_address = base58.b58encode(addr + checksum).decode()
    print(f'{i+72}: {trimmed} | {compressed_address}') 