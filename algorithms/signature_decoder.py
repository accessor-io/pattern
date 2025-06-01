import hashlib
import binascii

class SignatureDecoder:
    def __init__(self):
        self.signature = "c74ac9b166fd40ea3b30c00193d7e8db4549ce4b14a212a4102df02109a6c870"
        self.chain_code = "563a87145f4e1fe27175889568ff70d7dcae12b18640d2b7dff53881e1a62ff8"
        
    def decode(self):
        print("Signature Analysis")
        print("=" * 50)
        
        # Try using signature as key
        print("\nUsing signature as key:")
        sig_bytes = binascii.unhexlify(self.signature)
        chain_bytes = binascii.unhexlify(self.chain_code)
        
        # XOR the signature with chain code
        xored = bytes(a ^ b for a, b in zip(sig_bytes, chain_bytes))
        print(f"\nXOR result: {binascii.hexlify(xored).decode()}")
        print(f"As ASCII: {xored.decode('ascii', errors='ignore')}")
        
        # Try different offsets
        print("\nTrying different offsets:")
        for i in range(0, len(self.chain_code)-32, 2):
            # Take 32 bytes from chain code
            chain_slice = self.chain_code[i:i+64]
            if len(chain_slice) == 64:  # Only if we have enough bytes
                # XOR with signature
                chain_bytes = binascii.unhexlify(chain_slice)
                xored = bytes(a ^ b for a, b in zip(sig_bytes, chain_bytes))
                try:
                    ascii_str = xored.decode('ascii', errors='ignore')
                    if any(c.isalnum() for c in ascii_str):  # Only print if contains alphanumeric
                        print(f"\nOffset {i//2}:")
                        print(f"ASCII: {ascii_str}")
                except:
                    pass
                    
        # Try using signature as Bitcoin address
        print("\nTrying as Bitcoin address:")
        # Double SHA256
        sha256_1 = hashlib.sha256(sig_bytes).digest()
        sha256_2 = hashlib.sha256(sha256_1).hexdigest()
        print(f"Double SHA256: {sha256_2}")
        
        # Look for this hash in chain code
        if sha256_2 in self.chain_code:
            print(f"Found hash in chain code at position {self.chain_code.index(sha256_2)}")
            
        # Try signature as script
        print("\nAnalyzing as script:")
        script_ops = []
        i = 0
        while i < len(self.signature):
            op = int(self.signature[i:i+2], 16)
            if op <= 0x4e:  # Valid opcode
                script_ops.append(f"OP_{op:02x}")
                i += 2
            else:
                # Try as push data
                script_ops.append(f"PUSH {op}")
                i += 2
                
        print("\nPossible script operations:")
        for op in script_ops:
            print(op)
            
def main():
    decoder = SignatureDecoder()
    decoder.decode()

if __name__ == "__main__":
    main() 