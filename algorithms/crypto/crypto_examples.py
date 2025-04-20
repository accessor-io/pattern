from crypto_data import CRYPTO_MAPPINGS

def main():
    # Example 1: Find all initialization commands
    print("\n1. Finding all INIT commands:")
    init_commands = [cmd for addr, cmd in CRYPTO_MAPPINGS if cmd.startswith('INIT_')]
    for cmd in init_commands[:3]:  # Show first 3 examples
        print(f"  - {cmd}")

    # Example 2: Find a Bitcoin address for a specific command
    print("\n2. Finding address for a specific command:")
    target_command = "INIT_87_SECURE_FORWARD_MEMORY_VERIFY_QUEUE"
    address = next((addr for addr, cmd in CRYPTO_MAPPINGS if cmd == target_command), None)
    print(f"  Command: {target_command}")
    print(f"  Address: {address}")

    # Example 3: Group commands by operation type
    print("\n3. Commands grouped by operation type:")
    operation_types = {
        'MEMORY': [],
        'HASH': [],
        'VERIFY': []
    }
    
    for _, cmd in CRYPTO_MAPPINGS:
        for op_type in operation_types:
            if op_type in cmd:
                operation_types[op_type].append(cmd)
                break
    
    # Show example from each type
    for op_type, commands in operation_types.items():
        print(f"\n  {op_type} operations example:")
        print(f"  - {commands[0]}")

    # Example 4: Search for commands with specific patterns
    print("\n4. Finding commands with specific patterns:")
    secure_memory_commands = [
        cmd for _, cmd in CRYPTO_MAPPINGS 
        if 'SECURE' in cmd and 'MEMORY' in cmd
    ]
    print("  Secure Memory Operations:")
    print(f"  - {secure_memory_commands[0]}")

if __name__ == "__main__":
    main() 