import hashlib
import binascii

class FinalPathExecutor:
    def __init__(self):
        self.chain_code = "563a87145f4e1fe27175889568ff70d7dcae12b18640d2b7dff53881e1a62ff8"
        self.start_pos = 56
        self.key = "8bb0fb2ff02bbe28959fb757d33fd316a5d05610f2f45c873ba46ef7ec9dacd0"
        
    def execute(self):
        print("Final Path Execution")
        print("=" * 50)
        
        # Step 1: Get value at start position
        print("\nStep 1 - Starting Position Analysis:")
        if self.start_pos * 2 < len(self.chain_code):
            start_value = self.chain_code[self.start_pos*2:self.start_pos*2+2]
            print(f"Value at position {self.start_pos}: {start_value}")
            try:
                as_num = int(start_value, 16)
                print(f"As number: {as_num}")
                if as_num <= 0x4e:
                    print(f"Valid opcode: OP_{as_num:02x}")
            except:
                pass
                
        # Step 2: Follow value chain
        print("\nStep 2 - Following Value Chain:")
        chain = []
        current = self.start_pos
        
        # Follow for 16 steps or until we loop
        for i in range(16):
            if current * 2 < len(self.chain_code):
                value = self.chain_code[current*2:current*2+2]
                chain.append(value)
                print(f"Position {current}: {value}")
                try:
                    current = int(value, 16)
                except:
                    break
                    
        # Step 3: Try to decode chain
        print("\nStep 3 - Chain Analysis:")
        if chain:
            # Combine all values
            combined = ''.join(chain)
            print(f"Combined chain: {combined}")
            
            # Try as ASCII
            try:
                chain_bytes = bytes.fromhex(combined)
                ascii_str = chain_bytes.decode('ascii', errors='ignore')
                print(f"As ASCII: {ascii_str}")
            except:
                pass
                
            # Try as address
            try:
                addr_bytes = bytes.fromhex(combined[:40])  # Take first 20 bytes
                addr_hash = hashlib.sha256(addr_bytes).hexdigest()
                print(f"As address: {addr_hash}")
            except:
                pass
                
        # Step 4: XOR with key
        print("\nStep 4 - Key Combination:")
        try:
            # Take matching length from key
            key_part = bytes.fromhex(self.key[:len(combined)])
            chain_bytes = bytes.fromhex(combined)
            
            # XOR matching parts
            result = bytes(a ^ b for a, b in zip(chain_bytes, key_part))
            print(f"XOR result: {result.hex()}")
            
            # Try to decode
            try:
                decoded = result.decode('ascii', errors='ignore')
                print(f"Decoded: {decoded}")
            except:
                pass
        except:
            pass
            
        # Step 5: Try reversing the path
        print("\nStep 5 - Reverse Path Analysis:")
        reverse_chain = []
        current = int(chain[-1], 16) if chain else 0
        
        for i in range(8):
            if current * 2 < len(self.chain_code):
                value = self.chain_code[current*2:current*2+2]
                reverse_chain.append(value)
                print(f"Position {current}: {value}")
                try:
                    current = int(value, 16)
                except:
                    break
                    
        # Try to decode reverse chain
        if reverse_chain:
            combined = ''.join(reverse_chain)
            print(f"\nReverse chain: {combined}")
            try:
                rev_bytes = bytes.fromhex(combined)
                print(f"As ASCII: {rev_bytes.decode('ascii', errors='ignore')}")
            except:
                pass
                
def main():
    executor = FinalPathExecutor()
    executor.execute()

if __name__ == "__main__":
    main() 