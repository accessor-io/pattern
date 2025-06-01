import sys, hashlib, base58, ecdsa
sys.path.append('.')
from key_sequence_generator import privkey_to_pubkey, pubkey_point_to_bytes, pubkey_to_address
priv=1
point=privkey_to_pubkey(priv)
comp=pubkey_point_to_bytes(point, compressed=True)
addr_ours=pubkey_to_address(comp, use_compressed=True, use_custom_ripemd=False)
print('Our addr', addr_ours)
# external
sha=hashlib.sha256(comp).digest()
ripe=hashlib.new('ripemd160', sha).digest()
version=b'\x00'+ripe
checksum=hashlib.sha256(hashlib.sha256(version).digest()).digest()[:4]
addr_ext=base58.b58encode(version+checksum).decode()
print('Ext addr', addr_ext) 