"""
Comprehensive Analysis for Position 67
Using both complete analysis and hex file data
"""

import math
import logging
import json
import os
import subprocess
from typing import Set, List, Dict, Optional

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Position67Analyzer:
    def __init__(self):
        self.hex_file = "../data/32bHex.txt"
        self.known_values = {}
        
        # Load values from hex file
        with open(self.hex_file, 'r') as f:
            for i, line in enumerate(f.readlines(), 1):
                hex_str = line.strip()
                if hex_str:
                    self.known_values[i] = int(hex_str, 16)
                    
        # Add known values
        self.known_values.update({
            66: 0x2832ed74f2b5e35ee,  # Our target's predecessor
            70: 0x349b84b6431a6c4ef1,  # Next known value
            75: 0x4c5ce114686a1336e07,
            80: 0xea1a5c66dcc11b5ad180,
            85: 0x11720c4f018d51b8cebba8,
            90: 0x2ce00bb2136a445c71e85bf,
            95: 0x527a792b183c7f64a0e8b1f4,
            100: 0xaf55fc59c335c8ec67ed24826,
            105: 0x16f14fc2054cd87ee6396b33df3
        })
        
        # Create output directories
        os.makedirs('analysis_67', exist_ok=True)
        os.makedirs('analysis_67/patterns', exist_ok=True)
        os.makedirs('analysis_67/candidates', exist_ok=True)
        
    def save_candidates(self, candidates: Set[int], batch_num: int) -> None:
        """Save a batch of candidates and verify Bitcoin address"""
        # Save candidates
        filename = f'analysis_67/candidates/batch_{batch_num}.json'
        with open(filename, 'w') as f:
            hex_candidates = [hex(c) for c in candidates]
            json.dump(hex_candidates, f)
        logging.info(f"Saved {len(candidates)} candidates to {filename}")
        
        # Verify candidates
        try:
            subprocess.run(['python3', 'verify_bitcoin.py', filename], check=True)
        except subprocess.CalledProcessError:
            logging.warning(f"Bitcoin verification failed for batch {batch_num}")
            
    def save_progress(self, current: int, total: int) -> None:
        """Save current progress"""
        with open('analysis_67/progress.json', 'w') as f:
            json.dump({
                'current': current,
                'total': total,
                'percentage': (current/total) * 100
            }, f)
            
    def analyze_sequence_properties(self) -> Dict:
        """Analyze overall sequence properties"""
        properties = {
            'growth_rates': [],
            'bit_changes': [],
            'hamming_weights': [],
            'pattern_cycles': []
        }
        
        # Analyze each consecutive pair
        positions = sorted(self.known_values.keys())
        for i in range(len(positions)-1):
            pos1, pos2 = positions[i], positions[i+1]
            val1, val2 = self.known_values[pos1], self.known_values[pos2]
            
            # Growth rate
            growth = math.log2(val2) - math.log2(val1)
            properties['growth_rates'].append({
                'from_pos': pos1,
                'to_pos': pos2,
                'rate': growth / (pos2 - pos1)
            })
            
            # Bit changes
            bin1 = format(val1, 'b').zfill(256)
            bin2 = format(val2, 'b').zfill(256)
            changes = sum(1 for i in range(256) if bin1[i] != bin2[i])
            properties['bit_changes'].append({
                'from_pos': pos1,
                'to_pos': pos2,
                'changes': changes,
                'ratio': changes/256
            })
            
            # Hamming weights
            hw1 = bin1.count('1')
            hw2 = bin2.count('1')
            properties['hamming_weights'].append({
                'position': pos1,
                'weight': hw1
            })
            if i == len(positions)-2:  # Add last position
                properties['hamming_weights'].append({
                    'position': pos2,
                    'weight': hw2
                })
                
            # Pattern cycles (looking at 8-bit blocks)
            bytes1 = [bin1[i:i+8] for i in range(0, 256, 8)]
            bytes2 = [bin2[i:i+8] for i in range(0, 256, 8)]
            pattern = []
            for j in range(len(bytes1)):
                if bytes1[j] != bytes2[j]:
                    pattern.append(j)
            properties['pattern_cycles'].append({
                'from_pos': pos1,
                'to_pos': pos2,
                'changed_bytes': pattern,
                'total_changes': len(pattern)
            })
                
        # Save analysis
        with open('analysis_67/sequence_properties.json', 'w') as f:
            json.dump(properties, f, indent=2)
            
        return properties
        
    def analyze_bit_patterns(self) -> Dict:
        """Analyze bit patterns between positions 66 and 70"""
        val66 = self.known_values[66]
        val70 = self.known_values[70]
        
        bin66 = format(val66, 'b').zfill(256)
        bin70 = format(val70, 'b').zfill(256)
        
        # Analyze changes
        changes = []
        patterns = []
        current_pattern = []
        
        for i in range(256):
            if bin66[i] != bin70[i]:
                changes.append(i)
                current_pattern.append(1)
            else:
                current_pattern.append(0)
                
            if len(current_pattern) == 8:
                patterns.append(current_pattern)
                current_pattern = []
                
        # Analyze byte-level changes
        bytes66 = [bin66[i:i+8] for i in range(0, 256, 8)]
        bytes70 = [bin70[i:i+8] for i in range(0, 256, 8)]
        
        byte_changes = []
        for i in range(32):
            if bytes66[i] != bytes70[i]:
                byte_changes.append({
                    'position': i,
                    'from': bytes66[i],
                    'to': bytes70[i],
                    'changes': sum(1 for j in range(8) if bytes66[i][j] != bytes70[i][j])
                })
                
        analysis = {
            'bit_changes': {
                'positions': changes,
                'total': len(changes),
                'ratio': len(changes)/256
            },
            'byte_changes': {
                'changes': byte_changes,
                'total': len(byte_changes),
                'ratio': len(byte_changes)/32
            },
            'patterns': patterns
        }
        
        # Save analysis
        with open('analysis_67/bit_patterns.json', 'w') as f:
            json.dump(analysis, f, indent=2)
            
        return analysis
        
    def analyze_constraints(self) -> Dict:
        """Analyze constraints for position 67"""
        # From sequence analysis
        properties = self.analyze_sequence_properties()
        
        # Calculate average growth rate
        avg_growth = sum(p['rate'] for p in properties['growth_rates']) / len(properties['growth_rates'])
        std_growth = math.sqrt(sum((p['rate'] - avg_growth)**2 for p in properties['growth_rates']) / len(properties['growth_rates']))
        
        # Calculate average bit changes
        avg_changes = sum(p['ratio'] for p in properties['bit_changes']) / len(properties['bit_changes'])
        std_changes = math.sqrt(sum((p['ratio'] - avg_changes)**2 for p in properties['bit_changes']) / len(properties['bit_changes']))
        
        constraints = {
            'growth_rate': {
                'min': max(1.2, avg_growth - 2*std_growth),
                'max': min(2.0, avg_growth + 2*std_growth),
                'avg': avg_growth,
                'std': std_growth
            },
            'bit_changes': {
                'min': max(0.25, avg_changes - 2*std_changes),
                'max': min(0.75, avg_changes + 2*std_changes),
                'avg': avg_changes,
                'std': std_changes
            },
            'hamming_weight': {
                'min': min(hw['weight'] for hw in properties['hamming_weights']),
                'max': max(hw['weight'] for hw in properties['hamming_weights']),
                'expected': sum(hw['weight'] for hw in properties['hamming_weights']) / len(properties['hamming_weights'])
            },
            'byte_changes': {
                'min': min(p['total_changes'] for p in properties['pattern_cycles']),
                'max': max(p['total_changes'] for p in properties['pattern_cycles']),
                'expected': sum(p['total_changes'] for p in properties['pattern_cycles']) / len(properties['pattern_cycles'])
            }
        }
        
        # Save constraints
        with open('analysis_67/constraints.json', 'w') as f:
            json.dump(constraints, f, indent=2)
            
        return constraints
        
    def generate_candidates(self) -> None:
        """Generate candidate values for position 67"""
        patterns = self.analyze_bit_patterns()
        constraints = self.analyze_constraints()
        
        # Expected changes for position 67 (1/4 way between 66 and 70)
        expected_changes = int(patterns['bit_changes']['total'] * 0.25)
        logging.info(f"Expecting {expected_changes} bit changes")
        
        # Generate candidates
        bin66 = format(self.known_values[66], 'b').zfill(256)
        batch_size = 1000000
        batch_num = 0
        candidates = set()
        
        def generate_combinations(base_value: str, changes_needed: int,
                                positions: List[int], current_pos: int = 0,
                                current_value: str = None):
            nonlocal candidates, batch_num
            
            if current_value is None:
                current_value = base_value
                
            if changes_needed == 0:
                # Validate candidate meets basic constraints
                candidate = int(current_value, 2)
                if self.validate_basic_constraints(candidate, constraints):
                    candidates.add(candidate)
                    if len(candidates) >= batch_size:
                        self.save_candidates(candidates, batch_num)
                        batch_num += 1
                        candidates = set()
                return
                
            if current_pos >= len(positions) or changes_needed > len(positions) - current_pos:
                return
                
            # Save progress
            self.save_progress(current_pos, len(positions))
            
            # Don't change this position
            generate_combinations(base_value, changes_needed,
                               positions, current_pos + 1, current_value)
                               
            # Change this position
            new_value = (current_value[:positions[current_pos]] +
                        ('1' if current_value[positions[current_pos]] == '0' else '0') +
                        current_value[positions[current_pos]+1:])
            generate_combinations(base_value, changes_needed - 1,
                               positions, current_pos + 1, new_value)
                               
        # Generate combinations
        generate_combinations(bin66, expected_changes, patterns['bit_changes']['positions'])
        
        # Save remaining candidates
        if candidates:
            self.save_candidates(candidates, batch_num)
            
    def validate_basic_constraints(self, value: int, constraints: Dict) -> bool:
        """Validate a value meets basic constraints"""
        bin_val = format(value, 'b').zfill(256)
        
        # Check Hamming weight
        hw = bin_val.count('1')
        if not (constraints['hamming_weight']['min'] <= hw <= constraints['hamming_weight']['max']):
            return False
            
        # Check growth rate from position 66
        growth = math.log2(value) - math.log2(self.known_values[66])
        if not (constraints['growth_rate']['min'] <= growth <= constraints['growth_rate']['max']):
            return False
            
        return True
        
    def validate_candidate(self, value: int) -> bool:
        """Validate a candidate meets all requirements"""
        bin_val = format(value, 'b').zfill(256)
        bin66 = format(self.known_values[66], 'b').zfill(256)
        bin70 = format(self.known_values[70], 'b').zfill(256)
        
        constraints = self.analyze_constraints()
        
        # Check bit changes from 66
        changes66 = sum(1 for i in range(256) if bin_val[i] != bin66[i])
        if not (constraints['bit_changes']['min'] * 256 <= changes66 <= constraints['bit_changes']['max'] * 256):
            return False
            
        # Check bit changes to 70
        changes70 = sum(1 for i in range(256) if bin_val[i] != bin70[i])
        if not (constraints['bit_changes']['min'] * 256 <= changes70 <= constraints['bit_changes']['max'] * 256):
            return False
            
        # Check growth rates
        growth66 = math.log2(value) - math.log2(self.known_values[66])
        growth70 = math.log2(self.known_values[70]) - math.log2(value)
        if not (constraints['growth_rate']['min'] <= growth66 <= constraints['growth_rate']['max'] and
                constraints['growth_rate']['min'] <= growth70 <= constraints['growth_rate']['max']):
            return False
            
        # Check byte-level changes
        bytes_val = [bin_val[i:i+8] for i in range(0, 256, 8)]
        bytes66 = [bin66[i:i+8] for i in range(0, 256, 8)]
        bytes70 = [bin70[i:i+8] for i in range(0, 256, 8)]
        
        byte_changes66 = sum(1 for i in range(32) if bytes_val[i] != bytes66[i])
        byte_changes70 = sum(1 for i in range(32) if bytes_val[i] != bytes70[i])
        
        if not (constraints['byte_changes']['min'] <= byte_changes66 <= constraints['byte_changes']['max'] and
                constraints['byte_changes']['min'] <= byte_changes70 <= constraints['byte_changes']['max']):
            return False
            
        return True
        
    def find_position_67(self) -> Optional[int]:
        """Find the value for position 67"""
        logging.info("Starting comprehensive search for position 67")
        
        # Analyze sequence properties
        properties = self.analyze_sequence_properties()
        logging.info("Analyzed sequence properties")
        
        # Analyze bit patterns
        patterns = self.analyze_bit_patterns()
        logging.info("Analyzed bit patterns")
        
        # Generate candidates if needed
        if not os.path.exists('analysis_67/candidates/batch_0.json'):
            self.generate_candidates()
            
        # Validate candidates
        valid_candidates = []
        batch_num = 0
        
        while True:
            filename = f'analysis_67/candidates/batch_{batch_num}.json'
            if not os.path.exists(filename):
                break
                
            with open(filename, 'r') as f:
                candidates = [int(h, 16) for h in json.load(f)]
                
            logging.info(f"Validating batch {batch_num} ({len(candidates)} candidates)")
            for candidate in candidates:
                if self.validate_candidate(candidate):
                    valid_candidates.append(candidate)
                    logging.info(f"Found valid candidate: 0x{candidate:x}")
                    
            batch_num += 1
            
        if valid_candidates:
            # Save valid candidates
            with open('analysis_67/valid_candidates.json', 'w') as f:
                json.dump([hex(c) for c in valid_candidates], f, indent=2)
                
            # Choose smallest valid value
            value = min(valid_candidates)
            logging.info(f"Selected value for position 67: 0x{value:x}")
            
            # Save final result with detailed analysis
            with open('analysis_67/position_67.json', 'w') as f:
                json.dump({
                    'position': 67,
                    'value_hex': hex(value),
                    'value_decimal': value,
                    'value_binary': format(value, 'b').zfill(256),
                    'validation': {
                        'bit_changes_66': sum(1 for i in range(256) 
                            if format(value, 'b').zfill(256)[i] != 
                               format(self.known_values[66], 'b').zfill(256)[i]),
                        'bit_changes_70': sum(1 for i in range(256)
                            if format(value, 'b').zfill(256)[i] !=
                               format(self.known_values[70], 'b').zfill(256)[i]),
                        'growth_rate_66': math.log2(value) - math.log2(self.known_values[66]),
                        'growth_rate_70': math.log2(self.known_values[70]) - math.log2(value),
                        'sequence_properties': properties,
                        'bit_patterns': patterns
                    }
                }, f, indent=2)
                
            return value
        else:
            logging.warning("No valid candidates found")
            return None

def main():
    analyzer = Position67Analyzer()
    
    print("Starting Comprehensive Analysis for Position 67")
    print("=" * 80)
    print("\nLoading sequence from data/32bHex.txt...")
    
    value = analyzer.find_position_67()
    
    if value is not None:
        print(f"\nFound value for position 67: 0x{value:x}")
        print(f"Decimal: {value}")
        print(f"Binary: {format(value, 'b').zfill(256)}")
        print("\nAll analysis files saved in analysis_67/")
        
        # Verify Bitcoin address
        print("\nVerifying Bitcoin address generation...")
        subprocess.run(['python3', 'verify_bitcoin.py', 'analysis_67/valid_candidates.json'], check=True)
    else:
        print("\nNo valid value found for position 67")
        
if __name__ == "__main__":
    main() 