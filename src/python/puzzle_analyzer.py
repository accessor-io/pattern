import hashlib
import binascii

class PuzzleAnalyzer:
    def __init__(self):
        self.chain_code = "563a87145f4e1fe27175889568ff70d7dcae12b18640d2b7dff53881e1a62ff8"
        self.master_key = "73fc74d3cc995ae3f81703688d7409bb38d26f167bbc47aa82bc89592db41422"
        
    def analyze_as_ascii(self):
        print("ASCII Analysis")
        print("=" * 50)
        
        # Try to decode hex to ASCII
        try:
            chain_ascii = binascii.unhexlify(self.chain_code).decode('ascii', errors='ignore')
            master_ascii = binascii.unhexlify(self.master_key).decode('ascii', errors='ignore')
            print(f"Chain Code as ASCII: {chain_ascii}")
            print(f"Master Key as ASCII: {master_ascii}")
        except:
            print("Could not decode as ASCII")
            
    def analyze_as_numbers(self):
        print("\nNumerical Analysis")
        print("=" * 50)
        
        # Break into 4-byte chunks
        chain_chunks = [self.chain_code[i:i+8] for i in range(0, len(self.chain_code), 8)]
        master_chunks = [self.master_key[i:i+8] for i in range(0, len(self.master_key), 8)]
        
        print("Chain Code 4-byte chunks:")
        for i, chunk in enumerate(chain_chunks):
            value = int(chunk, 16)
            print(f"Chunk {i+1}: {chunk} = {value} (decimal)")
            
        print("\nMaster Key 4-byte chunks:")
        for i, chunk in enumerate(master_chunks):
            value = int(chunk, 16)
            print(f"Chunk {i+1}: {chunk} = {value} (decimal)")
            
    def analyze_as_bitcoin_data(self):
        print("\nBitcoin Data Analysis")
        print("=" * 50)
        
        # Try different Bitcoin-related interpretations
        chain_sha = hashlib.sha256(binascii.unhexlify(self.chain_code)).hexdigest()
        master_sha = hashlib.sha256(binascii.unhexlify(self.master_key)).hexdigest()
        
        print(f"Chain Code SHA256: {chain_sha}")
        print(f"Master Key SHA256: {master_sha}")
        
        # Look for potential Bitcoin script opcodes
        print("\nPotential Script Opcodes:")
        for i in range(0, len(self.chain_code), 2):
            opcode = int(self.chain_code[i:i+2], 16)
            if opcode <= 0x4e:  # Standard Bitcoin script opcodes
                print(f"Position {i//2}: {opcode:02x} might be opcode")
                
    def analyze_patterns(self):
        print("\nPattern Analysis")
        print("=" * 50)
        
        # Look for repeating patterns
        def find_repeats(data):
            patterns = {}
            for length in range(2, 9):  # Look for patterns of length 2-8
                for i in range(len(data)-length):
                    pattern = data[i:i+length]
                    if data.count(pattern) > 1:
                        patterns[pattern] = data.count(pattern)
            return patterns
            
        chain_patterns = find_repeats(self.chain_code)
        master_patterns = find_repeats(self.master_key)
        
        print("Repeating patterns in Chain Code:")
        for pattern, count in chain_patterns.items():
            print(f"Pattern {pattern} appears {count} times")
            
        print("\nRepeating patterns in Master Key:")
        for pattern, count in master_patterns.items():
            print(f"Pattern {pattern} appears {count} times")
            
    def analyze_combined(self):
        print("\nCombined Analysis")
        print("=" * 50)
        
        # XOR the two values
        chain_bytes = binascii.unhexlify(self.chain_code)
        master_bytes = binascii.unhexlify(self.master_key)
        xored = bytes(a ^ b for a, b in zip(chain_bytes, master_bytes))
        
        print(f"XOR result: {binascii.hexlify(xored).decode()}")
        print(f"XOR as ASCII: {xored.decode('ascii', errors='ignore')}")
        
        # Try adding them as numbers
        chain_num = int(self.chain_code, 16)
        master_num = int(self.master_key, 16)
        added = chain_num + master_num
        
        print(f"\nSum as hex: {hex(added)[2:]}")
        
def main():
    analyzer = PuzzleAnalyzer()
    analyzer.analyze_as_ascii()
    analyzer.analyze_as_numbers()
    analyzer.analyze_as_bitcoin_data()
    analyzer.analyze_patterns()
    analyzer.analyze_combined()

if __name__ == "__main__":
    main() 