from crypto_data import CRYPTO_MAPPINGS
from collections import defaultdict

class CryptoVisualizer:
    def __init__(self):
        self.commands = {}  # command -> address mapping
        self.patterns = defaultdict(list)  # operation -> following operations
        self.crypto_chains = []  # sequences of crypto operations
        self.address_links = defaultdict(set)  # address -> related addresses
        
    def analyze_patterns(self):
        """Analyze cryptographic patterns in the command set"""
        # Load all commands and addresses
        for addr, cmd in CRYPTO_MAPPINGS:
            self.commands[cmd] = addr
            ops = cmd.split('_')
            
            # Track operation patterns
            for i in range(len(ops)-1):
                self.patterns[ops[i]].append(ops[i+1])
                
            # Find crypto operations
            crypto_ops = [op for op in ops if op in {'HASH', 'CIPHER', 'ENCRYPT', 'DECRYPT', 'KEY', 'VERIFY', 'SECURE'}]
            if len(crypto_ops) > 0:
                self.crypto_chains.append((addr, crypto_ops))
                
            # Analyze address patterns
            addr_num = addr[1:-1]  # Remove the 1 prefix and checksum
            for other_addr, other_cmd in CRYPTO_MAPPINGS:
                if addr != other_addr:
                    other_num = other_addr[1:-1]
                    # Check for address relationships
                    if any(n in other_num for n in addr_num):
                        self.address_links[addr].add(other_addr)

    def find_crypto_sequences(self):
        """Find significant cryptographic operation sequences"""
        sequences = []
        crypto_ops = {'HASH', 'CIPHER', 'ENCRYPT', 'DECRYPT', 'KEY', 'VERIFY', 'SECURE'}
        
        for cmd, addr in self.commands.items():
            ops = cmd.split('_')
            crypto_seq = []
            for op in ops:
                if op in crypto_ops:
                    crypto_seq.append(op)
            if len(crypto_seq) >= 2:  # Only track significant sequences
                sequences.append((addr, crypto_seq))
        
        return sequences

    def analyze_address_patterns(self):
        """Analyze patterns in Bitcoin addresses"""
        patterns = defaultdict(list)
        
        for addr in self.commands.values():
            # Extract key parts of address (remove 1 prefix and checksum)
            key_part = addr[1:-1]
            
            # Look for repeating patterns
            for i in range(2, len(key_part)-1):
                pattern = key_part[i:i+2]
                if pattern.isalnum():  # Only consider alphanumeric patterns
                    patterns[pattern].append(addr)
                    
        return patterns

    def visualize_system(self):
        """Generate a visualization of the cryptographic system"""
        self.analyze_patterns()
        
        print("\n=== Cryptographic System Analysis ===\n")
        
        print("Core Cryptographic Patterns:")
        for op in ['HASH', 'CIPHER', 'ENCRYPT', 'DECRYPT', 'KEY', 'VERIFY', 'SECURE']:
            if op in self.patterns:
                print(f"\n{op} leads to:")
                following_ops = defaultdict(int)
                for next_op in self.patterns[op]:
                    following_ops[next_op] += 1
                for next_op, count in sorted(following_ops.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"  {next_op}: {count} times")
        
        print("\nSignificant Crypto Sequences:")
        sequences = self.find_crypto_sequences()
        for addr, seq in sequences[:10]:  # Show top 10
            print(f"  {addr}: {' -> '.join(seq)}")
            
        print("\nAddress Pattern Analysis:")
        addr_patterns = self.analyze_address_patterns()
        significant_patterns = {k: v for k, v in addr_patterns.items() if len(v) > 3}
        print(f"Found {len(significant_patterns)} significant address patterns")
        for pattern, addrs in sorted(significant_patterns.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            print(f"\nPattern '{pattern}' appears in {len(addrs)} addresses:")
            for addr in addrs[:3]:  # Show first 3 examples
                print(f"  {addr}")
                
        print("\nCommand Network Structure:")
        crypto_ops_count = defaultdict(int)
        for cmd in self.commands:
            ops = cmd.split('_')
            for op in ops:
                if op in {'HASH', 'CIPHER', 'ENCRYPT', 'DECRYPT', 'KEY', 'VERIFY', 'SECURE'}:
                    crypto_ops_count[op] += 1
        
        print("\nCrypto Operation Distribution:")
        for op, count in sorted(crypto_ops_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  {op}: {count} occurrences")
            
        print("\nHighly Connected Addresses:")
        for addr, links in sorted(self.address_links.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            print(f"\n{addr} connects to {len(links)} other addresses")
            cmd = [c for c, a in CRYPTO_MAPPINGS if a == addr][0]
            print(f"Command: {cmd}")
            print("Connected to:")
            for linked_addr in list(links)[:3]:  # Show first 3 connections
                linked_cmd = [c for c, a in CRYPTO_MAPPINGS if a == linked_addr][0]
                print(f"  {linked_addr}: {linked_cmd}")

def main():
    visualizer = CryptoVisualizer()
    visualizer.visualize_system()

if __name__ == "__main__":
    main() 