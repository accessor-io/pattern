import hashlib
import binascii

class PathExecutor:
    def __init__(self):
        self.chain_code = "563a87145f4e1fe27175889568ff70d7dcae12b18640d2b7dff53881e1a62ff8"
        self.path = ["V:", "_N", "qu", "hp", "@", "8", "/"]
        self.key = "dd8aa461815ed658d5a79857d33fd316a5d05610f2f45c873ba46ef7ec9dacd0"
        
    def execute_path(self):
        print("Executing Command Path")
        print("=" * 50)
        
        # Step 1: Initialize with key
        print("\nStep 1 - Key Initialization:")
        key_bytes = bytes.fromhex(self.key)
        print(f"Key: {self.key}")
        
        # Step 2: Follow path
        print("\nStep 2 - Following Path:")
        current_value = None
        for i, step in enumerate(self.path):
            print(f"\nStep {i+1}: {step}")
            
            # Get position in chain code
            pos = self.chain_code.find(step.encode().hex())
            if pos >= 0:
                value = self.chain_code[pos:pos+8]
                print(f"Found at position {pos//2}")
                print(f"Value: {value}")
                
                # Try to interpret value
                try:
                    as_num = int(value, 16)
                    print(f"As number: {as_num}")
                    current_value = as_num
                except:
                    pass
                    
                # Special handling for markers
                if step == "@":
                    print("Address marker - using as index")
                    if current_value and current_value * 2 < len(self.chain_code):
                        addr_value = self.chain_code[current_value*2:current_value*2+8]
                        print(f"Address value: {addr_value}")
                elif step == "/":
                    print("Path separator - following path")
                    if current_value:
                        path_value = current_value % len(self.chain_code)
                        print(f"Next path: {path_value}")
                        
        # Step 3: Generate command sequence
        print("\nStep 3 - Generating Command:")
        command_bytes = b""
        for step in self.path:
            command_bytes += step.encode()
        command_hash = hashlib.sha256(command_bytes).hexdigest()
        print(f"Command hash: {command_hash}")
        
        # Step 4: XOR with key
        print("\nStep 4 - Combining with Key:")
        if len(command_bytes) > 0:
            # Pad command to key length
            padded_command = command_bytes + b"\x00" * (32 - len(command_bytes))
            result = bytes(a ^ b for a, b in zip(padded_command, key_bytes))
            print(f"Result: {result.hex()}")
            
            # Try to decode result
            try:
                decoded = result.decode('ascii', errors='ignore')
                print(f"Decoded: {decoded}")
            except:
                pass
                
        # Step 5: Follow final path
        print("\nStep 5 - Following Final Path:")
        if current_value:
            path = []
            current = current_value % len(self.chain_code)
            for _ in range(8):  # Follow up to 8 steps
                if current * 2 < len(self.chain_code):
                    value = self.chain_code[current*2:current*2+2]
                    path.append(value)
                    try:
                        current = int(value, 16)
                    except:
                        break
                        
            print(f"Path values: {path}")
            
            # Try to combine path values
            if path:
                combined = ''.join(path)
                print(f"Combined path: {combined}")
                try:
                    path_bytes = bytes.fromhex(combined)
                    print(f"As bytes: {path_bytes.hex()}")
                    print(f"As ASCII: {path_bytes.decode('ascii', errors='ignore')}")
                except:
                    pass
                    
def main():
    executor = PathExecutor()
    executor.execute_path()

if __name__ == "__main__":
    main() 