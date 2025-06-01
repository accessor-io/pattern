import sys, hashlib, base58, ecdsa
sys.path.append('.')
from key_sequence_generator import privkey_to_pubkey, pubkey_point_to_bytes, pubkey_to_address
priv=1
point=privkey_to_pubkey(priv)
our_comp=pubkey_point_to_bytes(point, compressed=True)
print('Our comp', our_comp.hex())
# external
sk=ecdsa.SigningKey.from_secret_exponent(priv, curve=ecdsa.SECP256k1)
pt=sk.verifying_key.pubkey.point
x=pt.x(); y=pt.y()
ext_comp=(b'\x02' if y%2==0 else b'\x03') + x.to_bytes(32,'big')
print('Ext comp', ext_comp.hex())
print('Equal?', our_comp==ext_comp) 