from bitcoinlib.keys import Key

class BitcoinAddressAnalyzer:
    def __init__(self):
        self.ADDRESS_MARKERS = {
            'BEGIN': ['1'],
            'GATEWAY': ['2', '3'],
            'TRANSFER': ['A', 'B'],
            'ZERO': ['0'],
            'MEMORY': ['M', 'N'],
            'PROCESS': ['P', 'Q'],
            'VERIFY': ['V', 'W'],
            'SECURE': ['S', 'T'],
            'NETWORK': ['N', 'O'],
            'BUFFER': ['B', 'C'],
            'CHAIN': ['C', 'D'],
            'KEY': ['K', 'L']
        }
        self.compressed_patterns = {}
        self.uncompressed_patterns = {}

    def analyze_address_components(self, private_key_hex, compressed_addr, uncompressed_addr):
        """Compare components between compressed and uncompressed addresses"""
        key_int = int(private_key_hex, 16)
        
        # Get components from both addresses
        compressed_components = self.get_address_components(compressed_addr)
        uncompressed_components = self.get_address_components(uncompressed_addr)
        
        # Track component patterns
        comp_pattern = '|'.join(sorted(compressed_components))
        uncomp_pattern = '|'.join(sorted(uncompressed_components))
        
        # Store patterns for analysis
        if comp_pattern not in self.compressed_patterns:
            self.compressed_patterns[comp_pattern] = []
        if uncomp_pattern not in self.uncompressed_patterns:
            self.uncompressed_patterns[uncomp_pattern] = []
            
        self.compressed_patterns[comp_pattern].append(compressed_addr)
        self.uncompressed_patterns[uncomp_pattern].append(uncompressed_addr)
        
        return {
            'key_hex': private_key_hex,
            'key_int': key_int,
            'compressed': {
                'address': compressed_addr,
                'components': compressed_components,
                'pattern': comp_pattern
            },
            'uncompressed': {
                'address': uncompressed_addr,
                'components': uncompressed_components,
                'pattern': uncomp_pattern
            },
            'differences': list(set(uncompressed_components) - set(compressed_components))
        }

    def get_address_components(self, address):
        """Extract components from a Bitcoin address"""
        components = []
        i = 0
        while i < len(address):
            for component, markers in self.ADDRESS_MARKERS.items():
                for marker in markers:
                    if i < len(address) and address[i:].startswith(marker):
                        if component not in components:
                            components.append(component)
                        break
            i += 1
        return sorted(components)

    def format_comparison_output(self, analysis):
        """Format the component comparison output"""
        return (
            f"Key: {analysis['key_hex']}\n"
            f"Compressed Address: {analysis['compressed']['address']}\n"
            f"  Components: {analysis['compressed']['components']}\n"
            f"  Pattern: {analysis['compressed']['pattern']}\n"
            f"Uncompressed Address: {analysis['uncompressed']['address']}\n"
            f"  Components: {analysis['uncompressed']['components']}\n"
            f"  Pattern: {analysis['uncompressed']['pattern']}\n"
            f"Unique to Uncompressed: {analysis['differences'] if analysis['differences'] else 'None'}\n"
        )

    def summarize_component_patterns(self):
        """Summarize component pattern differences"""
        summary = "\nComponent Pattern Analysis:\n\n"
        
        summary += "Compressed Address Patterns:\n"
        for pattern, addresses in self.compressed_patterns.items():
            summary += f"  Pattern '{pattern}' found in {len(addresses)} addresses\n"
        
        summary += "\nUncompressed Address Patterns:\n"
        for pattern, addresses in self.uncompressed_patterns.items():
            summary += f"  Pattern '{pattern}' found in {len(addresses)} addresses\n"
        
        # Find unique patterns
        comp_set = set(self.compressed_patterns.keys())
        uncomp_set = set(self.uncompressed_patterns.keys())
        
        summary += "\nUnique to Uncompressed:\n"
        for pattern in (uncomp_set - comp_set):
            summary += f"  {pattern}\n"
            
        return summary

def main():
    analyzer = BitcoinAddressAnalyzer()
    
    # Extended test data from life2.py
    test_data = [
        ("0000000000000000000000000000000000000000000000000000000000000001", 
         "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH", 
         "1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm"),
        ("0000000000000000000000000000000000000000000000000000000000000003",
         "1CUNEBjYrCn2y1SdiUMohaKUi4wpP326Lb",
         "1NZUP3JAc9JkmbvmoTv7nVgZGtyJjirKV1"),
        ("0000000000000000000000000000000000000000000000000000000000000007", 
         "19ZewH8Kk1PDbSNdJ97FP4EiCjTRaZMZQA", 
         "1BYbgHpSKQCtMrQfwN6b6n5S718EJkEJ41"),
        ("0000000000000000000000000000000000000000000000000000000000000008", 
         "1EhqbyUMvvs7BfL8goY6qcPbD6YKfPqb7e", 
         "1JMcEcKXQ7xA7JLAMPsBmHz68bzugYtdrv"),
        ("0000000000000000000000000000000000000000000000000000000000000015", 
         "1E6NuFjCi27W5zoXg8TRdcSRq84zJeBW3k", 
         "19vxtDbLMNasSpbAEZd7va5Qge6d2zYWbp"),
        ("0000000000000000000000000000000000000000000000000000000000000031", 
         "1PitScNLyp2HCygzadCh7FveTnfmpPbfp8", 
         "18JVE1MSS7a2NEhtHJkxhwgvT4hLQYBw3w"),
        ("000000000000000000000000000000000000000000000000000000000000004c", 
         "1McVt1vMtCC7yn5b9wgX1833yCcLXzueeC", 
         "1ESJVfV5UVERkWgVNfMjsLwJT88yMJHi8R"),
        ("00000000000000000000000000000000000000000000000000000000000000e0", 
         "1M92tSqNmQLYw33fuBvjmeadirh1ysMBxK", 
         "1HFvQh3dVFPae3JaFjL5Mpua9Zbg9Y6FrK"),
        ("00000000000000000000000000000000000000000000000000000000000001d3", 
         "1CQFwcjw1dwhtkVWBttNLDtqL7ivBonGPV", 
         "1CpudzGLUutTRM8wFu2BRQJNo11CzpMmHH"),
        ("0000000000000000000000000000000000000000000000000000000000000202", 
         "1LeBZP5QCwwgXRtmVUvTVrraqPUokyLHqe", 
         "1ofbgenBbkCcmQyRK7XzHnhFHULAdNsBu"),
        ("0000000000000000000000000000000000000000000000000000000000000483", 
         "1PgQVLmst3Z314JrQn5TNiys8Hc38TcXJu", 
         "1J3PLTqmUnBX3CMxxCap3pFgzPGgN5btKf"),
        ("0000000000000000000000000000000000000000000000000000000000000a7b", 
         "1DBaumZxUkM4qMQRt2LVWyFJq5kDtSZQot", 
         "1AWHYKPNdiu33TFCve7k7QiKuWLpiyzBby"),
        ("0000000000000000000000000000000000000000000000000000000000001460", 
         "1Pie8JkxBT6MGPz9Nvi3fsPkr2D8q3GBc1", 
         "1DUCXnzF7hA7fLDToQEJjQaZ2rCVHonNfF"),
        ("0000000000000000000000000000000000000000000000000000000000002930", 
         "1ErZWg5cFCe4Vw5BzgfzB74VNLaXEiEkhk", 
         "1HpTkLHDZ8zcqwkeNWiFfHBouiZvP9gj4Z"),
        ("00000000000000000000000000000000000000000000000000000000000068f3", 
         "1QCbW9HWnwQWiQqVo5exhAnmfqKRrCRsvW", 
         "17HsDU9MSyoYCrkDkPg2gz5ZwdX2kWLvBG"),
        ("000000000000000000000000000000000000000000000000000000000000c936", 
         "1BDyrQ6WoF8VN3g9SAS1iKZcPzFfnDVieY", 
         "136MiPt1obHE3LaR95u4JcM9KgnxzSDa8m"),
        ("000000000000000000000000000000000000000000000000000000000001764f", 
         "1HduPEXZRdG26SUT5Yk83mLkPyjnZuJ7Bm", 
         "1MWDkTaDJiSh6sXWeoiwU5ZHmosyqmMnEJ"),
        ("000000000000000000000000000000000000000000000000000000000003080d", 
         "1GnNTmTVLZiqQfLbAdp9DVdicEnB5GoERE", 
         "159KUhWBS8qVZwbX7ZPzwQt6mNppZcN3WX"),
        ("000000000000000000000000000000000000000000000000000000000005749f", 
         "1NWmZRpHH4XSPwsW6dsS3nrNWfL1yrJj4w", 
         "1BhBok4wXceco3cxfqA8e6hZUnjikD6QR4"),
        ("00000000000000000000000000000000000000000000000000000000000d2c55", 
         "1HsMJxNiV7TLxmoF6uJNkydxPFDog4NQum", 
         "1GVzEdhzLtcNruKtgSVNEn31BpXsw6nVxN")
    ]
    
    print("# Extended Component Analysis: Compressed vs Uncompressed Addresses\n")
    
    for key, compressed, uncompressed in test_data:
        analysis = analyzer.analyze_address_components(key, compressed, uncompressed)
        print(analyzer.format_comparison_output(analysis))
    
    print(analyzer.summarize_component_patterns())

if __name__ == "__main__":
    main()