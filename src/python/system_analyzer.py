import networkx as nx
from collections import defaultdict
import json
from crypto_data import CRYPTO_MAPPINGS

class SystemAnalyzer:
    def __init__(self):
        self.command_graph = nx.DiGraph()
        self.operation_graph = nx.DiGraph()
        self.address_map = {}
        self.command_levels = defaultdict(list)
        self.critical_paths = []
        
    def load_mappings(self):
        """Load and process all crypto mappings"""
        for address, command in CRYPTO_MAPPINGS:
            self.address_map[command] = address
            operations = command.split('_')
            
            # Add command node
            self.command_graph.add_node(command, type='command', address=address)
            
            # Add operation nodes and edges
            prev_op = None
            for op in operations:
                if not op.isdigit():  # Skip numeric operations
                    self.operation_graph.add_node(op, type='operation')
                    if prev_op:
                        self.operation_graph.add_edge(prev_op, op)
                    prev_op = op
                    
    def analyze_command_structure(self):
        """Analyze the command structure and relationships"""
        results = {
            "total_commands": len(self.command_graph),
            "total_operations": len(self.operation_graph),
            "critical_operations": self.find_critical_operations(),
            "command_chains": self.find_command_chains(),
            "operation_flows": self.analyze_operation_flows(),
            "encryption_patterns": self.find_encryption_patterns()
        }
        return results
        
    def find_critical_operations(self):
        """Find critical cryptographic operations and their connections"""
        critical_ops = {'HASH', 'CIPHER', 'ENCRYPT', 'DECRYPT', 'KEY', 'VERIFY', 'SECURE'}
        critical_paths = []
        
        for start in critical_ops:
            if start not in self.operation_graph:
                continue
            for end in critical_ops:
                if end not in self.operation_graph or start == end:
                    continue
                try:
                    path = nx.shortest_path(self.operation_graph, start, end)
                    if len(path) > 1:
                        critical_paths.append({
                            'start': start,
                            'end': end,
                            'path': path,
                            'length': len(path)
                        })
                except nx.NetworkXNoPath:
                    continue
                    
        return critical_paths
        
    def find_command_chains(self):
        """Find sequential command chains in the system"""
        chains = []
        visited = set()
        
        def dfs_chain(command, current_chain):
            if len(current_chain) > 0:
                chains.append(current_chain[:])
            
            visited.add(command)
            next_commands = [cmd for cmd in self.command_graph[command] 
                           if cmd not in visited]
            
            for next_cmd in next_commands:
                dfs_chain(next_cmd, current_chain + [next_cmd])
                
            visited.remove(command)
            
        # Start DFS from each command
        for command in self.command_graph.nodes():
            if command not in visited:
                dfs_chain(command, [command])
                
        return chains
        
    def analyze_operation_flows(self):
        """Analyze operation flows and patterns"""
        flows = defaultdict(list)
        
        # Analyze operation transitions
        for op1, op2 in self.operation_graph.edges():
            flows[op1].append(op2)
            
        # Find common operation sequences
        sequences = []
        for op in flows:
            if len(flows[op]) > 0:
                sequences.append({
                    'operation': op,
                    'leads_to': flows[op],
                    'frequency': len(flows[op])
                })
                
        return sorted(sequences, key=lambda x: x['frequency'], reverse=True)
        
    def find_encryption_patterns(self):
        """Identify potential encryption patterns in the system"""
        patterns = []
        
        # Look for cyclic patterns involving crypto operations
        try:
            cycles = list(nx.simple_cycles(self.operation_graph))
            crypto_cycles = [c for c in cycles if any(op in c for op in 
                           {'HASH', 'CIPHER', 'ENCRYPT', 'DECRYPT'})]
            
            for cycle in crypto_cycles:
                patterns.append({
                    'cycle': cycle,
                    'length': len(cycle),
                    'crypto_ops': [op for op in cycle if op in 
                                 {'HASH', 'CIPHER', 'ENCRYPT', 'DECRYPT'}]
                })
        except:
            pass
            
        return patterns

def main():
    analyzer = SystemAnalyzer()
    analyzer.load_mappings()
    
    results = analyzer.analyze_command_structure()
    
    print("\n=== System Analysis Results ===\n")
    
    print(f"Total Commands: {results['total_commands']}")
    print(f"Total Operations: {results['total_operations']}")
    
    print("\nCritical Operation Paths:")
    for path in results['critical_operations'][:5]:  # Show top 5
        print(f"  {' -> '.join(path['path'])}")
        
    print("\nMajor Operation Flows:")
    for flow in results['operation_flows'][:10]:  # Show top 10
        print(f"  {flow['operation']} leads to {len(flow['leads_to'])} operations")
        
    print("\nEncryption Patterns Found:")
    for pattern in results['encryption_patterns'][:5]:  # Show top 5
        print(f"  Cycle: {' -> '.join(pattern['cycle'])}")
        print(f"  Crypto Operations: {', '.join(pattern['crypto_ops'])}")
        
    print("\nCommand Chain Analysis:")
    chains = results['command_chains']
    significant_chains = [c for c in chains if len(c) >= 3][:5]  # Show top 5 significant chains
    for chain in significant_chains:
        print(f"\nChain length {len(chain)}:")
        for cmd in chain:
            print(f"  {cmd} ({analyzer.address_map[cmd]})")

if __name__ == "__main__":
    main() 