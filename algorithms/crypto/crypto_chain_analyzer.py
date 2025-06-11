from crypto_data import CRYPTO_MAPPINGS

def get_command_for_address(addr):
    """Helper function to get command for an address"""
    matches = [cmd for a, cmd in CRYPTO_MAPPINGS if a == addr]
    return matches[0] if matches else "Unknown Command"

def analyze_crypto_chains():
    # Initialize tracking structures
    chains = {}  # addr -> command chain
    connections = {}  # addr -> connected addresses
    crypto_ops = {'HASH', 'CIPHER', 'ENCRYPT', 'DECRYPT', 'KEY', 'VERIFY', 'SECURE'}
    command_map = {addr: cmd for addr, cmd in CRYPTO_MAPPINGS}
    
    # First pass: Build command chains
    for addr, cmd in CRYPTO_MAPPINGS:
        ops = cmd.split('_')
        crypto_sequence = []
        for op in ops:
            if op in crypto_ops:
                crypto_sequence.append(op)
        if crypto_sequence:
            chains[addr] = crypto_sequence
            
    # Second pass: Find connections between chains
    for addr1, chain1 in chains.items():
        connections[addr1] = []
        for addr2, chain2 in chains.items():
            if addr1 != addr2:
                # Check for overlapping operations
                if set(chain1) & set(chain2):
                    connections[addr1].append(addr2)
                    
    # Analyze and print results
    print("\n=== Cryptographic Chain Analysis ===\n")
    
    # 1. Find the longest crypto chains
    print("Longest Cryptographic Chains:")
    sorted_chains = sorted(chains.items(), key=lambda x: len(x[1]), reverse=True)
    for addr, chain in sorted_chains[:5]:
        print(f"\nAddress: {addr}")
        print(f"Command: {command_map[addr]}")
        print(f"Crypto Operations: {' -> '.join(chain)}")
        
    # 2. Find most connected chains
    print("\nMost Connected Chains:")
    sorted_connections = sorted(connections.items(), key=lambda x: len(x[1]), reverse=True)
    for addr, connected in sorted_connections[:5]:
        print(f"\nAddress: {addr}")
        print(f"Command: {command_map[addr]}")
        print(f"Connected to {len(connected)} other chains")
        print("Example connections:")
        for conn_addr in connected[:3]:
            print(f"  {conn_addr}: {command_map[conn_addr]}")
            
    # 3. Analyze operation patterns
    print("\nCrypto Operation Patterns:")
    patterns = {}
    for chain in chains.values():
        for i in range(len(chain)-1):
            pair = (chain[i], chain[i+1])
            patterns[pair] = patterns.get(pair, 0) + 1
            
    print("\nCommon Operation Sequences:")
    sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
    for (op1, op2), count in sorted_patterns[:10]:
        print(f"  {op1} -> {op2}: {count} occurrences")
        
    # 4. Find central nodes
    print("\nCentral Cryptographic Nodes:")
    centrality = {}
    for addr, chain in chains.items():
        score = len(chain) * len(connections[addr])
        centrality[addr] = score
        
    sorted_centrality = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
    for addr, score in sorted_centrality[:5]:
        print(f"\nAddress: {addr}")
        print(f"Command: {command_map[addr]}")
        print(f"Centrality Score: {score}")
        print(f"Crypto Operations: {' -> '.join(chains[addr])}")
        
    # 5. Identify potential encryption rounds
    print("\nPotential Encryption Rounds:")
    rounds = []
    for addr, chain in chains.items():
        if len(chain) >= 3 and chain[0] == chain[-1]:
            rounds.append((addr, chain))
            
    for addr, round_chain in rounds[:5]:
        print(f"\nAddress: {addr}")
        print(f"Command: {command_map[addr]}")
        print(f"Round: {' -> '.join(round_chain)}")
        
    # 6. Analyze operation frequencies
    print("\nOperation Frequencies:")
    op_freq = {}
    for chain in chains.values():
        for op in chain:
            op_freq[op] = op_freq.get(op, 0) + 1
            
    for op, freq in sorted(op_freq.items(), key=lambda x: x[1], reverse=True):
        print(f"  {op}: {freq} occurrences")
        
    # 7. Find key transformation patterns
    print("\nKey Transformation Patterns:")
    key_patterns = []
    for addr, chain in chains.items():
        if 'KEY' in chain:
            key_idx = chain.index('KEY')
            if key_idx < len(chain) - 1:
                key_patterns.append((addr, chain[key_idx:]))
                
    for addr, pattern in sorted(key_patterns, key=lambda x: len(x[1]), reverse=True)[:5]:
        print(f"\nAddress: {addr}")
        print(f"Command: {command_map[addr]}")
        print(f"Key Transform: {' -> '.join(pattern)}")

def main():
    analyze_crypto_chains()

if __name__ == "__main__":
    main() 