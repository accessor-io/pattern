import sys, hashlib, base58, ecdsa
sys.path.append('.')
from key_sequence_generator import privkey_to_pubkey, pubkey_point_to_bytes
key70_hex='349b84b6431a6c4ef1'
key70=int(key70_hex,16)
expected_addr='1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU'
# get hash160 from address
alphabet='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def base58_decode_full(s):
    n=0
    for c in s:
        n=n*58+alphabet.index(c)
    h=n.to_bytes((n.bit_length()+7)//8,'big')
    pad=0
    for c in s:
        if c=='1': pad+=1
        else: break
    return b'\x00'*pad+h

b=base58_decode_full(expected_addr)
expected_h160=b[1:-4]
print('expected hash160',expected_h160.hex())

def addr_of(k):
    pt=privkey_to_pubkey(k)
    comp=pubkey_point_to_bytes(pt, compressed=True)
    sha=hashlib.sha256(comp).digest()
    ripe=hashlib.new('ripemd160',sha).digest()
    return ripe

pred_diff=970436974005023690483
start=pred_diff-10**9
end=pred_diff+10**9
step=1000000
print('searching', (end-start)//step)
for diff in range(start,end,step):
    k=key70+diff
    h=addr_of(k)
    if h==expected_h160:
        print('Found diff',diff)
        print('key',hex(k))
        break 