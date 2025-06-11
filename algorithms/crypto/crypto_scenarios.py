from crypto_utils import CryptoCommandUtils
from typing import List, Dict
import json

class CryptoScenarios:
    def __init__(self):
        self.utils = CryptoCommandUtils()

    def scenario_1_security_audit(self):
        """Scenario 1: Security Operation Audit
        Find all commands related to security operations and analyze their complexity"""
        print("\n=== Security Operation Audit ===")
        
        # Find all security-related commands
        security_ops = ['SECURE', 'VERIFY', 'GUARD']
        security_commands = {}
        
        for op in security_ops:
            commands = self.utils.find_commands_by_operation(op)
            security_commands[op] = commands
            print(f"\nFound {len(commands)} commands with {op} operations:")
            for addr, cmd in commands[:2]:  # Show first 2 examples
                complexity = self.utils.analyze_command_complexity(cmd)
                print(f"\nAddress: {addr}")
                print(f"Command: {cmd}")
                print(f"Complexity: {complexity['total_operations']} operations")

    def scenario_2_command_chain_analysis(self):
        """Scenario 2: Command Chain Analysis
        Analyze different command chains for process flows"""
        print("\n=== Command Chain Analysis ===")
        
        chains = [
            ('INIT', 'VERIFY'),
            ('PROCESS', 'MEMORY'),
            ('LOAD', 'EXECUTE')
        ]
        
        for start, end in chains:
            commands = self.utils.find_command_chain(start, end)
            print(f"\nCommands that start with {start} and contain {end}:")
            for cmd in commands[:2]:  # Show first 2 examples
                print(f"- {cmd}")

    def scenario_3_operation_sequence_finder(self):
        """Scenario 3: Operation Sequence Finder
        Find commands that follow specific operation sequences"""
        print("\n=== Operation Sequence Analysis ===")
        
        sequences = [
            ['INIT', 'SECURE', 'VERIFY'],
            ['LOAD', 'MEMORY', 'EXECUTE'],
            ['PROCESS', 'BUFFER', 'SYNC']
        ]
        
        for seq in sequences:
            print(f"\nLooking for sequence: {' -> '.join(seq)}")
            commands = self.utils.get_command_sequence(seq)
            if commands:
                print("Found matching commands:")
                for cmd in commands[:2]:  # Show first 2 examples
                    print(f"- {cmd}")
            else:
                print("No exact matches found")

    def scenario_4_related_command_analysis(self):
        """Scenario 4: Related Command Analysis
        Analyze groups of related commands"""
        print("\n=== Related Command Analysis ===")
        
        # Start with a security-focused command
        security_commands = self.utils.find_commands_by_operation('SECURE')
        if security_commands:
            addr, cmd = security_commands[0]
            print(f"\nBase command: {cmd}")
            print("Related commands:")
            related = self.utils.find_related_commands(addr, 3)
            for rel_cmd in related:
                print(f"- {rel_cmd}")

    def scenario_5_command_complexity_comparison(self):
        """Scenario 5: Command Complexity Comparison
        Compare complexity of different types of commands"""
        print("\n=== Command Complexity Comparison ===")
        
        operation_types = ['INIT', 'PROCESS', 'VERIFY']
        for op_type in operation_types:
            commands = self.utils.find_commands_by_operation(op_type)
            if commands:
                addr, cmd = commands[0]
                complexity = self.utils.analyze_command_complexity(cmd)
                print(f"\n{op_type} Command Example:")
                print(f"Command: {cmd}")
                print(f"Total Operations: {complexity['total_operations']}")
                print(f"Unique Operations: {complexity['unique_operations']}")

def main():
    scenarios = CryptoScenarios()
    
    # Run all scenarios
    scenarios.scenario_1_security_audit()
    scenarios.scenario_2_command_chain_analysis()
    scenarios.scenario_3_operation_sequence_finder()
    scenarios.scenario_4_related_command_analysis()
    scenarios.scenario_5_command_complexity_comparison()

if __name__ == "__main__":
    main() 