import hashlib
import base58
from binascii import hexlify, unhexlify

class BitcoinKeyAnalyzer:
    def __init__(self):
        self.key = "BHJKKXGOMMXCYTV"
        
    def to_wif(self, hex_key):
        """Convert hex private key to WIF format"""
        # Add version byte (0x80 for mainnet)
        extended_key = '80' + hex_key
        
        # Double SHA256
        first_sha = hashlib.sha256(unhexlify(extended_key)).digest()
        second_sha = hashlib.sha256(first_sha).digest()
        
        # Add checksum
        final_key = extended_key + hexlify(second_sha[:4]).decode('ascii')
        
        # Convert to base58
        return base58.b58encode(unhexlify(final_key)).decode('ascii')
        
    def to_address(self, public_key_hex):
        """Convert public key to Bitcoin address"""
        # SHA256
        sha256_hash = hashlib.sha256(unhexlify(public_key_hex)).digest()
        
        # RIPEMD160
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        hash160 = ripemd160.digest()
        
        # Add version byte (0x00 for mainnet)
        version_hash160 = b'\x00' + hash160
        
        # Double SHA256 for checksum
        first_sha = hashlib.sha256(version_hash160).digest()
        second_sha = hashlib.sha256(first_sha).digest()
        
        # Add checksum
        final_addr = version_hash160 + second_sha[:4]
        
        # Convert to base58
        return base58.b58encode(final_addr).decode('ascii')
        
    def analyze_key_formats(self):
        print("\nKey Format Analysis")
        print("=" * 50)
        
        # 1. Original key
        print("\nOriginal Key:", self.key)
        
        # 2. Convert to potential hex formats
        print("\nPotential Hex Formats:")
        
        # Method 1: Direct ASCII to hex
        hex1 = ''.join([hex(ord(c))[2:].zfill(2) for c in self.key])
        print("ASCII Hex:", hex1)
        
        # Method 2: Using key pattern
        numbers = [ord(c) - ord('A') for c in self.key]
        hex2 = ''.join([hex(n)[2:].zfill(2) for n in numbers])
        print("Pattern Hex:", hex2)
        
        # Try both as private keys
        print("\nPotential WIF Keys:")
        try:
            wif1 = self.to_wif(hex1)
            print("WIF 1:", wif1)
        except:
            print("WIF 1: Invalid")
            
        try:
            wif2 = self.to_wif(hex2)
            print("WIF 2:", wif2)
        except:
            print("WIF 2: Invalid")
            
    def analyze_encoded_info(self):
        print("\nEncoded Information Analysis")
        print("=" * 50)
        
        # 1. Group analysis
        groups = [self.key[i:i+3] for i in range(0, len(self.key), 3)]
        print("\nKey Groups:", ' '.join(groups))
        
        # 2. Position analysis
        print("\nPosition-based patterns:")
        print("First chars:", ''.join([g[0] for g in groups]))
        print("Middle chars:", ''.join([g[1] for g in groups if len(g) > 1]))
        print("Last chars:", ''.join([g[2] for g in groups if len(g) > 2]))
        
        # 3. Mathematical patterns
        numbers = [ord(c) - ord('A') for c in self.key]
        diffs = [numbers[i+1] - numbers[i] for i in range(len(numbers)-1)]
        
        print("\nMathematical Patterns:")
        print("Base-26 numbers:", numbers)
        print("Differences:", diffs)
        
        # 4. Look for Bitcoin-specific patterns
        print("\nBitcoin-specific Patterns:")
        
        # Check for Base58 characters
        base58_chars = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
        valid_base58 = all(c in base58_chars for c in self.key)
        print("Valid Base58:", valid_base58)
        
        # Check for potential address patterns
        if self.key.startswith('B'):
            print("Starts with 'B': Potential BIP format")
            
        # 5. Try different encodings
        print("\nAlternative Encodings:")
        
        # Base58 decode attempt
        try:
            b58_decoded = base58.b58decode(self.key).hex()
            print("Base58 decoded:", b58_decoded)
        except:
            print("Base58 decoded: Invalid")
            
        # Base32 decode attempt
        try:
            b32_decoded = base64.b32decode(self.key).hex()
            print("Base32 decoded:", b32_decoded)
        except:
            print("Base32 decoded: Invalid")
            
    def find_hidden_sequences(self):
        print("\nHidden Sequence Analysis")
        print("=" * 50)
        
        # 1. Look for Fibonacci-like sequences
        print("\nFibonacci-like Patterns:")
        numbers = [ord(c) - ord('A') for c in self.key]
        
        for i in range(len(numbers)-2):
            if abs(numbers[i] + numbers[i+1] - numbers[i+2]) <= 1:
                print(f"Found at position {i}: {numbers[i]}, {numbers[i+1]}, {numbers[i+2]}")
                
        # 2. Look for repeating subsequences
        print("\nRepeating Subsequences:")
        for length in range(2, 6):
            seen = set()
            for i in range(len(self.key)-length+1):
                substr = self.key[i:i+length]
                if substr in seen:
                    print(f"Found repeating {length}-sequence: {substr}")
                seen.add(substr)
                
        # 3. Check for potential key derivation paths
        print("\nPotential Derivation Paths:")
        segments = [self.key[i:i+4] for i in range(0, len(self.key), 4)]
        for i, seg in enumerate(segments):
            print(f"m/{i}'/{sum(ord(c) for c in seg)}'")

def main():
    analyzer = BitcoinKeyAnalyzer()
    
    print("Bitcoin Key Analysis")
    print("=" * 50)
    
    analyzer.analyze_key_formats()
    analyzer.analyze_encoded_info()
    analyzer.find_hidden_sequences()

if __name__ == "__main__":
    main() 