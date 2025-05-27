from ripemd160 import hexdigest

# Test vectors from https://homes.esat.kuleuven.be/~bosselae/ripemd160.html
test_vectors = [
    ("", "9c1185a5c5e9fc54612808977ee8f548b2258d31"),
    ("a", "0bdc9d2d256b3ee9daae347be6f4dc835a467ffe"),
    ("abc", "8eb208f7e05d987a9b044a8e98c6b087f15a0bfc"),
    ("message digest", "5d0689ef49d2fae572b881b123a85ffa21595f36"),
    ("abcdefghijklmnopqrstuvwxyz", "f71c27109c692c1b56bbdceb5b9d2865b3708dbc"),
    ("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq", 
     "12a053384a9c0c88e405a06c27dcf49ada62eb2b"),
    ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
     "b0e20b6e3116640286ed3a87a5713079b21f5189")
]

def test_ripemd160():
    print("Testing RIPEMD160 implementation...")
    for message, expected in test_vectors:
        result = hexdigest(message)
        match = result == expected
        print(f"\nInput: {message}")
        print(f"Expected:  {expected}")
        print(f"Generated: {result}")
        print(f"Match: {match}")

if __name__ == "__main__":
    test_ripemd160() 