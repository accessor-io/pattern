from crypto_utils import CryptoCommandUtils
from typing import List, Dict, Tuple
from collections import defaultdict

class AdvancedCryptoAnalysis:
    def __init__(self):
        self.utils = CryptoCommandUtils()

    def analyze_security_flow_patterns(self):
        """Combines security audit with command chain analysis to find
        complex security operation patterns"""
        print("\n=== Security Flow Pattern Analysis ===")
        
        # First, get all security-related commands
        security_ops = {
            'init_ops': self.utils.find_commands_by_operation('INIT'),
            'secure_ops': self.utils.find_commands_by_operation('SECURE'),
            'verify_ops': self.utils.find_commands_by_operation('VERIFY')
        }
        
        # Analyze security flow patterns
        print("\nAnalyzing security flow patterns:")
        for init_addr, init_cmd in security_ops['init_ops']:
            # Find related secure and verify operations
            related_cmds = self.utils.find_related_commands(init_addr)
            secure_verify = [cmd for cmd in related_cmds 
                           if 'SECURE' in cmd and 'VERIFY' in cmd]
            
            if secure_verify:
                print(f"\nInitialization Command: {init_cmd}")
                print("Related Secure-Verify Flows:")
                for cmd in secure_verify:
                    complexity = self.utils.analyze_command_complexity(cmd)
                    print(f"- {cmd}")
                    print(f"  Complexity: {complexity['total_operations']} operations")

    def analyze_operation_dependencies(self):
        """Combines command chain analysis with complexity comparison
        to understand operation dependencies and their impact"""
        print("\n=== Operation Dependency Analysis ===")
        
        # Define key operation types to analyze
        primary_ops = ['INIT', 'PROCESS', 'VERIFY']
        secondary_ops = ['MEMORY', 'BUFFER', 'SYNC']
        
        dependency_map = defaultdict(list)
        
        # Build dependency map
        for primary in primary_ops:
            print(f"\nAnalyzing dependencies for {primary} operations:")
            for secondary in secondary_ops:
                chains = self.utils.find_command_chain(primary, secondary)
                if chains:
                    dependency_map[primary].extend(chains)
                    print(f"\n{primary} -> {secondary} chain found:")
                    for chain in chains[:2]:  # Show first 2 examples
                        complexity = self.utils.analyze_command_complexity(chain)
                        print(f"- {chain}")
                        print(f"  Complexity: {complexity['total_operations']} operations")

    def analyze_command_patterns_by_complexity(self):
        """Combines sequence finding with complexity analysis to identify
        patterns in command structure based on complexity"""
        print("\n=== Command Pattern Complexity Analysis ===")
        
        # Group commands by complexity
        complexity_groups = defaultdict(list)
        
        # Analyze all commands
        for addr, cmd in self.utils.commands:
            complexity = self.utils.analyze_command_complexity(cmd)
            total_ops = complexity['total_operations']
            complexity_groups[total_ops].append(cmd)
        
        # Analyze patterns in each complexity group
        print("\nAnalyzing patterns by complexity level:")
        for complexity, commands in sorted(complexity_groups.items()):
            print(f"\nCommands with {complexity} operations:")
            # Show example commands and their common patterns
            for cmd in commands[:2]:  # Show first 2 examples
                print(f"- {cmd}")
            
            # Analyze common operation types in this complexity group
            common_ops = self._find_common_operations(commands)
            print("Common operations in this group:")
            for op, count in common_ops[:3]:  # Show top 3 common operations
                print(f"  {op}: appears in {count} commands")

    def _find_common_operations(self, commands: List[str]) -> List[Tuple[str, int]]:
        """Helper method to find common operations in a list of commands"""
        operation_count = defaultdict(int)
        for cmd in commands:
            operations = cmd.split('_')
            for op in operations:
                operation_count[op] += 1
        
        # Sort by frequency
        return sorted(operation_count.items(), key=lambda x: x[1], reverse=True)

    def analyze_security_complexity_correlation(self):
        """Combines security analysis with complexity comparison to understand
        the relationship between security operations and command complexity"""
        print("\n=== Security-Complexity Correlation Analysis ===")
        
        security_metrics = {
            'secure_commands': [],
            'non_secure_commands': []
        }
        
        # Categorize commands
        for addr, cmd in self.utils.commands:
            complexity = self.utils.analyze_command_complexity(cmd)
            if 'SECURE' in cmd or 'VERIFY' in cmd or 'GUARD' in cmd:
                security_metrics['secure_commands'].append((cmd, complexity))
            else:
                security_metrics['non_secure_commands'].append((cmd, complexity))
        
        # Analyze and compare metrics
        print("\nSecurity Operation Complexity Analysis:")
        for category, commands in security_metrics.items():
            if commands:
                avg_complexity = sum(c['total_operations'] for _, c in commands) / len(commands)
                print(f"\n{category.replace('_', ' ').title()}:")
                print(f"Average complexity: {avg_complexity:.2f} operations")
                print("Examples:")
                for cmd, complexity in commands[:2]:  # Show first 2 examples
                    print(f"- {cmd}")
                    print(f"  Operations: {complexity['total_operations']}")

def main():
    analyzer = AdvancedCryptoAnalysis()
    
    # Run combined analyses
    analyzer.analyze_security_flow_patterns()
    analyzer.analyze_operation_dependencies()
    analyzer.analyze_command_patterns_by_complexity()
    analyzer.analyze_security_complexity_correlation()

if __name__ == "__main__":
    main() 