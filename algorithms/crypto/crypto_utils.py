from typing import List, Dict, Optional, Set, Tuple
from crypto_data import CRYPTO_MAPPINGS

class CryptoCommandUtils:
    def __init__(self):
        self.commands = CRYPTO_MAPPINGS
        self._build_indices()

    def _build_indices(self):
        """Build lookup indices for faster searching"""
        self.command_to_address = {cmd: addr for addr, cmd in self.commands}
        self.address_to_command = {addr: cmd for addr, cmd in self.commands}
        
        # Build operation type index
        self.operation_types: Set[str] = set()
        for _, cmd in self.commands:
            self.operation_types.update(word for word in cmd.split('_'))

    def get_all_operation_types(self) -> Set[str]:
        """Get all unique operation types found in commands"""
        return self.operation_types

    def find_commands_by_operation(self, operation: str) -> List[Tuple[str, str]]:
        """Find all commands containing a specific operation type"""
        operation = operation.upper()
        return [(addr, cmd) for addr, cmd in self.commands if operation in cmd]

    def find_command_chain(self, start_op: str, end_op: str) -> List[str]:
        """Find commands that could form a chain from start_op to end_op"""
        start_op, end_op = start_op.upper(), end_op.upper()
        return [cmd for _, cmd in self.commands if cmd.startswith(start_op) and end_op in cmd]

    def analyze_command_complexity(self, command: str) -> Dict[str, int]:
        """Analyze the complexity of a command based on operation count"""
        if command not in self.command_to_address:
            return {}
        
        operations = command.split('_')
        complexity = {
            'total_operations': len(operations),
            'unique_operations': len(set(operations))
        }
        return complexity

    def find_related_commands(self, address: str, max_results: int = 5) -> List[str]:
        """Find commands related to the command associated with given address"""
        if address not in self.address_to_command:
            return []
            
        base_cmd = self.address_to_command[address]
        base_ops = set(base_cmd.split('_'))
        
        # Find commands that share operations
        related = []
        for addr, cmd in self.commands:
            if addr == address:
                continue
            
            cmd_ops = set(cmd.split('_'))
            common_ops = len(base_ops.intersection(cmd_ops))
            if common_ops > 0:
                related.append((common_ops, cmd))
        
        # Sort by number of common operations and return top results
        related.sort(reverse=True)
        return [cmd for _, cmd in related[:max_results]]

    def get_command_sequence(self, operations: List[str]) -> List[str]:
        """Find commands that contain operations in sequence"""
        operations = [op.upper() for op in operations]
        matching_commands = []
        
        for _, cmd in self.commands:
            cmd_ops = cmd.split('_')
            if self._contains_sequence(cmd_ops, operations):
                matching_commands.append(cmd)
                
        return matching_commands

    def _contains_sequence(self, cmd_ops: List[str], sequence: List[str]) -> bool:
        """Helper method to check if command contains operation sequence"""
        for i in range(len(cmd_ops) - len(sequence) + 1):
            if all(cmd_ops[i + j] == sequence[j] for j in range(len(sequence))):
                return True
        return False

def main():
    # Create utility instance
    crypto_utils = CryptoCommandUtils()
    
    print("\n1. Available Operation Types:")
    operations = sorted(list(crypto_utils.get_all_operation_types()))[:5]
    print(f"  First 5 operation types: {', '.join(operations)}")
    
    print("\n2. Commands with SECURE operations:")
    secure_commands = crypto_utils.find_commands_by_operation('SECURE')[:2]
    for addr, cmd in secure_commands:
        print(f"  Address: {addr}")
        print(f"  Command: {cmd}\n")
    
    print("3. Finding command chains:")
    init_verify_chain = crypto_utils.find_command_chain('INIT', 'VERIFY')[:2]
    print("  INIT to VERIFY chain examples:")
    for cmd in init_verify_chain:
        print(f"  - {cmd}")
    
    print("\n4. Command Complexity Analysis:")
    sample_cmd = "INIT_87_SECURE_FORWARD_MEMORY_VERIFY_QUEUE"
    complexity = crypto_utils.analyze_command_complexity(sample_cmd)
    print(f"  Command: {sample_cmd}")
    print(f"  Total Operations: {complexity['total_operations']}")
    print(f"  Unique Operations: {complexity['unique_operations']}")
    
    print("\n5. Related Commands:")
    sample_address = "187swFMjz1G54ycVU56B7jZFHFTNVQFDiu"  # Address for INIT_87_SECURE...
    related = crypto_utils.find_related_commands(sample_address, 2)
    print(f"  Commands related to address {sample_address}:")
    for cmd in related:
        print(f"  - {cmd}")
    
    print("\n6. Operation Sequences:")
    sequence = ['INIT', 'SECURE', 'VERIFY']
    sequence_commands = crypto_utils.get_command_sequence(sequence)[:2]
    print(f"  Commands containing sequence {' -> '.join(sequence)}:")
    for cmd in sequence_commands:
        print(f"  - {cmd}")

if __name__ == "__main__":
    main() 