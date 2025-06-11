from crypto_data import CRYPTO_MAPPINGS
from collections import defaultdict

def decode_operation_sequence():
    # Initialize tracking
    operations = []
    messages = []
    current_sequence = []
    
    # Key operation patterns we found
    patterns = [
        ('HASH', 'VERIFY', 'KEY'),
        ('CIPHER', 'SECURE', 'VERIFY'),
        ('KEY', 'HASH', 'VERIFY'),
        ('SECURE', 'HASH', 'KEY')
    ]
    
    # Track command sequences
    command_sequences = defaultdict(list)
    
    # First pass: Build operation sequences
    for addr, cmd in CRYPTO_MAPPINGS:
        ops = [op for op in cmd.split('_') if op in {'HASH', 'CIPHER', 'KEY', 'VERIFY', 'SECURE'}]
        if ops:
            operations.append((addr, ops))
            
            # Check for pattern matches
            for pattern in patterns:
                if all(p in ops for p in pattern):
                    command_sequences[pattern].append((addr, cmd))
                    
    print("\n=== Operation Sequence Analysis ===\n")
    
    # Analyze each pattern sequence
    for pattern, commands in command_sequences.items():
        print(f"\nPattern: {' -> '.join(pattern)}")
        print("Commands:")
        for addr, cmd in commands:
            print(f"{addr}: {cmd}")
            
            # Extract numbers after key operations
            numbers = []
            parts = cmd.split('_')
            for i, part in enumerate(parts):
                if part in pattern and i+1 < len(parts) and parts[i+1].isdigit():
                    numbers.append(int(parts[i+1]))
            
            if numbers:
                print(f"Numbers: {numbers}")
                # Try to decode numbers as ASCII
                ascii_chars = []
                for num in numbers:
                    if 32 <= num <= 126:  # Printable ASCII range
                        ascii_chars.append(chr(num))
                if ascii_chars:
                    print(f"ASCII: {''.join(ascii_chars)}")
                    messages.append(''.join(ascii_chars))
                    
            # Look for hex patterns in address
            addr_core = addr[1:-4]  # Remove Bitcoin prefix and checksum
            hex_chars = []
            for i in range(0, len(addr_core), 2):
                try:
                    char_code = int(addr_core[i:i+2], 16)
                    if 32 <= char_code <= 126:
                        hex_chars.append(chr(char_code))
                except:
                    continue
            if hex_chars:
                print(f"Address ASCII: {''.join(hex_chars)}")
                messages.append(''.join(hex_chars))
                
    # Analyze operation transitions
    print("\nOperation Transitions:")
    transitions = defaultdict(list)
    
    for i in range(len(operations)-1):
        current_addr, current_ops = operations[i]
        next_addr, next_ops = operations[i+1]
        
        if current_ops and next_ops:
            transition = (current_ops[-1], next_ops[0])
            transitions[transition].append((current_addr, next_addr))
            
    # Show most common transitions
    print("\nMost Common Operation Transitions:")
    for (op1, op2), addrs in sorted(transitions.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"\n{op1} -> {op2} ({len(addrs)} times)")
        for addr1, addr2 in addrs[:3]:  # Show first 3 examples
            print(f"  {addr1} -> {addr2}")
            
    # Look for circular patterns
    print("\nCircular Operation Patterns:")
    for i, (addr, ops) in enumerate(operations):
        if len(ops) >= 3 and ops[0] == ops[-1]:
            print(f"\n{addr}: {' -> '.join(ops)}")
            
    # Analyze collected messages
    if messages:
        print("\nCollected Message Fragments:")
        for msg in messages:
            print(msg)
            
    # Look for key transformations
    print("\nKey Transformations:")
    key_sequences = []
    for addr, cmd in CRYPTO_MAPPINGS:
        if 'KEY' in cmd:
            parts = cmd.split('_')
            key_index = parts.index('KEY')
            if key_index < len(parts) - 1:
                next_ops = parts[key_index+1:]
                key_sequences.append((addr, next_ops))
                
    for addr, sequence in key_sequences:
        print(f"\n{addr}:")
        print(f"KEY -> {' -> '.join(sequence)}")

def main():
    decode_operation_sequence()

if __name__ == "__main__":
    main() 