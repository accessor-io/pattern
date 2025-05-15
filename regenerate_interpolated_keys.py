import math
key_70 = int('0000000000000000000000000000000000000000000000349b84b6431a6c4ef1', 16)
key_75 = int('0000000000000000000000000000000000000000000004c5ce114686a1336e07', 16)
log70 = math.log(key_70)
log75 = math.log(key_75)
vals = []
for i in range(5):
    interp = log70 + (log75 - log70) * (i/4)
    v = int(round(math.exp(interp)))
    vals.append(v)
vals[-1] = key_75
with open('pattern/interpolated_keys_71_75.txt','w') as f:
    for v in vals:
        f.write(f'{v:064x}\n') 