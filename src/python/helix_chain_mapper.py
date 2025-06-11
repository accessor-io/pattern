from crypto_data import CRYPTO_MAPPINGS
from collections import defaultdict

def find_related_commands(current_cmd, current_addr):
    """Find all related commands based on shared operations"""
    related = []
    cmd_parts = set(current_cmd.split('_'))
    
    for addr, cmd in CRYPTO_MAPPINGS:
        if addr != current_addr:
            next_parts = set(cmd.split('_'))
            shared = cmd_parts & next_parts
            if shared:
                related.append({
                    'address': addr,
                    'command': cmd,
                    'shared_ops': shared,
                    'similarity': len(shared) / len(cmd_parts)
                })
    
    # Sort by similarity
    return sorted(related, key=lambda x: x['similarity'], reverse=True)

def map_command_paths(start_address, max_depth=3, max_branches=3):
    """Map multiple possible command paths"""
    paths = []
    visited = set()
    
    def explore_path(addr, path=None, depth=0):
        if depth >= max_depth or addr in visited:
            paths.append(path)
            return
        
        visited.add(addr)
        current_cmd = next(cmd for a, cmd in CRYPTO_MAPPINGS if a == addr)
        
        # Find related commands
        related = find_related_commands(current_cmd, addr)
        
        # Explore top branches
        for branch in related[:max_branches]:
            new_path = path + [{'address': addr, 'command': current_cmd}] if path else [{'address': addr, 'command': current_cmd}]
            explore_path(branch['address'], new_path, depth + 1)
        
        visited.remove(addr)
    
    explore_path(start_address)
    return paths

def analyze_path_patterns(paths):
    """Analyze patterns across different command paths"""
    analysis = {
        'common_sequences': defaultdict(int),
        'operation_flows': defaultdict(int),
        'address_patterns': defaultdict(list)
    }
    
    for path in paths:
        # Analyze command sequences
        if len(path) >= 2:
            for i in range(len(path)-1):
                seq = (path[i]['command'], path[i+1]['command'])
                analysis['common_sequences'][seq] += 1
        
        # Analyze operation flows
        for node in path:
            ops = node['command'].split('_')
            for i in range(len(ops)-1):
                flow = (ops[i], ops[i+1])
                analysis['operation_flows'][flow] += 1
        
        # Analyze address patterns
        for i in range(len(path)-1):
            addr1 = path[i]['address']
            addr2 = path[i+1]['address']
            # Find matching segments
            for j in range(min(len(addr1), len(addr2))-3):
                if addr1[j:j+4] == addr2[j:j+4]:
                    analysis['address_patterns'][addr1[j:j+4]].append((addr1, addr2))
    
    return analysis

if __name__ == "__main__":
    # Start with master key (first address)
    master_key = CRYPTO_MAPPINGS[0][0]
    print(f"Starting path analysis from master key: {master_key}")
    
    # Map and analyze command paths
    paths = map_command_paths(master_key)
    analysis = analyze_path_patterns(paths)
    
    # Show different paths
    print("\nCommand Paths Found:")
    for i, path in enumerate(paths):
        print(f"\nPath {i+1}:")
        for j, node in enumerate(path):
            print(f"Step {j+1}:")
            print(f"Address: {node['address']}")
            print(f"Command: {node['command']}")
            if j < len(path)-1:
                print("↓")
        print("-" * 50)
    
    # Show pattern analysis
    print("\nPattern Analysis:")
    
    print("\nCommon Command Sequences:")
    for (cmd1, cmd2), count in sorted(analysis['common_sequences'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"\nSequence (appeared {count} times):")
        print(f"  {cmd1}")
        print(f"  ↓")
        print(f"  {cmd2}")
    
    print("\nCommon Operation Flows:")
    for (op1, op2), count in sorted(analysis['operation_flows'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"{op1} -> {op2}: {count} times")
    
    print("\nRepeating Address Patterns:")
    for pattern, occurrences in sorted(analysis['address_patterns'].items(), key=lambda x: len(x[1]), reverse=True)[:5]:
        print(f"\nPattern '{pattern}' appears in transitions:")
        for addr1, addr2 in occurrences[:3]:  # Show first 3 examples
            print(f"  {addr1} -> {addr2}") 