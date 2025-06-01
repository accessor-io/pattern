import hashlib
import hmac
import base58
from binascii import hexlify, unhexlify

class HDKeyGenerator:
    def __init__(self):
        # Our master key and chain code from previous analysis
        self.master_key = "0000000000000000000000000000000000000000000000000000000000000001"
        self.chain_code = "563a87145f4e1fe27175889568ff70d7dcae12b18640d2b7dff53881e1a62ff8"
        
    def derive_child_key(self, index, hardened=False):
        if hardened:
            index += 0x80000000  # Add hardened offset
            
        # Convert master key to bytes
        master_bytes = unhexlify(self.master_key)
        chain_bytes = unhexlify(self.chain_code)
        
        # Data to HMAC
        if hardened:
            data = b'\x00' + master_bytes  # Prepend with 0x00 for private derivation
        else:
            # For normal derivation, we'd use the public key, but we'll simplify here
            data = master_bytes
            
        data += index.to_bytes(4, byteorder='big')  # Add index
        
        # Generate child key using HMAC-SHA512
        hmac_bytes = hmac.new(chain_bytes, data, hashlib.sha512).digest()
        
        # Split into child key and new chain code
        child_key = hmac_bytes[:32]
        child_chain = hmac_bytes[32:]
        
        # Add to parent key (simplified - in real implementation, this would use EC math)
        parent_key_int = int.from_bytes(master_bytes, byteorder='big')
        child_key_int = int.from_bytes(child_key, byteorder='big')
        final_key = (parent_key_int + child_key_int) % 2**256
        
        return {
            'key': hexlify(final_key.to_bytes(32, byteorder='big')).decode(),
            'chain_code': hexlify(child_chain).decode()
        }
        
    def generate_address(self, key_hex):
        # Add version byte (0x00 for mainnet)
        version_key = b'\x00' + unhexlify(key_hex)
        
        # Double SHA256 for checksum
        double_sha = hashlib.sha256(hashlib.sha256(version_key).digest()).digest()
        
        # Add checksum
        final_key = version_key + double_sha[:4]
        
        # Convert to base58
        return base58.b58encode(final_key).decode()
        
    def generate_wif(self, key_hex):
        # Add version byte (0x80 for mainnet private key)
        version_key = b'\x80' + unhexlify(key_hex)
        
        # Double SHA256 for checksum
        double_sha = hashlib.sha256(hashlib.sha256(version_key).digest()).digest()
        
        # Add checksum
        final_key = version_key + double_sha[:4]
        
        # Convert to base58
        return base58.b58encode(final_key).decode()
        
    def generate_wallet_batch(self):
        print("Generating HD Wallet Keys")
        print("=" * 50)
        
        # Generate first hardened child
        print("\nm/0' (First Hardened Child):")
        child0h = self.derive_child_key(0, hardened=True)
        print(f"Private Key: {child0h['key']}")
        print(f"WIF: {self.generate_wif(child0h['key'])}")
        print(f"Address: {self.generate_address(child0h['key'])}")
        print(f"Chain Code: {child0h['chain_code']}")
        
        # Generate second hardened child
        print("\nm/1' (Second Hardened Child):")
        child1h = self.derive_child_key(1, hardened=True)
        print(f"Private Key: {child1h['key']}")
        print(f"WIF: {self.generate_wif(child1h['key'])}")
        print(f"Address: {self.generate_address(child1h['key'])}")
        print(f"Chain Code: {child1h['chain_code']}")
        
        # Generate normal children
        print("\nm/0 (First Normal Child):")
        child0 = self.derive_child_key(0, hardened=False)
        print(f"Private Key: {child0['key']}")
        print(f"WIF: {self.generate_wif(child0['key'])}")
        print(f"Address: {self.generate_address(child0['key'])}")
        print(f"Chain Code: {child0['chain_code']}")
        
        # Generate a few more normal children
        for i in range(1, 4):
            print(f"\nm/0/{i} (Normal Child {i}):")
            child = self.derive_child_key(i, hardened=False)
            print(f"Private Key: {child['key']}")
            print(f"WIF: {self.generate_wif(child['key'])}")
            print(f"Address: {self.generate_address(child['key'])}")

def main():
    generator = HDKeyGenerator()
    generator.generate_wallet_batch()

if __name__ == "__main__":
    main() 