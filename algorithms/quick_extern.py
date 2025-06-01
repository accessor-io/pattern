import ecdsa, hashlib, base58
priv_int=1
sk=ecdsa.SigningKey.from_secret_exponent(priv_int, curve=ecdsa.SECP256k1)
point=sk.verifying_key.pubkey.point
x=point.x()
y=point.y()
comp=(b'\x02' if y%2==0 else b'\x03') + x.to_bytes(32,'big')
print('Compressed pubkey',comp.hex())
sha=hashlib.sha256(comp).digest()
ripe=hashlib.new('ripemd160', sha).digest()
version=b'\x00'+ripe
checksum=hashlib.sha256(hashlib.sha256(version).digest()).digest()[:4]
addr=base58.b58encode(version+checksum).decode()
print('Address',addr) 