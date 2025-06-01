import hashlib
import base58

def generate_candidates():
    base = '0000000000000000000000000000000000000000000000002832ed74f2b5e35'
    control_chars = ['0f', '10', '11']
    candidates = []
    for cc in control_chars:
        candidate = base + cc
        candidates.append(candidate.strip())  # Ensure no whitespace
    return candidates

def verify_address(hex_str, target='1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9'):
    hex_str = hex_str.strip()  # Remove any whitespace
    print(f"Verifying candidate length: {len(hex_str)}")
    print(f"Verifying candidate: {hex_str}")
    print(f"Last two characters: {hex_str[-2:]}")
    data = bytes.fromhex(hex_str)
    sha = hashlib.sha256(data).digest()
    ripe = hashlib.new('ripemd160', sha).digest()
    vh160 = b'\x00' + ripe
    checksum = hashlib.sha256(hashlib.sha256(vh160).digest()).digest()[:4]
    final = vh160 + checksum
    address = base58.b58encode(final).decode()
    return address == target

def main():
    candidates = generate_candidates()
    for candidate in candidates:
        if verify_address(candidate):
            print(f"Match found: {candidate}")
            break
    else:
        print("No match found.")

if __name__ == "__main__":
    main()
