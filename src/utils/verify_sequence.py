import hashlib
import binascii

class VerificationExecutor:
    def __init__(self):
        self.chain_code = "563a87145f4e1fe27175889568ff70d7dcae12b18640d2b7dff53881e1a62ff8"
        self.command = ":Vu"  # Verify User
        self.checkpoint = 18   # From position 12
        self.path = "/"       # Final segment
        self.segments = [
            "V:",            # 563a8714
            "_N",           # 5f4e1fe2
            "qu",           # 71758895
            "hp",           # 68ff70d7
            "",             # dcae12b1
            "@",            # 8640d2b7
            "8",            # dff53881
            "/"             # e1a62ff8
        ]
        
    def execute_verification(self):
        print("Executing Verification Sequence")
        print("=" * 50)
        
        # Step 1: Initialize verification
        print("\nStep 1 - Command Initialization:")
        print(f"Command: {self.command}")
        
        # Hash the command
        cmd_hash = hashlib.sha256(self.command.encode()).hexdigest()
        print(f"Command hash: {cmd_hash}")
        
        # Step 2: Follow segment sequence
        print("\nStep 2 - Following Segments:")
        current_path = []
        for i, segment in enumerate(self.segments):
            print(f"\nSegment {i}: {segment}")
            
            # Get hex representation
            hex_seg = self.chain_code[i*8:(i+1)*8]
            print(f"Hex: {hex_seg}")
            
            # Try to interpret as number
            try:
                num = int(hex_seg, 16)
                print(f"As number: {num}")
                current_path.append(num)
            except:
                pass
                
            # Check for special markers
            if segment == "@":
                print("Found address marker")
            elif segment == "/":
                print("Found path separator")
                
        # Step 3: Use checkpoint
        print(f"\nStep 3 - Checkpoint Analysis (Position {self.checkpoint}):")
        if self.checkpoint * 2 < len(self.chain_code):
            checkpoint_value = self.chain_code[self.checkpoint*2:self.checkpoint*2+2]
            print(f"Value at checkpoint: {checkpoint_value}")
            try:
                as_num = int(checkpoint_value, 16)
                print(f"As number: {as_num}")
                # Check if it's a valid opcode
                if as_num <= 0x4e:
                    print(f"Could be opcode: OP_{as_num:02x}")
            except:
                pass
                
        # Step 4: Follow verification path
        print("\nStep 4 - Following Verification Path:")
        path_sequence = []
        
        # Start with command hash
        current = int(cmd_hash[:2], 16)
        path_sequence.append(current)
        
        # Follow for checkpoint steps
        for i in range(self.checkpoint):
            if current * 2 < len(self.chain_code):
                next_value = self.chain_code[current*2:current*2+2]
                try:
                    current = int(next_value, 16)
                    path_sequence.append(current)
                except:
                    break
                    
        print(f"Path sequence: {path_sequence}")
        
        # Step 5: Generate verification key
        print("\nStep 5 - Generating Verification Key:")
        
        # Combine all values
        verification_data = bytes([
            int(self.chain_code[i:i+2], 16) 
            for i in range(0, len(self.chain_code), 2)
            if i//2 in path_sequence
        ])
        
        verification_hash = hashlib.sha256(verification_data).hexdigest()
        print(f"Verification hash: {verification_hash}")
        
        # Step 6: Check for success markers
        print("\nStep 6 - Checking Success Markers:")
        
        # Look for special patterns
        success_markers = {
            "86": "Verify",
            "75": "User",
            "3a": "Command",
            "2f": "Path"
        }
        
        found_markers = []
        for marker, meaning in success_markers.items():
            if marker in self.chain_code:
                pos = self.chain_code.index(marker) // 2
                found_markers.append((pos, meaning))
                print(f"Found {meaning} marker at position {pos}")
                
        # Step 7: Final verification
        print("\nStep 7 - Final Verification:")
        
        # Check if we have all required markers
        required_markers = {"Verify", "User", "Command", "Path"}
        found_marker_types = {m[1] for m in found_markers}
        
        if required_markers.issubset(found_marker_types):
            print("All required markers found!")
            
            # Generate final key
            markers_data = bytes([pos for pos, _ in found_markers])
            final_key = hashlib.sha256(markers_data).hexdigest()
            print(f"Final key: {final_key}")
            
            # Try to decode final message
            try:
                message_bytes = bytes([int(final_key[i:i+2], 16) for i in range(0, 32, 2)])
                message = message_bytes.decode('ascii', errors='ignore')
                print(f"Decoded message: {message}")
            except:
                pass
        else:
            print("Missing required markers!")
            print(f"Found: {found_marker_types}")
            print(f"Required: {required_markers}")
            
def main():
    executor = VerificationExecutor()
    executor.execute_verification()

if __name__ == "__main__":
    main() 