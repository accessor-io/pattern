import hashlib
import binascii

class SequenceDecoder:
    def __init__(self):
        self.chain_code = "563a87145f4e1fe27175889568ff70d7dcae12b18640d2b7dff53881e1a62ff8"
        self.master_key = "8bb0fb2ff02bbe28959fb757d33fd316a5d05610f2f45c873ba46ef7ec9dacd0"
        self.command_sequence = [
            ("V:", "Verify", 0x56),
            ("_N", "Next", 0x4e),
            ("qu", "Query", 0x71),
            ("hp", "Helper", 0x68),
            ("@", "Address", 0x40),
            ("8", "Value", 0x38),
            ("/", "Path", 0x2f)
        ]
        
    def decode_sequence(self):
        print("Decoding Command Sequence")
        print("=" * 50)
        
        # Step 1: Generate sequence key
        print("\nStep 1 - Sequence Key Generation:")
        sequence_bytes = bytes([op for _, _, op in self.command_sequence])
        print(f"Sequence bytes: {sequence_bytes.hex()}")
        
        # Step 2: Map sequence to chain code
        print("\nStep 2 - Chain Code Mapping:")
        chain_segments = []
        for cmd, name, op in self.command_sequence:
            hex_op = f"{op:02x}"
            pos = self.chain_code.find(hex_op)
            if pos >= 0:
                segment = self.chain_code[pos:pos+8]
                chain_segments.append(segment)
                print(f"{name:8}: {segment}")
                
        # Step 3: Map sequence to master key
        print("\nStep 3 - Master Key Mapping:")
        master_segments = []
        for cmd, name, op in self.command_sequence:
            hex_op = f"{op:02x}"
            pos = self.master_key.find(hex_op)
            if pos >= 0:
                segment = self.master_key[pos:pos+8]
                master_segments.append(segment)
                print(f"{name:8}: {segment}")
                
        # Step 4: Generate verification path
        print("\nStep 4 - Verification Path:")
        path = []
        current = 0
        for cmd, name, op in self.command_sequence:
            path.append(op)
            print(f"{name:8}: {op:02x}")
            # Get next position
            if current * 2 < len(self.chain_code):
                next_val = self.chain_code[current*2:current*2+2]
                try:
                    current = int(next_val, 16)
                    print(f"Next pos: {current}")
                except:
                    pass
                    
        # Step 5: Follow verification path
        print("\nStep 5 - Following Path:")
        path_values = []
        current = 0
        for step in path:
            pos = (current + step) % len(self.chain_code)
            if pos * 2 < len(self.chain_code):
                value = self.chain_code[pos*2:pos*2+2]
                path_values.append(value)
                print(f"Position {pos:2}: {value}")
                try:
                    current = int(value, 16)
                except:
                    pass
                    
        # Step 6: Combine all segments
        print("\nStep 6 - Combining Segments:")
        all_segments = chain_segments + master_segments + path_values
        if all_segments:
            combined = ''.join(all_segments)
            print(f"Combined: {combined}")
            
            # Try to decode
            try:
                bytes_val = bytes.fromhex(combined)
                ascii_str = bytes_val.decode('ascii', errors='ignore')
                print(f"ASCII: {ascii_str}")
            except:
                pass
                
        # Step 7: Generate final key
        print("\nStep 7 - Final Key Generation:")
        if path_values:
            # XOR all path values
            path_bytes = bytes([int(v, 16) for v in path_values])
            # XOR with sequence
            if len(path_bytes) >= len(sequence_bytes):
                result = bytes(a ^ b for a, b in zip(path_bytes, sequence_bytes))
                print(f"Final key: {result.hex()}")
                try:
                    print(f"ASCII: {result.decode('ascii', errors='ignore')}")
                except:
                    pass
                    
def main():
    decoder = SequenceDecoder()
    decoder.decode_sequence()

if __name__ == "__main__":
    main() 