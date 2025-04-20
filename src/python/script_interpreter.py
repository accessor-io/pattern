import hashlib
import binascii

class BitcoinScriptInterpreter:
    def __init__(self):
        self.stack = []
        self.chain_code = "000000000000000000000000000000000000000000000002832ed74f2b5e35ee"
        
    def execute_script(self):
        print("Executing Bitcoin Script")
        print("=" * 50)
        
        # Extract opcodes we found
        opcodes = [
            (0x56, "OP_PUSH"),  # First byte
            (0x3a, "OP_COMPARE"),
            (0x14, "PUSH_20"),
            (0x4e, "PUSH_DATA"),
            (0x1f, "OP_NEGATE"),
            (0x12, "PUSH_18"),
            (0x40, "OP_RESERVED"),
            (0x38, "OP_SIZE"),
            (0x2f, "OP_LESSTHANOREQUAL")
        ]
        
        print("\nExecuting Opcodes:")
        
        for opcode, name in opcodes:
            print(f"\nOpcode {opcode:02x} ({name})")
            
            if opcode == 0x56:
                # Push the next byte
                self.stack.append(bytes([0x56]))
                
            elif opcode == 0x3a:
                # Compare top two stack items
                if len(self.stack) >= 2:
                    a = self.stack.pop()
                    b = self.stack.pop()
                    self.stack.append(bytes([1 if a == b else 0]))
                    
            elif opcode == 0x14:
                # Push next 20 bytes
                next_bytes = binascii.unhexlify(self.chain_code[2:42])
                self.stack.append(next_bytes)
                
            elif opcode == 0x4e:
                # Push data with size from stack
                if len(self.stack) >= 1:
                    size = int.from_bytes(self.stack.pop(), 'big')
                    if size * 2 <= len(self.chain_code):
                        data = binascii.unhexlify(self.chain_code[:size*2])
                        self.stack.append(data)
                        
            elif opcode == 0x1f:
                # Negate top stack item
                if len(self.stack) >= 1:
                    num = int.from_bytes(self.stack.pop(), 'big')
                    self.stack.append((-num).to_bytes(32, 'big', signed=True))
                    
            elif opcode == 0x12:
                # Push next 18 bytes
                next_bytes = binascii.unhexlify(self.chain_code[2:38])
                self.stack.append(next_bytes)
                
            elif opcode == 0x38:
                # Get size of top stack item
                if len(self.stack) >= 1:
                    size = len(self.stack[-1])
                    self.stack.append(bytes([size]))
                    
            elif opcode == 0x2f:
                # Less than or equal
                if len(self.stack) >= 2:
                    a = int.from_bytes(self.stack.pop(), 'big')
                    b = int.from_bytes(self.stack.pop(), 'big')
                    self.stack.append(bytes([1 if a <= b else 0]))
                    
            print("Stack:", [binascii.hexlify(x).decode() for x in self.stack])
            
        print("\nFinal Stack:", [binascii.hexlify(x).decode() for x in self.stack])
        return True

def main():
    interpreter = BitcoinScriptInterpreter()
    success = interpreter.execute_script()
    print(f"\nScript execution {'succeeded' if success else 'failed'}")

if __name__ == "__main__":
    main()
