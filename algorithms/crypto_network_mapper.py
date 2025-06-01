from crypto_data import CRYPTO_MAPPINGS
from collections import defaultdict

class NetworkMapper:
    def __init__(self):
        self.mappings = CRYPTO_MAPPINGS
        self.nodes = {}  # Command nodes
        self.edges = []  # Command connections
        self.operation_flows = defaultdict(list)  # Operation sequences
        
    def build_network(self):
        """Build the complete command network"""
        # First pass: Create nodes
        for addr, cmd in self.mappings:
            if cmd not in self.nodes:
                self.nodes[cmd] = {
                    'address': addr,
                    'operations': cmd.split('_'),
                    'connections': set(),
                    'level': 0
                }
        
        # Second pass: Create edges
        for cmd1 in self.nodes:
            ops1 = set(cmd1.split('_'))
            for cmd2 in self.nodes:
                if cmd1 != cmd2:
                    ops2 = set(cmd2.split('_'))
                    shared = ops1 & ops2
                    if shared:
                        self.nodes[cmd1]['connections'].add(cmd2)
                        self.edges.append({
                            'from': cmd1,
                            'to': cmd2,
                            'shared_ops': shared,
                            'weight': len(shared)
                        })
        
        # Third pass: Assign levels (distance from master key)
        start_cmd = self.mappings[0][1]  # Master key command
        self._assign_levels(start_cmd)
        
        # Fourth pass: Track operation flows
        self._analyze_operation_flows()
    
    def _assign_levels(self, start_cmd, level=0, visited=None):
        """Recursively assign levels to nodes based on distance from start"""
        if visited is None:
            visited = set()
            
        if start_cmd in visited:
            return
            
        visited.add(start_cmd)
        self.nodes[start_cmd]['level'] = level
        
        for cmd2 in self.nodes[start_cmd]['connections']:
            self._assign_levels(cmd2, level + 1, visited)
    
    def _analyze_operation_flows(self):
        """Analyze how operations flow through the network"""
        for edge in self.edges:
            ops1 = self.nodes[edge['from']]['operations']
            ops2 = self.nodes[edge['to']]['operations']
            
            # Track operation transitions
            for i in range(len(ops1)-1):
                self.operation_flows[ops1[i]].append(ops1[i+1])
            for i in range(len(ops2)-1):
                self.operation_flows[ops2[i]].append(ops2[i+1])
    
    def get_command_paths(self, start_cmd, max_depth=3):
        """Find all possible command paths from start"""
        paths = []
        
        def explore(cmd, path=None, depth=0):
            if depth >= max_depth:
                paths.append(path)
                return
                
            current_path = path + [cmd] if path else [cmd]
            
            # Get next possible commands
            next_cmds = self.nodes[cmd]['connections']
            if not next_cmds or depth == max_depth - 1:
                paths.append(current_path)
                return
                
            for next_cmd in next_cmds:
                explore(next_cmd, current_path, depth + 1)
        
        explore(start_cmd)
        return paths
    
    def find_central_commands(self):
        """Find commands that are most connected"""
        return sorted(self.nodes.items(), 
                     key=lambda x: len(x[1]['connections']), 
                     reverse=True)
    
    def find_operation_sequences(self):
        """Find common operation sequences"""
        sequences = defaultdict(int)
        
        for edge in self.edges:
            ops1 = self.nodes[edge['from']]['operations']
            ops2 = self.nodes[edge['to']]['operations']
            
            # Look for operation pairs
            for op1 in ops1:
                for op2 in ops2:
                    if op1 != op2:
                        sequences[(op1, op2)] += 1
        
        return sequences

def main():
    # Initialize and build network
    mapper = NetworkMapper()
    print("Building command network...")
    mapper.build_network()
    
    # Show network structure
    print("\nNetwork Structure:")
    print(f"Total Commands: {len(mapper.nodes)}")
    print(f"Total Connections: {len(mapper.edges)}")
    
    # Show levels
    print("\nCommand Levels (distance from master key):")
    for cmd, data in sorted(mapper.nodes.items(), key=lambda x: x[1]['level']):
        print(f"\nLevel {data['level']}:")
        print(f"Command: {cmd}")
        print(f"Address: {data['address']}")
        print(f"Connections: {len(data['connections'])}")
    
    # Show central commands
    print("\nMost Connected Commands:")
    for cmd, data in mapper.find_central_commands()[:5]:
        print(f"\n{cmd}")
        print(f"Connections: {len(data['connections'])}")
        print(f"Operations: {data['operations']}")
    
    # Show common operation sequences
    print("\nCommon Operation Sequences:")
    sequences = mapper.find_operation_sequences()
    for (op1, op2), count in sorted(sequences.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{op1} -> {op2}: {count} times")
    
    # Show operation flows
    print("\nOperation Flow Patterns:")
    for op, next_ops in mapper.operation_flows.items():
        common_next = defaultdict(int)
        for next_op in next_ops:
            common_next[next_op] += 1
        
        print(f"\nFrom {op} to:")
        for next_op, count in sorted(common_next.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"  {next_op}: {count} times")
    
    # Show some complete paths
    print("\nExample Command Paths:")
    start_cmd = mapper.mappings[0][1]  # Master key command
    paths = mapper.get_command_paths(start_cmd)
    
    for i, path in enumerate(paths[:3]):
        print(f"\nPath {i+1}:")
        for j, cmd in enumerate(path):
            print(f"Step {j+1}: {cmd}")

if __name__ == "__main__":
    main() 