import hashlib
import binascii

class DeepPatternAnalyzer:
    def __init__(self):
        self.chain_code = "563a87145f4e1fe27175889568ff70d7dcae12b18640d2b7dff53881e1a62ff8"
        self.master_key = "8bb0fb2ff02bbe28959fb757d33fd316a5d05610f2f45c873ba46ef7ec9dacd0"
        self.segments = [
            (0, 8),   # First 8 chars
            (8, 16),  # Next 8 chars
            (16, 24), # And so on...
            (24, 32),
            (32, 40),
            (40, 48),
            (48, 56),
            (56, 64)
        ]
        
    def analyze_patterns(self):
        print("Deep Pattern Analysis")
        print("=" * 50)
        
        # Step 1: Analyze chain code segments
        print("\nStep 1 - Chain Code Segments:")
        chain_parts = []
        for i, (start, end) in enumerate(self.segments):
            segment = self.chain_code[start:end]
            chain_parts.append(segment)
            print(f"Segment {i}: {segment}")
            # Try to decode
            try:
                bytes_val = bytes.fromhex(segment)
                ascii_str = bytes_val.decode('ascii', errors='ignore')
                if ascii_str:
                    print(f"ASCII: {ascii_str}")
            except:
                pass
                
        # Step 2: Analyze master key segments
        print("\nStep 2 - Master Key Segments:")
        master_parts = []
        for i, (start, end) in enumerate(self.segments):
            segment = self.master_key[start:end]
            master_parts.append(segment)
            print(f"Segment {i}: {segment}")
            # Try to decode
            try:
                bytes_val = bytes.fromhex(segment)
                ascii_str = bytes_val.decode('ascii', errors='ignore')
                if ascii_str:
                    print(f"ASCII: {ascii_str}")
            except:
                pass
                
        # Step 3: XOR corresponding segments
        print("\nStep 3 - XOR Analysis:")
        xor_results = []
        for c, m in zip(chain_parts, master_parts):
            try:
                c_bytes = bytes.fromhex(c)
                m_bytes = bytes.fromhex(m)
                result = bytes(a ^ b for a, b in zip(c_bytes, m_bytes))
                xor_results.append(result)
                print(f"{c} XOR {m} = {result.hex()}")
                # Try to decode
                ascii_str = result.decode('ascii', errors='ignore')
                if ascii_str:
                    print(f"ASCII: {ascii_str}")
            except:
                pass
                
        # Step 4: Look for repeating patterns
        print("\nStep 4 - Pattern Search:")
        for length in range(2, 9):  # Look for patterns of length 2-8
            print(f"\nPatterns of length {length}:")
            # In chain code
            for i in range(len(self.chain_code) - length + 1):
                pattern = self.chain_code[i:i+length]
                count = self.chain_code.count(pattern)
                if count > 1:
                    print(f"Chain pattern {pattern} appears {count} times")
                    
            # In master key
            for i in range(len(self.master_key) - length + 1):
                pattern = self.master_key[i:i+length]
                count = self.master_key.count(pattern)
                if count > 1:
                    print(f"Master pattern {pattern} appears {count} times")
                    
        # Step 5: Analyze byte distribution
        print("\nStep 5 - Byte Distribution:")
        # Chain code bytes
        chain_bytes = {}
        for i in range(0, len(self.chain_code), 2):
            byte = self.chain_code[i:i+2]
            chain_bytes[byte] = chain_bytes.get(byte, 0) + 1
        print("\nChain code byte frequency:")
        for byte, count in sorted(chain_bytes.items(), key=lambda x: x[1], reverse=True):
            if count > 1:
                print(f"Byte {byte} appears {count} times")
                
        # Master key bytes
        master_bytes = {}
        for i in range(0, len(self.master_key), 2):
            byte = self.master_key[i:i+2]
            master_bytes[byte] = master_bytes.get(byte, 0) + 1
        print("\nMaster key byte frequency:")
        for byte, count in sorted(master_bytes.items(), key=lambda x: x[1], reverse=True):
            if count > 1:
                print(f"Byte {byte} appears {count} times")
                
        # Step 6: Look for mathematical relationships
        print("\nStep 6 - Mathematical Analysis:")
        chain_nums = []
        master_nums = []
        
        # Convert segments to numbers
        for c, m in zip(chain_parts, master_parts):
            try:
                c_num = int(c, 16)
                m_num = int(m, 16)
                chain_nums.append(c_num)
                master_nums.append(m_num)
            except:
                pass
                
        # Look for relationships
        if chain_nums and master_nums:
            print("\nNumber relationships:")
            for i in range(len(chain_nums)):
                c = chain_nums[i]
                m = master_nums[i]
                print(f"\nSegment {i}:")
                print(f"Chain: {c}")
                print(f"Master: {m}")
                print(f"Sum: {c + m}")
                print(f"Difference: {c - m}")
                print(f"Product: {c * m}")
                if m != 0:
                    print(f"Division: {c / m}")
                    
        # Step 7: Generate potential keys
        print("\nStep 7 - Key Generation:")
        # Try different combinations of segments
        for i in range(len(chain_parts)):
            for j in range(i+1, len(chain_parts)+1):
                chain_combo = ''.join(chain_parts[i:j])
                master_combo = ''.join(master_parts[i:j])
                print(f"\nSegments {i}-{j}:")
                print(f"Chain: {chain_combo}")
                print(f"Master: {master_combo}")
                try:
                    # XOR the combinations
                    c_bytes = bytes.fromhex(chain_combo)
                    m_bytes = bytes.fromhex(master_combo)
                    result = bytes(a ^ b for a, b in zip(c_bytes, m_bytes))
                    print(f"XOR: {result.hex()}")
                    # Try to decode
                    ascii_str = result.decode('ascii', errors='ignore')
                    if ascii_str:
                        print(f"ASCII: {ascii_str}")
                except:
                    pass
                    
def main():
    analyzer = DeepPatternAnalyzer()
    analyzer.analyze_patterns()

if __name__ == "__main__":
    main() 