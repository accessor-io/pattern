import hashlib
import hmac
from binascii import hexlify, unhexlify

def analyze_chain_code():
    # Our chain code from the previous generation
    chain_code = "563a87145f4e1fe27175889568ff70d7dcae12b18640d2b7dff53881e1a62ff8"
    
    print("Chain Code Analysis")
    print("=" * 50)
    
    # Break down the chain code
    print("\nChain Code:", chain_code)
    print(f"Length: {len(chain_code)} hex characters = {len(chain_code) // 2} bytes")
    
    # Convert to bytes
    chain_bytes = unhexlify(chain_code)
    
    # Show as binary
    binary = ''.join(format(b, '08b') for b in chain_bytes)
    print(f"\nBinary (first 32 bits): {binary[:32]} ...")
    
    # Break into 4-byte segments
    segments = [chain_code[i:i+8] for i in range(0, len(chain_code), 8)]
    print("\nSegments (4-byte chunks):")
    for i, seg in enumerate(segments):
        print(f"Segment {i + 1}: {seg}")
        
    # Explain chain code purpose
    print("\nChain Code Purpose:")
    purposes = [
        "Used to derive child keys in HD wallets",
        "Provides randomness for key derivation",
        "Ensures child keys are unique",
        "Enables hierarchical wallet structure"
    ]
    for i, purpose in enumerate(purposes, 1):
        print(f"{i}. {purpose}")
    
    # Demonstrate child key derivation
    print("\nChild Key Derivation Example:")
    
    # Example index for child key
    index = 0  # First child
    
    # Convert index to bytes (4 bytes, big-endian)
    index_bytes = index.to_bytes(4, byteorder='big')
    
    # Example public key (just for demonstration)
    example_pub_key = b'0' * 32
    
    # Combine data for child key derivation
    data = example_pub_key + index_bytes
    
    # Use chain code as HMAC key
    child = hmac.new(chain_bytes, data, hashlib.sha512).digest()
    
    print(f"Child Key (first 32 bytes): {hexlify(child[:32]).decode()}")
    print(f"Child Chain Code (last 32 bytes): {hexlify(child[32:]).decode()}")
    
    # Show derivation path possibilities
    print("\nPossible Derivation Paths:")
    derivation_paths = [
        "m/0' - First hardened child",
        "m/1' - Second hardened child",
        "m/0'/0 - First normal child of first hardened child",
        "m/0'/0/0 - First normal child of first normal child of first hardened child"
    ]
    for path in derivation_paths:
        print(path)

def main():
    analyze_chain_code()

if __name__ == "__main__":
    main() 