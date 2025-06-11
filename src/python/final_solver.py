import hashlib
import binascii

class FinalSolver:
    def __init__(self):
        # Our key findings
        self.chain_code = "563a87145f4e1fe27175889568ff70d7dcae12b18640d2b7dff53881e1a62ff8"
        self.command_sequence = ":Vu"
        self.stack_values = [48, 86, -49]  # From opcode execution
        self.address_hash = "476845e44a6f958e0e5a75bc4e62857af5adc296d7b6fc42d598cce84a21d700"
        self.position_values = {
            0x01: "3a",  # ':'
            0x14: "86",  # 'V'
            0x12: "12",  # 18
            0x10: "dc",
            0x09: "75"   # 'u'
        }
        
    def solve(self):
        print("Final Solution Attempt")
        print("=" * 50)
        
        # Step 1: Use command sequence as key
        print("\nStep 1 - Command Sequence Analysis:")
        cmd_bytes = self.command_sequence.encode('ascii')
        cmd_hash = hashlib.sha256(cmd_bytes).hexdigest()
        print(f"Command: {self.command_sequence}")
        print(f"Command hash: {cmd_hash}")
        
        # Step 2: Combine with stack values
        print("\nStep 2 - Stack Value Integration:")
        stack_bytes = bytes([abs(x) % 256 for x in self.stack_values])
        stack_hash = hashlib.sha256(stack_bytes).hexdigest()
        print(f"Stack values: {self.stack_values}")
        print(f"Stack hash: {stack_hash}")
        
        # Step 3: Use position values as offsets
        print("\nStep 3 - Position Value Analysis:")
        positions = sorted(self.position_values.items())
        offset_sequence = []
        for pos, val in positions:
            try:
                num = int(val, 16)
                offset_sequence.append(num)
                print(f"Position {pos:02x}: {val} -> {num}")
            except:
                pass
                
        # Step 4: Try different combinations
        print("\nStep 4 - Trying Combinations:")
        
        # Combine command with stack
        combined = cmd_bytes + stack_bytes
        print(f"\nCommand + Stack:")
        print(f"Hex: {binascii.hexlify(combined).decode()}")
        print(f"Hash: {hashlib.sha256(combined).hexdigest()}")
        
        # Try position values as key
        pos_bytes = bytes([int(v, 16) for v in self.position_values.values()])
        print(f"\nPosition values as key:")
        print(f"Hex: {binascii.hexlify(pos_bytes).decode()}")
        print(f"Hash: {hashlib.sha256(pos_bytes).hexdigest()}")
        
        # Step 5: Generate potential Bitcoin addresses
        print("\nStep 5 - Generating Bitcoin Addresses:")
        
        # From command sequence
        cmd_addr = hashlib.sha256(hashlib.sha256(cmd_bytes).digest()).hexdigest()
        print(f"\nCommand address: {cmd_addr}")
        
        # From stack values
        stack_addr = hashlib.sha256(hashlib.sha256(stack_bytes).digest()).hexdigest()
        print(f"\nStack address: {stack_addr}")
        
        # From position values
        pos_addr = hashlib.sha256(hashlib.sha256(pos_bytes).digest()).hexdigest()
        print(f"\nPosition address: {pos_addr}")
        
        # Step 6: Look for patterns in chain code
        print("\nStep 6 - Chain Code Pattern Analysis:")
        
        # Break chain code into segments
        segments = [self.chain_code[i:i+8] for i in range(0, len(self.chain_code), 8)]
        print("\nChain code segments:")
        for i, segment in enumerate(segments):
            # Try to decode as ASCII
            try:
                ascii_str = binascii.unhexlify(segment).decode('ascii', errors='ignore')
                print(f"Segment {i}: {segment} -> {ascii_str}")
            except:
                print(f"Segment {i}: {segment}")
                
        # Step 7: Final attempt - combine everything
        print("\nStep 7 - Final Combination Attempt:")
        
        # Combine all our findings
        all_bytes = cmd_bytes + stack_bytes + pos_bytes
        final_hash = hashlib.sha256(all_bytes).hexdigest()
        print(f"\nFinal hash: {final_hash}")
        
        # Compare with our address hash
        print(f"\nComparing with target: {self.address_hash}")
        if final_hash == self.address_hash:
            print("MATCH FOUND!")
        else:
            print("No direct match")
            
        # Try reversing bytes
        reverse_hash = hashlib.sha256(all_bytes[::-1]).hexdigest()
        print(f"\nReverse hash: {reverse_hash}")
        if reverse_hash == self.address_hash:
            print("MATCH FOUND (reversed)!")
            
def main():
    solver = FinalSolver()
    solver.solve()

if __name__ == "__main__":
    main() 