import subprocess
from typing import List, Dict
from hash_analyzer import HashAnalyzer
import json

class PatternAnalyzer:
    def __init__(self, rust_binary: str = "./target/release/puzzle_solver"):
        self.rust_binary = rust_binary
        self.hash_analyzer = HashAnalyzer()
        
    def analyze_bit_patterns(self, keys: List[str]) -> Dict:
        """Enhanced analysis using HashAnalyzer"""
        # Convert hex strings to integers
        key_values = [int(k, 16) for k in keys]
        
        # Test different f(n) candidates
        results = {}
        for n in range(len(key_values) - 1):
            # Test next key prediction
            predicted = self.predict_next_key([hex(k) for k in key_values[:n+1]])
            actual = key_values[n+1]
            
            results[n+1] = {
                'predicted': predicted,
                'actual': hex(actual),
                'match': predicted == hex(actual),
                'bit_diff': abs(len(bin(int(predicted, 16))) - len(bin(actual)))
            }
            
        return results
    
    def predict_next_key(self, previous_keys: List[str]) -> str:
        """Predict next key using best performing f(n)"""
        if not previous_keys:
            return hex(1)  # a1 = 0x1
            
        prev_key = int(previous_keys[-1], 16)
        n = len(previous_keys) + 1
        
        # Use combined f(n) approach
        f_result = (prev_key ^ n) + (n * (2 ** (n % 10)))
        next_key = (prev_key << 1) + f_result
        
        return hex(next_key)

    def _parse_rust_output(self, output: str) -> Dict:
        """Parse Rust binary output with enhanced metrics"""
        try:
            data = json.loads(output)
            return {
                "bit_heatmap": data.get("bit_patterns", {}),
                "xor_diff": data.get("xor_differences", []),
                "growth_factors": data.get("growth_metrics", [])
            }
        except json.JSONDecodeError:
            return {
                "bit_heatmap": {},
                "xor_diff": [],
                "growth_factors": []
            } 