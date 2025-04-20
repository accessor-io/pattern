from crypto_data import CRYPTO_MAPPINGS
from collections import defaultdict
import re

class NumberPatternAnalyzer:
    def __init__(self):
        self.number_sequences = []
        self.address_numbers = {}
        self.command_numbers = defaultdict(list)
        self.number_chains = []
        
    def extract_numbers(self, text):
        """Extract all numbers from text"""
        return re.findall(r'\d+', text)
        
    def analyze_address_numbers(self):
        """Analyze numerical patterns in Bitcoin addresses"""
        for addr, cmd in CRYPTO_MAPPINGS:
            # Extract numbers from address (excluding prefix)
            addr_nums = self.extract_numbers(addr[1:])
            if addr_nums:
                self.address_numbers[addr] = addr_nums
                
            # Extract numbers from command
            cmd_nums = self.extract_numbers(cmd)
            if cmd_nums:
                self.command_numbers[addr] = cmd_nums
                
            # Look for number chains in command
            parts = cmd.split('_')
            number_sequence = []
            for part in parts:
                if part.isdigit():
                    number_sequence.append(int(part))
            if number_sequence:
                self.number_chains.append((addr, number_sequence))
                
    def find_number_patterns(self):
        """Find patterns in number sequences"""
        patterns = defaultdict(list)
        
        # Look for arithmetic sequences
        for addr, nums in self.number_chains:
            if len(nums) >= 2:
                diffs = [nums[i+1] - nums[i] for i in range(len(nums)-1)]
                if len(set(diffs)) == 1:  # Constant difference = arithmetic sequence
                    patterns['arithmetic'].append((addr, nums, diffs[0]))
                    
        # Look for geometric sequences
        for addr, nums in self.number_chains:
            if len(nums) >= 2:
                ratios = []
                for i in range(len(nums)-1):
                    if nums[i] != 0:
                        ratio = nums[i+1] / nums[i]
                        ratios.append(ratio)
                if len(ratios) > 0 and len(set(ratios)) == 1:
                    patterns['geometric'].append((addr, nums, ratios[0]))
                    
        return patterns
        
    def analyze_number_relationships(self):
        """Analyze relationships between numbers in commands and addresses"""
        relationships = []
        
        for addr in self.command_numbers:
            cmd_nums = self.command_numbers[addr]
            addr_nums = self.address_numbers.get(addr, [])
            
            # Look for numbers that appear in both command and address
            common_nums = set(cmd_nums) & set(addr_nums)
            if common_nums:
                relationships.append((addr, list(common_nums)))
                
        return relationships
        
    def find_number_transformations(self):
        """Find potential number transformation patterns"""
        transformations = []
        
        for addr, cmd in CRYPTO_MAPPINGS:
            parts = cmd.split('_')
            for i in range(len(parts)-1):
                if parts[i].isdigit() and parts[i+1].isdigit():
                    num1 = int(parts[i])
                    num2 = int(parts[i+1])
                    # Look for mathematical relationships
                    if num2 == num1 * 2:
                        transformations.append((addr, 'double', num1, num2))
                    elif num2 == num1 + 1:
                        transformations.append((addr, 'increment', num1, num2))
                    elif num2 == num1 * num1:
                        transformations.append((addr, 'square', num1, num2))
                        
        return transformations
        
    def analyze_crypto_numbers(self):
        """Analyze numbers in crypto operations"""
        self.analyze_address_numbers()
        
        print("\n=== Cryptographic Number Analysis ===\n")
        
        # 1. Number Sequences in Commands
        print("Number Sequences in Commands:")
        for addr, sequence in self.number_chains[:10]:
            cmd = [c for a, c in CRYPTO_MAPPINGS if a == addr][0]
            print(f"\nAddress: {addr}")
            print(f"Command: {cmd}")
            print(f"Number Sequence: {sequence}")
            
        # 2. Number Patterns
        patterns = self.find_number_patterns()
        print("\nArithmetic Sequences Found:")
        for addr, nums, diff in patterns.get('arithmetic', []):
            cmd = [c for a, c in CRYPTO_MAPPINGS if a == addr][0]
            print(f"\nAddress: {addr}")
            print(f"Command: {cmd}")
            print(f"Sequence: {nums} (difference: {diff})")
            
        print("\nGeometric Sequences Found:")
        for addr, nums, ratio in patterns.get('geometric', []):
            cmd = [c for a, c in CRYPTO_MAPPINGS if a == addr][0]
            print(f"\nAddress: {addr}")
            print(f"Command: {cmd}")
            print(f"Sequence: {nums} (ratio: {ratio})")
            
        # 3. Number Relationships
        print("\nNumber Relationships (Command <-> Address):")
        relationships = self.analyze_number_relationships()
        for addr, common_nums in relationships[:10]:
            cmd = [c for a, c in CRYPTO_MAPPINGS if a == addr][0]
            print(f"\nAddress: {addr}")
            print(f"Command: {cmd}")
            print(f"Common Numbers: {common_nums}")
            
        # 4. Number Transformations
        print("\nNumber Transformations Found:")
        transformations = self.find_number_transformations()
        for addr, trans_type, num1, num2 in transformations:
            cmd = [c for a, c in CRYPTO_MAPPINGS if a == addr][0]
            print(f"\nAddress: {addr}")
            print(f"Command: {cmd}")
            print(f"Transformation: {num1} -> {num2} ({trans_type})")
            
        # 5. Statistical Analysis
        print("\nNumber Statistics:")
        all_numbers = []
        for nums in self.command_numbers.values():
            all_numbers.extend(map(int, nums))
            
        if all_numbers:
            print(f"Total numbers found: {len(all_numbers)}")
            print(f"Unique numbers: {len(set(all_numbers))}")
            print(f"Most common numbers: {sorted(set(all_numbers))[:10]}")
            print(f"Number range: {min(all_numbers)} to {max(all_numbers)}")

def main():
    analyzer = NumberPatternAnalyzer()
    analyzer.analyze_crypto_numbers()

if __name__ == "__main__":
    main() 