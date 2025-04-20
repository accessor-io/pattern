import hashlib
import binascii

class PatternDecoder:
    def __init__(self):
        self.chain_code = "563a87145f4e1fe27175889568ff70d7dcae12b18640d2b7dff53881e1a62ff8"
        self.master_key = "8bb0fb2ff02bbe28959fb757d33fd316a5d05610f2f45c873ba46ef7ec9dacd0"
        self.pattern = "V:NqqEhp@8/V/+"
        self.positions = {
            'V': 0x56,
            'N': 0x4e,
            'q': 0x71,
            'E': 0x45,
            'h': 0x68,
            'p': 0x70,
            '@': 0x40,
            '8': 0x38,
            '/': 0x2f,
            '+': 0x2b
        }
        
    def follow_pattern(self):
        print("Following Pattern Sequence")
        print("=" * 50)
        
        # Step 1: Convert pattern to positions
        print("\nStep 1 - Pattern Positions:")
        pattern_bytes = []
        for c in self.pattern:
            if c in self.positions:
                pos = self.positions[c]
                pattern_bytes.append(pos)
                print(f"Character {c}: {pos:02x}")
                
        # Step 2: Follow chain code path
        print("\nStep 2 - Chain Code Path:")
        chain_values = []
        current = 0
        for pos in pattern_bytes:
            if current * 2 < len(self.chain_code):
                value = self.chain_code[current*2:current*2+2]
                chain_values.append(value)
                print(f"Position {current:2}: {value}")
                try:
                    current = (current + pos) % (len(self.chain_code)//2)
                except:
                    pass
                    
        # Step 3: Follow master key path
        print("\nStep 3 - Master Key Path:")
        master_values = []
        current = 0
        for pos in pattern_bytes:
            if current * 2 < len(self.master_key):
                value = self.master_key[current*2:current*2+2]
                master_values.append(value)
                print(f"Position {current:2}: {value}")
                try:
                    current = (current + pos) % (len(self.master_key)//2)
                except:
                    pass
                    
        # Step 4: Combine paths
        print("\nStep 4 - Combined Path:")
        if chain_values and master_values:
            # XOR corresponding values
            results = []
            for c, m in zip(chain_values, master_values):
                try:
                    c_val = int(c, 16)
                    m_val = int(m, 16)
                    result = c_val ^ m_val
                    results.append(result)
                    print(f"{c} XOR {m} = {result:02x}")
                except:
                    pass
                    
            # Convert results to bytes
            if results:
                result_bytes = bytes(results)
                print(f"\nResult bytes: {result_bytes.hex()}")
                try:
                    print(f"ASCII: {result_bytes.decode('ascii', errors='ignore')}")
                except:
                    pass
                    
        # Step 5: Follow result path
        print("\nStep 5 - Result Path:")
        if results:
            path = []
            current = results[0]
            for i in range(len(results)):
                pos = current % len(self.chain_code)
                if pos * 2 < len(self.chain_code):
                    value = self.chain_code[pos*2:pos*2+2]
                    path.append(value)
                    print(f"Position {pos:2}: {value}")
                    try:
                        current = int(value, 16)
                    except:
                        break
                        
            # Combine path values
            if path:
                combined = ''.join(path)
                print(f"\nCombined path: {combined}")
                try:
                    path_bytes = bytes.fromhex(combined)
                    print(f"ASCII: {path_bytes.decode('ascii', errors='ignore')}")
                except:
                    pass
                    
        # Step 6: Generate final key
        print("\nStep 6 - Final Key Generation:")
        if results and path:
            # XOR results with path
            final_bytes = bytes([
                results[i] ^ int(path[i % len(path)], 16)
                for i in range(len(results))
            ])
            print(f"Final key: {final_bytes.hex()}")
            try:
                print(f"ASCII: {final_bytes.decode('ascii', errors='ignore')}")
            except:
                pass
                
def main():
    decoder = PatternDecoder()
    decoder.follow_pattern()

if __name__ == "__main__":
    main() 