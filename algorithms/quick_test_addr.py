import sys
sys.path.append('.')
from key_sequence_generator import privkey_to_pubkey, pubkey_point_to_bytes, pubkey_to_address, EXPECTED_ADDRESSES
priv_int=1
pt=privkey_to_pubkey(priv_int)
unc=pubkey_point_to_bytes(pt, compressed=False)
comp=pubkey_point_to_bytes(pt, compressed=True)
print('Expected:', EXPECTED_ADDRESSES[0])
print('Unc custom :', pubkey_to_address(unc, use_compressed=False, use_custom_ripemd=True))
print('Unc standard:', pubkey_to_address(unc, use_compressed=False, use_custom_ripemd=False))
print('Comp custom :', pubkey_to_address(comp, use_compressed=True, use_custom_ripemd=True))
print('Comp standard:', pubkey_to_address(comp, use_compressed=True, use_custom_ripemd=False)) 