from bitcoin import *
import binascii

class BitcoinProtocolAnalyzer:
    def __init__(self):
        self.protocol_mappings = {}
        self.pattern_cache = {}
        
    def verify_key_to_address(self, private_key_hex):
        """Verify private key to address generation"""
        try:
            # Convert hex to private key
            priv = int(private_key_hex, 16)
            
            # Generate public key
            pub = privtopub(priv)
            pub_compressed = compress(pub)
            
            # Generate addresses
            addr_uncompressed = pubtoaddr(pub)
            addr_compressed = pubtoaddr(pub_compressed)
            
            return {
                'private_key': private_key_hex,
                'compressed': addr_compressed,
                'uncompressed': addr_uncompressed
            }
        except Exception as e:
            return f"Error: {str(e)}"

    def analyze_protocol_pattern(self, address):
        """Analyze protocol mapping pattern in address"""
        components = []
        current_component = ''
        
        # Basic protocol components
        PROTOCOL_MARKERS = {
            'BEGIN': ['B', 'Bg'],
            'GATEWAY': ['G', 'Gw'],
            'TRANSFER': ['T', 'Tr'],
            'ZERO': ['Z', 'Z0'],
            'MEMORY': ['M', 'Mem'],
            'PROCESS': ['P', 'Pr'],
            'VERIFY': ['V', 'Vr'],
            'SECURE': ['S', 'Sc'],
            'NETWORK': ['N', 'Nt'],
            'BUFFER': ['B', 'Bf'],
            'CHAIN': ['C', 'Ch'],
            'KEY': ['K', 'Ky']
        }
        
        # Analyze character sequences
        i = 0
        while i < len(address):
            if address[i] in '123456789':
                # Skip version byte
                i += 1
                continue
                
            # Look for protocol markers
            for protocol, markers in PROTOCOL_MARKERS.items():
                for marker in markers:
                    if address[i:i+len(marker)] == marker:
                        if current_component:
                            components.append(current_component)
                        current_component = protocol
                        i += len(marker)
                        break
            i += 1
            
        if current_component:
            components.append(current_component)
            
        return components

    def analyze_private_key_pattern(self, private_key_hex):
        """Analyze pattern in private key generation"""
        key_int = int(private_key_hex, 16)
        binary = bin(key_int)[2:].zfill(256)  # Full 256-bit representation
        
        patterns = {
            'leading_zeros': len(binary) - len(binary.lstrip('0')),
            'total_ones': binary.count('1'),
            'byte_pattern': [int(binary[i:i+8], 2) for i in range(0, 256, 8)],
            'special_sequences': []
        }
        
        return patterns

    def verify_dataset(self, dataset):
        """Verify and analyze the complete dataset"""
        results = []
        
        for entry in dataset:
            index = entry[0]
            priv_key = entry[1]
            compressed = entry[2]
            uncompressed = entry[3]
            
            # Verify addresses
            verification = self.verify_key_to_address(priv_key)
            
            # Analyze protocol patterns
            protocol_pattern = self.analyze_protocol_pattern(compressed)
            
            # Analyze private key patterns
            key_pattern = self.analyze_private_key_pattern(priv_key)
            
            results.append({
                'index': index,
                'verification': verification,
                'protocol_pattern': protocol_pattern,
                'key_pattern': key_pattern,
                'matches_original': {
                    'compressed': verification['compressed'] == compressed,
                    'uncompressed': verification['uncompressed'] == uncompressed
                }
            })
            
        return results

# Example usage
analyzer = BitcoinProtocolAnalyzer()

# Test dataset (first few entries)
test_data = [
    [0, "0000000000000000000000000000000000000000000000000000000000000001", 
     "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH", "1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm"],
    [1, "0000000000000000000000000000000000000000000000000000000000000003",
     "1CUNEBjYrCn2y1SdiUMohaKUi4wpP326Lb", "1NZUP3JAc9JkmbvmoTv7nVgZGtyJjirKV1"]
]

# Analyze patterns
def analyze_full_dataset():
    results = analyzer.verify_dataset(test_data)
    
    print("\nProtocol Pattern Analysis:")
    for result in results:
        print(f"\nIndex: {result['index']}")
        print(f"Protocol Components: {result['protocol_pattern']}")
        print(f"Address Verification: {result['matches_original']}")
        print(f"Key Patterns:")
        print(f"- Leading zeros: {result['key_pattern']['leading_zeros']}")
        print(f"- Total ones: {result['key_pattern']['total_ones']}")
        
    return results

# Additional pattern analysis
def analyze_protocol_relationships():
    """Analyze relationships between protocol mappings"""
    all_results = analyze_full_dataset()
    
    # Analyze patterns between consecutive addresses
    for i in range(len(all_results) - 1):
        current = all_results[i]
        next_result = all_results[i + 1]
        
        print(f"\nPattern Evolution {i} → {i+1}:")
        print(f"Protocol Change: {current['protocol_pattern']} → {next_result['protocol_pattern']}")
        
        # Analyze binary differences in private keys
        current_key = int(test_data[i][1], 16)
        next_key = int(test_data[i+1][1], 16)
        key_diff = bin(current_key ^ next_key)[2:].zfill(256)
        
        print(f"Key Binary Difference Pattern:")
        print(f"Changed bits: {key_diff.count('1')}")

if __name__ == "__main__":
    print("Starting Protocol Analysis...")
    analyze_protocol_relationships()
    print("Protocol Analysis Complete.")    
    