import hashlib, base58
pub_hex='02145d2611c823a396ef6712ce0f712f09b9b4f3135e3e0aa3230fb9b6d08d1e16'
pub_bytes=bytes.fromhex(pub_hex)
sha=hashlib.sha256(pub_bytes).digest()
ripe=hashlib.new('ripemd160', sha).digest()
version=b'\x00'+ripe
checksum=hashlib.sha256(hashlib.sha256(version).digest()).digest()[:4]
addr=base58.b58encode(version+checksum).decode()
print(addr) 