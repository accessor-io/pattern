from ecdsa import SECP256k1, SigningKey

def validate_term(hex_value):
    try:
        key_int = int(hex_value, 16)
        return 1 <= key_int < SECP256k1.order
    except:
        return False

def verify_solutions(file_path):
    with open(file_path) as f:
        for line in f:
            if line.startswith('term'):
                term, hex_val = line.split(':')
                hex_val = hex_val.strip().lstrip('0x')
                print(f"{term}: {'Valid' if validate_term(hex_val) else 'Invalid'}")

if __name__ == "__main__":
    import sys
    verify_solutions(sys.argv[1])
