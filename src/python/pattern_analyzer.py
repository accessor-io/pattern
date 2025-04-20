import networkx as nx
from collections import defaultdict

class PatternAnalyzer:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.operation_sequences = defaultdict(int)
        self.command_levels = defaultdict(list)
        
    def add_command(self, command, level, address):
        operations = command.split('_')
        self.command_levels[level].append((command, address))
        
        # Add nodes and edges for operations
        prev_op = None
        for op in operations:
            if prev_op:
                self.graph.add_edge(prev_op, op)
                self.operation_sequences[(prev_op, op)] += 1
            prev_op = op
            
    def find_critical_paths(self):
        """Find paths that could represent cryptographic operations"""
        critical_ops = {'HASH', 'CIPHER', 'ENCRYPT', 'DECRYPT', 'KEY', 'VERIFY'}
        paths = []
        
        for start in critical_ops:
            if start not in self.graph:
                continue
            for end in critical_ops:
                if end not in self.graph or start == end:
                    continue
                try:
                    path = nx.shortest_path(self.graph, start, end)
                    if len(path) > 1:
                        paths.append(path)
                except nx.NetworkXNoPath:
                    continue
        return paths
    
    def analyze_operation_patterns(self):
        """Analyze patterns in operation sequences"""
        patterns = defaultdict(list)
        
        # Group by first operation
        for (op1, op2), count in self.operation_sequences.items():
            patterns[op1].append((op2, count))
            
        # Sort by frequency
        for op in patterns:
            patterns[op].sort(key=lambda x: x[1], reverse=True)
            
        return patterns
    
    def find_cyclic_patterns(self):
        """Find cyclic patterns that could represent encryption rounds"""
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return [c for c in cycles if any(op in c for op in {'HASH', 'CIPHER', 'ENCRYPT'})]
        except:
            return []

def main():
    analyzer = PatternAnalyzer()
    
    # Add commands from the network analysis
    # Example commands:
    analyzer.add_command("BEGIN_GATEWAY_ZERO_TRANSFER_SECURE_ACCESS_METHOD", 0, "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH")
    analyzer.add_command("LINK_5c9_MEMORY_PROCESS_GATEWAY_LOAD_BUFFER", 1, "15c9mPGLku1HuW9LRtBf4jcHVpBUt8txKz")
    analyzer.add_command("INIT_8Z_MEMORY_BUFFER_UNIFORM_FORWARD_LOAD", 2, "18ZMbwUFLMHoZBbfpCjUJQTCMCbktshgpe")
    
    print("Critical Cryptographic Paths:")
    paths = analyzer.find_critical_paths()
    for path in paths[:5]:  # Show top 5 paths
        print(" -> ".join(path))
        
    print("\nOperation Patterns:")
    patterns = analyzer.analyze_operation_patterns()
    for op in ['HASH', 'CIPHER', 'KEY', 'VERIFY']:
        if op in patterns:
            print(f"\n{op} leads to:")
            for next_op, count in patterns[op][:3]:
                print(f"  {next_op}: {count} times")
                
    print("\nCyclic Patterns (Potential Encryption Rounds):")
    cycles = analyzer.find_cyclic_patterns()
    for cycle in cycles[:3]:  # Show top 3 cycles
        print(" -> ".join(cycle + [cycle[0]]))

if __name__ == "__main__":
    main() 