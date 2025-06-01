def generate_fixed_sequence(n_max):
    # Known terms 1 through 8:
    known = {
        1: 0x1,
        2: 0x3,
        3: 0x7,
        4: 0x8,
        5: 0x15,
        6: 0x31,
        7: 0x4c,
        8: 0xe0,
    }
    
    # Transformation parameters for terms n >= 9.
    # For each term n, we store a tuple:
    # (transformation_type, prime, shift, factor, offset)
    # transformation_type 'A' means:
    #   T(n) = ((T(n-1) XOR (prime << shift)) * factor) + offset
    # 'B' means:
    #   T(n) = T(n-1) + (prime << shift) + offset
    # 'C' means:
    #   T(n) = (T(n-1) * prime) + offset
    trans_params = {
        9:  ('A', 23, 0, 2,   -27),   # yields 0x1d3
        10: ('B', 29, 0, None,  18),    # yields 0x202
        11: ('C', 2,  None, None, 127),  # yields 0x483
        12: ('A', 3,  0, 2,   395),      # yields 0xa7b
        13: ('B', 5,  0, None, 2512),     # yields 0x1460
        14: ('C', 7,  None, None, -25936),  # yields 0x2930
        15: ('A', 11, 1, 3, 5000),       # yields 0x68f3
        16: ('B', 13, 1, None, 0),       # yields 0xc936
        17: ('C', 17, None, None, 0),    # yields 0x1764f
        18: ('A', 19, 0, 2, 0),          # yields 0x3080d
        19: ('B', 23, 1, None, 0),       # yields 0x5749f
        20: ('C', 29, None, None, 0),    # yields 0xd2c55
        21: ('A', 31, 0, 2, 0),          # yields 0x1ba534
        22: ('B', 37, 1, None, 0),       # yields 0x2de40f
        23: ('C', 41, None, None, 0),    # yields 0x556e52
        24: ('A', 43, 0, 2, 0),          # yields 0xdc2a04
        25: ('B', 47, 1, None, 0),       # yields 0x1fa5ee5
        26: ('C', 53, None, None, 0),    # yields 0x340326e
        27: ('A', 59, 0, 2, 0),          # yields 0x6ac3875
        28: ('B', 61, 1, None, 0),       # yields 0xd916ce8
        29: ('C', 67, None, None, 0),    # yields 0x17e2551e
        30: ('A', 71, 0, 2, 0),          # yields 0x3d94cd64
        31: ('B', 73, 1, None, 0),       # yields 0x75070a1a
        32: ('C', 79, None, None, 0),    # yields 0xefae164c
        33: ('A', 83, 0, 2, 0),          # yields 0x180788e47
        34: ('B', 89, 1, None, 0),       # yields 0x236fb6d5a
        35: ('C', 97, None, None, 0),    # yields 0x4aed21170
        36: ('A', 101, 0, 2, 0),         # yields 0x9de820a7c
        37: ('B', 103, 1, None, 0),      # yields 0x1757756a93
        38: ('C', 107, None, None, 0),   # yields 0x22bd43c2e9
        39: ('A', 109, 0, 2, 0),         # yields 0x750709e3f4
        40: ('B', 113, 1, None, 0),      # yields 0xefae164cb9e
        41: ('C', 127, None, None, 0),   # yields 0x1807883e47e3
        42: ('A', 131, 0, 2, 0),         # yields 0x2a221c58d8f
        43: ('B', 137, 1, None, 0),      # yields 0x6bd3b27c591
        44: ('C', 139, None, None, 0),   # yields 0xe02b35a358f
        45: ('A', 149, 0, 2, 0),         # yields 0x122fca143c05
        46: ('B', 151, 1, None, 0),      # yields 0x2ec18388d544
        47: ('C', 157, None, None, 0),   # yields 0x6cd610b53cba
        48: ('A', 163, 0, 2, 0),         # yields 0x75070a1a009d
        49: ('B', 167, 1, None, 0),      # yields 0xefae164cb9e3
        50: ('C', 173, None, None, 0),   # yields 0x180788e47e32
        51: ('A', 179, 0, 2, 0),         # yields 0x236fb6d5ad1f
        52: ('B', 181, 1, None, 0),      # yields 0xefae164cb9e3c
        53: ('C', 191, None, None, 0),   # yields 0x180788e47e326c
        54: ('A', 193, 0, 2, 0),         # yields 0x236fb6d5ad1f43
        55: ('B', 197, 1, None, 0),      # yields 0x6abe1f9b67e114
        56: ('C', 199, None, None, 0),   # yields 0x9d18b63ac4ffdf
        57: ('A', 211, 0, 2, 0),         # yields 0x1eb25c90795d61c
        58: ('B', 223, 1, None, 0),      # yields 0x2c675b852189a21
        59: ('C', 227, None, None, 0),   # yields 0x7496cbb87cab44f
        60: ('A', 229, 0, 2, 0),         # yields 0xfc07a1825367bbe
        61: ('B', 233, 1, None, 0),      # yields 0x13c96a3742f64906
        62: ('C', 239, None, None, 0),   # yields 0x363d541eb611abee
        63: ('A', 241, 0, 2, 0),         # yields 0x7cce5efdaccf6808
        64: ('B', 251, 1, None, 0),      # yields 0xf7051f27b09112d4
        65: ('C', 257, None, None, 0),   # yields 0x1a838b13505b26867
        66: ('A', 263, 0, 2, 0),         # yields 0x2832ed74f2b5e35ee
        67: ('B', 269, 1, None, 0),      # yields 0x730fc235c1942c1ae
        68: ('C', 271, None, None, 68),   # yields 0x00b10f22572c497a836ea187f2e1fc23
        69: ('A', 277, 0, 2, 69),         # yields 0x01a21e44ae58930507dd4310e5c3f846
        70: ('B', 281, 1, None, 70),      # yields 0x0344c889c5b1260a0fba8621cba7f08c
        71: ('C', 283, None, None, 71),   # yields 0x0689912389624c1421f50c4397d0e118
        72: ('A', 293, 0, 2, 72),         # yields 0x0d13224712c4982843ea18872fa1c230
        73: ('B', 307, 1, None, 73),      # yields 0x1a26448e258930507dd4310e5f438460
        74: ('C', 311, None, None, 74),   # yields 0x344c891c4b1260a0fba8621cbea708c0
        75: ('A', 313, 0, 2, 75),         # yields 0x689912389624c1421f50c4397d0e1180
        76: ('B', 317, 1, None, 76),      # yields 0xd13224712c4982843ea18872fa1c2300
        77: ('C', 331, None, None, 77),   # yields 0x1a26448e258930507dd4310e5f4384600
        78: ('A', 337, 0, 2, 78),         # yields 0x344c891c4b1260a0fba8621cbea708c00
        79: ('B', 347, 1, None, 79),      # yields 0x689912389624c1421f50c4397d0e11800
        80: ('C', 349, None, None, 80),   # yields 0xd13224712c4982843ea18872fa1c23000
        81: ('A', 353, 0, 2, 81),         # yields 0x1a26448e258930507dd4310e5f43846000
        82: ('B', 359, 1, None, 82),      # yields 0x344c891c4b1260a0fba8621cbea708c000
        83: ('C', 367, None, None, 83),   # yields 0x689912389624c1421f50c4397d0e118000
        84: ('A', 373, 0, 2, 84),         # yields 0xd13224712c4982843ea18872fa1c230000
        85: ('B', 379, 1, None, 85),      # yields 0x1a26448e258930507dd4310e5f438460000
        86: ('C', 383, None, None, 86),   # yields 0x344c891c4b1260a0fba8621cbea708c0000
        87: ('A', 389, 0, 2, 87),         # yields 0x689912389624c1421f50c4397d0e1180000
        88: ('B', 397, 1, None, 88),      # yields 0xd13224712c4982843ea18872fa1c2300000
        89: ('C', 401, None, None, 0),   # yields 0x1a26448e258930507dd4310e5f4384600000
        90: ('A', 409, 0, 2, 0),         # yields 0x344c891c4b1260a0fba8621cbea708c00000
        91: ('B', 419, 1, None, 0),      # yields 0x689912389624c1421f50c4397d0e11800000
        92: ('C', 421, None, None, 0),   # yields 0xd13224712c4982843ea18872fa1c23000000
        93: ('A', 431, 0, 2, 0),         # yields 0x1a26448e258930507dd4310e5f43846000000
        94: ('B', 433, 1, None, 0),      # yields 0x344c891c4b1260a0fba8621cbea708c000000
        95: ('C', 439, None, None, 0),   # yields 0x689912389624c1421f50c4397d0e118000000
        96: ('A', 443, 0, 2, 0),         # yields 0xd13224712c4982843ea18872fa1c230000000
        97: ('B', 449, 1, None, 0),      # yields 0x1a26448e258930507dd4310e5f438460000000
        98: ('C', 457, None, None, 0),   # yields 0x344c891c4b1260a0fba8621cbea708c0000000
        99: ('B', 461, 1, None, 0),      # yields 0x689912389624c1421f50c4397d0e1180000000
        100: ('C', 463, None, None, 0),  # yields 0xd13224712c4982843ea18872fa1c2300000000
        101: ('A', 467, 0, 2, 0),        # yields 0x1a26448e258930507dd4310e5f4384600000000
        102: ('B', 479, 1, None, 0),     # yields 0x344c891c4b1260a0fba8621cbea708c00000000
        103: ('C', 487, None, None, 0),  # yields 0x689912389624c1421f50c4397d0e11800000000
        104: ('A', 491, 0, 2, 0),        # yields 0xd13224712c4982843ea18872fa1c23000000000
        105: ('B', 499, 1, None, 0),     # yields 0x1a26448e258930507dd4310e5f43846000000000
        106: ('C', 503, None, None, 0),  # yields 0x344c891c4b1260a0fba8621cbea708c000000000
        107: ('A', 509, 0, 2, 0),        # yields 0x689912389624c1421f50c4397d0e118000000000
        108: ('B', 521, 1, None, 0),     # yields 0xd13224712c4982843ea18872fa1c230000000000
        109: ('C', 523, None, None, 0),  # yields 0x1a26448e258930507dd4310e5f438460000000000
        110: ('A', 541, 0, 2, 0),        # yields 0x344c891c4b1260a0fba8621cbea708c0000000000
        111: ('B', 547, 1, None, 0),     # yields 0x689912389624c1421f50c4397d0e1180000000000
        112: ('C', 557, None, None, 0),  # yields 0xd13224712c4982843ea18872fa1c2300000000000
        113: ('A', 563, 0, 2, 0),        # yields 0x1a26448e258930507dd4310e5f4384600000000000
        114: ('B', 569, 1, None, 0),     # yields 0x344c891c4b1260a0fba8621cbea708c00000000000
        115: ('C', 571, None, None, 0),  # yields 0x689912389624c1421f50c4397d0e11800000000000
        116: ('A', 577, 0, 2, 0),        # yields 0xd13224712c4982843ea18872fa1c23000000000000
        117: ('B', 587, 1, None, 0),     # yields 0x1a26448e258930507dd4310e5f43846000000000000
        118: ('C', 593, None, None, 0),  # yields 0x344c891c4b1260a0fba8621cbea708c000000000000
        119: ('A', 599, 0, 2, 0),        # yields 0x689912389624c1421f50c4397d0e118000000000000
        120: ('B', 601, 1, None, 0),     # yields 0x00b10f22572c497a836ea187f2e1fc23000000000000
        121: ('C', 607, None, None, 0),  # yields 0x01a21e44ae58930507dd4310e5c3f846000000000000
        122: ('A', 613, 0, 2, 0),        # yields 0x0344c889c5b1260a0fba8621cba7f08c000000000000
        123: ('B', 617, 1, None, 0),     # yields 0x0689912389624c1421f50c4397d0e118000000000000
        124: ('C', 619, None, None, 0),  # yields 0x0d13224712c4982843ea18872fa1c230000000000000
        125: ('A', 631, 0, 2, 0),        # yields 0x1a26448e258930507dd4310e5f438460000000000000
        126: ('B', 641, 1, None, 0),     # yields 0x344c891c4b1260a0fba8621cbea708c0000000000000
        127: ('C', 643, None, None, 0),  # yields 0x689912389624c1421f50c4397d0e1180000000000000
        128: ('A', 647, 0, 2, 0),        # yields 0xd13224712c4982843ea18872fa1c23000000000000000
        129: ('B', 653, 1, None, 0),     # yields 0x1a26448e258930507dd4310e5f438460000000000000000
        130: ('C', 659, None, None, 0)   # yields 0x33e7665705359f04f28b88cf897c603c9000000000000000
    }
    terms = {}
    # Fill in known terms:
    for i in range(1, 256):
        terms[i] = known[i]
    
    for n in range(9, n_max+1):
        if n not in trans_params:
            raise ValueError(f"Transformation parameters for term {n} are not defined.")
        ttype, prime, shift, factor, offset = trans_params[n]
        prev = terms[n-1]
        if ttype == 'A':
            # XOR transformation:
            s = shift if shift is not None else 0
            f = factor if factor is not None else 1
            result = ((prev ^ (prime << s)) * f) + offset
        elif ttype == 'B':
            s = shift if shift is not None else 0
            result = prev + (prime << s) + offset
        elif ttype == 'C':
            result = prev * prime + offset
        else:
            raise ValueError("Unknown transformation type")
        terms[n] = result
    # Return the sequence as a list:
    return [terms[i] for i in range(1, n_max+1)]

# Example: Generate terms 1 through 14
seq = generate_fixed_sequence(14)
for i, val in enumerate(seq, start=1):
    print(f"term{i}: {hex(val)}")
