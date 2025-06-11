from typing import List, Dict, Callable
import numpy as np
from dataclasses import dataclass
import matplotlib.pyplot as plt

@dataclass
class KeyData:
    index: int
    value: int
    bit_count: int
    xor_diff: int = None

class HashAnalyzer:
    def __init__(self):
        self.known_keys = {
            66: 0x2832ed74f2b5e35ee,
            67: 0x730fc235c1942c1ae,
            120: 0x00b10f22572c497a836ea187f2e1fc23,
            130: 0x33e7665705359f04f28b88cf897c603c9
        }
        
    def count_bits(self, n: int) -> int:
        """Count number of set bits in integer"""
        return bin(n).count('1')
    
    def test_f_function(self, f: Callable[[int, int], int], start_n: int, end_n: int) -> List[KeyData]:
        """Test a candidate f(n) function over a range"""
        results = []
        prev_key = self.known_keys[start_n]
        
        for n in range(start_n + 1, end_n + 1):
            # Apply sequence rule: an = (an-1 << 1) + f(n)
            shifted = prev_key << 1
            f_result = f(n, prev_key)
            new_key = shifted + f_result
            
            # Store results
            key_data = KeyData(
                index=n,
                value=new_key,
                bit_count=self.count_bits(new_key)
            )
            
            if n in self.known_keys:
                key_data.xor_diff = new_key ^ self.known_keys[n]
            
            results.append(key_data)
            prev_key = new_key
            
        return results

    def analyze_growth_pattern(self, results: List[KeyData]) -> Dict:
        """Analyze bit growth and differences between consecutive keys"""
        analysis = {
            'bit_growth': [],
            'xor_diffs': [],
            'accuracy': []
        }
        
        for i in range(1, len(results)):
            prev = results[i-1]
            curr = results[i]
            
            # Analyze bit growth
            bit_diff = curr.bit_count - prev.bit_count
            analysis['bit_growth'].append(bit_diff)
            
            # Check accuracy against known keys
            if curr.xor_diff is not None:
                accuracy = 1.0 if curr.xor_diff == 0 else 0.0
                analysis['accuracy'].append((curr.index, accuracy))
            
            # Calculate XOR difference
            xor_diff = curr.value ^ prev.value
            analysis['xor_diffs'].append(xor_diff)
            
        return analysis

    def plot_results(self, analysis: Dict, f_name: str):
        """Generate visualization of analysis results"""
        plt.figure(figsize=(15, 10))
        
        # Plot bit growth
        plt.subplot(2, 1, 1)
        plt.plot(analysis['bit_growth'], label='Bit Growth')
        plt.title(f'Analysis of f(n) = {f_name}')
        plt.ylabel('Bit Difference')
        plt.legend()
        
        # Plot accuracy for known keys
        if analysis['accuracy']:
            indices, accuracies = zip(*analysis['accuracy'])
            plt.subplot(2, 1, 2)
            plt.scatter(indices, accuracies, c='red', label='Known Key Match')
            plt.ylabel('Accuracy (1=match)')
            plt.legend()
        
        plt.tight_layout()
        plt.savefig('output/hash_analysis.png')

def test_candidate_functions():
    analyzer = HashAnalyzer()
    
    # Test different f(n) candidates
    candidates = [
        # Simple scaling function
        (lambda n, prev: n * (2 ** (n % 10)),
         "n * 2^(n mod 10)"),
        
        # XOR with previous key
        (lambda n, prev: prev ^ n,
         "prev_key XOR n"),
        
        # Combined approach
        (lambda n, prev: (prev ^ n) + (n * (2 ** (n % 10))),
         "(prev_key XOR n) + n * 2^(n mod 10)")
    ]
    
    for f, name in candidates:
        # Test function from 66 to 68 (short range)
        results = analyzer.test_f_function(f, 66, 68)
        analysis = analyzer.analyze_growth_pattern(results)
        analyzer.plot_results(analysis, name)
        
        # Print detailed results
        print(f"\nTesting f(n) = {name}")
        for r in results:
            print(f"n={r.index}: {hex(r.value)} ({r.bit_count} bits)")
            if r.xor_diff is not None:
                print(f"XOR diff from known: {hex(r.xor_diff)}")
        print("-" * 80)

if __name__ == "__main__":
    test_candidate_functions() 