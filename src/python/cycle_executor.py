import hashlib
import binascii

class CycleExecutor:
    def __init__(self):
        self.chain_code = "563a87145f4e1fe27175889568ff70d7dcae12b18640d2b7dff53881e1a62ff8"
        self.cycle = [
            ("V", "Verify", 0x56),
            (":", "Command", 0x3a),
            ("_N", "Next", 0x4e),
            ("qu", "Query", 0x71),
            ("hp", "Helper", 0x68),
            ("@", "Address", 0x40),
            ("8", "Value", 0x38),
            ("/", "Path", 0x2f)
        ]
        self.key = "8bb0fb2ff02bbe28959fb757d33fd316a5d05610f2f45c873ba46ef7ec9dacd0"
        
    def execute_cycle(self):
        print("Executing Verification Cycle")
        print("=" * 50)
        
        # Step 1: Initialize cycle
        print("\nStep 1 - Cycle Initialization:")
        cycle_bytes = bytes([op for _, _, op in self.cycle])
        cycle_hash = hashlib.sha256(cycle_bytes).hexdigest()
        print(f"Cycle hash: {cycle_hash}")
        
        # Step 2: Execute each step
        print("\nStep 2 - Executing Steps:")
        current_value = None
        accumulated = []
        
        for symbol, name, opcode in self.cycle:
            print(f"\nExecuting {name} ({symbol}):")
            
            # Find position in chain code
            hex_op = f"{opcode:02x}"
            pos = self.chain_code.find(hex_op)
            if pos >= 0:
                # Get 4 bytes at position
                value = self.chain_code[pos:pos+8]
                print(f"Found at position {pos//2}")
                print(f"Value: {value}")
                
                try:
                    as_num = int(value, 16)
                    print(f"As number: {as_num}")
                    current_value = as_num
                    accumulated.append(as_num)
                except:
                    pass
                    
                # Special handling
                if name == "Verify":
                    print("Verifying sequence start")
                elif name == "Command":
                    print("Command separator")
                elif name == "Next":
                    print("Moving to next operation")
                elif name == "Query":
                    print("Querying system")
                elif name == "Helper":
                    print("Helper function")
                elif name == "Address":
                    print("Address marker")
                    if current_value:
                        addr_pos = current_value % len(self.chain_code)
                        addr_value = self.chain_code[addr_pos*2:(addr_pos+1)*2]
                        print(f"Address value: {addr_value}")
                elif name == "Value":
                    print("Value marker")
                    if current_value:
                        val_pos = current_value % len(self.chain_code)
                        val_value = self.chain_code[val_pos*2:(val_pos+1)*2]
                        print(f"Marked value: {val_value}")
                elif name == "Path":
                    print("Path separator")
                    if current_value:
                        path_pos = current_value % len(self.chain_code)
                        path_value = self.chain_code[path_pos*2:(path_pos+1)*2]
                        print(f"Next path: {path_value}")
                        
        # Step 3: Analyze accumulated values
        print("\nStep 3 - Analyzing Accumulated Values:")
        if accumulated:
            # Convert to bytes
            acc_bytes = b"".join(x.to_bytes(4, 'big') for x in accumulated)
            acc_hash = hashlib.sha256(acc_bytes).hexdigest()
            print(f"Accumulated hash: {acc_hash}")
            
            # XOR with key
            key_bytes = bytes.fromhex(self.key)
            if len(acc_bytes) >= len(key_bytes):
                result = bytes(a ^ b for a, b in zip(acc_bytes[:len(key_bytes)], key_bytes))
                print(f"XOR with key: {result.hex()}")
                try:
                    print(f"As ASCII: {result.decode('ascii', errors='ignore')}")
                except:
                    pass
                    
        # Step 4: Follow final path
        print("\nStep 4 - Following Final Path:")
        if current_value:
            path = []
            current = current_value % len(self.chain_code)
            
            # Follow path for 8 steps
            for i in range(8):
                if current * 2 < len(self.chain_code):
                    value = self.chain_code[current*2:current*2+2]
                    path.append(value)
                    print(f"Step {i+1}: Position {current} -> {value}")
                    try:
                        current = int(value, 16)
                    except:
                        break
                        
            # Try to decode path
            if path:
                combined = ''.join(path)
                print(f"\nCombined path: {combined}")
                try:
                    path_bytes = bytes.fromhex(combined)
                    print(f"As ASCII: {path_bytes.decode('ascii', errors='ignore')}")
                except:
                    pass
                    
        # Step 5: Generate verification result
        print("\nStep 5 - Verification Result:")
        if accumulated and len(accumulated) == len(self.cycle):
            # Final verification hash
            final_bytes = bytes([x % 256 for x in accumulated])
            final_hash = hashlib.sha256(final_bytes).hexdigest()
            print(f"Final hash: {final_hash}")
            
            # Compare with key
            if final_hash == self.key:
                print("VERIFICATION SUCCESSFUL!")
            else:
                print("Verification failed")
                
def main():
    executor = CycleExecutor()
    executor.execute_cycle()

if __name__ == "__main__":
    main() 