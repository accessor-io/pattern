"""
Sequence Finder Algorithm
Iteratively finds missing values in the sequence by analyzing patterns and validating against paper requirements
"""

import math
import logging
from typing import List, Dict, Set, Optional
from integrated_analysis import IntegratedAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

class SequenceFinder:
    def __init__(self):
        self.analyzer = IntegratedAnalyzer()
        self.known_values = {
            66: 0x2832ed74f2b5e35ee,
            70: 0x349b84b6431a6c4ef1,
            75: 0x4c5ce114686a1336e07,
            80: 0xea1a5c66dcc11b5ad180,
            85: 0x11720c4f018d51b8cebba8,
            90: 0x2ce00bb2136a445c71e85bf,
            95: 0x527a792b183c7f64a0e8b1f4,
            100: 0xaf55fc59c335c8ec67ed24826,
            105: 0x16f14fc2054cd87ee6396b33df3
        }
        
    def find_missing_positions(self, start: int, end: int) -> List[int]:
        """Find all missing positions in a range"""
        missing = [pos for pos in range(start, end + 1) 
                  if pos not in self.known_values]
        logging.info(f"Found {len(missing)} missing positions between {start} and {end}")
        return missing
                
    def analyze_bit_patterns(self, val1: int, val2: int) -> Dict:
        """Analyze bit patterns between two values"""
        bin1 = format(val1, 'b').zfill(256)
        bin2 = format(val2, 'b').zfill(256)
        
        changes = []
        patterns = []
        current_pattern = []
        
        for i in range(len(bin1)):
            if bin1[i] != bin2[i]:
                changes.append(i)
                current_pattern.append(1)
            else:
                current_pattern.append(0)
                
            if len(current_pattern) == 8:
                patterns.append(current_pattern)
                current_pattern = []
                
        result = {
            'changes': changes,
            'patterns': patterns,
            'total_changes': len(changes),
            'pattern_groups': self._group_patterns(patterns)
        }
        
        logging.debug(f"Bit pattern analysis: {len(changes)} changes found")
        return result
        
    def _group_patterns(self, patterns: List[List[int]]) -> Dict:
        """Group similar bit patterns"""
        groups = {}
        for i, pattern in enumerate(patterns):
            pattern_str = ''.join(map(str, pattern))
            if pattern_str not in groups:
                groups[pattern_str] = []
            groups[pattern_str].append(i)
        return groups
        
    def predict_next_value(self, pos: int, prev_val: int) -> Set[int]:
        """Predict possible values for a position based on patterns"""
        logging.info(f"Predicting value for position {pos}")
        candidates = set()
        
        # Find closest known values
        known_positions = sorted(self.known_values.keys())
        prev_known = max([p for p in known_positions if p < pos], default=None)
        next_known = min([p for p in known_positions if p > pos], default=None)
        
        if prev_known is None or next_known is None:
            logging.warning(f"No adjacent known values found for position {pos}")
            return candidates
            
        # Analyze patterns
        prev_patterns = self.analyze_bit_patterns(
            self.known_values[prev_known],
            self.known_values[next_known]
        )
        
        # Calculate expected properties
        pos_ratio = (pos - prev_known) / (next_known - prev_known)
        expected_changes = int(prev_patterns['total_changes'] * pos_ratio)
        
        logging.info(f"Expected {expected_changes} bit changes for position {pos}")
        
        # Generate candidates
        bin_prev = format(prev_val, 'b').zfill(256)
        
        def generate_candidates(base_value: str, changes_needed: int, 
                              positions: List[int], current_pos: int = 0,
                              current_value: str = None):
            if current_value is None:
                current_value = base_value
                
            if changes_needed == 0:
                candidates.add(int(current_value, 2))
                return
                
            if current_pos >= len(positions) or changes_needed > len(positions) - current_pos:
                return
                
            # Don't change this position
            generate_candidates(base_value, changes_needed,
                             positions, current_pos + 1, current_value)
                             
            # Change this position
            new_value = (current_value[:positions[current_pos]] + 
                        ('1' if current_value[positions[current_pos]] == '0' else '0') +
                        current_value[positions[current_pos]+1:])
            generate_candidates(base_value, changes_needed - 1,
                             positions, current_pos + 1, new_value)
        
        # Generate all possible combinations of bit changes
        possible_positions = prev_patterns['changes']
        generate_candidates(bin_prev, expected_changes, possible_positions)
        
        logging.info(f"Generated {len(candidates)} candidates for position {pos}")
        return candidates
        
    def validate_candidate(self, pos: int, candidate: int) -> bool:
        """Validate a candidate value against sequence requirements"""
        # Find adjacent known values
        known_positions = sorted(self.known_values.keys())
        prev_known = max([p for p in known_positions if p < pos], default=None)
        next_known = min([p for p in known_positions if p > pos], default=None)
        
        if prev_known is None or next_known is None:
            return False
            
        # Verify with previous value
        prev_result = self.analyzer.verify_sequence_properties(
            self.known_values[prev_known],
            candidate
        )
        
        # Verify with next value
        next_result = self.analyzer.verify_sequence_properties(
            candidate,
            self.known_values[next_known]
        )
        
        is_valid = prev_result['valid'] and next_result['valid']
        logging.debug(f"Candidate validation for pos {pos}: {is_valid}")
        return is_valid
        
    def find_missing_value(self, pos: int) -> Optional[int]:
        """Find a missing value at a specific position"""
        logging.info(f"Searching for value at position {pos}")
        
        if pos in self.known_values:
            return self.known_values[pos]
            
        # Find closest known values
        known_positions = sorted(self.known_values.keys())
        prev_known = max([p for p in known_positions if p < pos], default=None)
        
        if prev_known is None:
            logging.warning(f"No previous known value found for position {pos}")
            return None
            
        # Generate candidates
        candidates = self.predict_next_value(
            pos,
            self.known_values[prev_known]
        )
        
        # Validate candidates
        valid_candidates = []
        for candidate in candidates:
            if self.validate_candidate(pos, candidate):
                valid_candidates.append(candidate)
                
        if valid_candidates:
            value = min(valid_candidates)
            logging.info(f"Found valid value for position {pos}: 0x{value:x}")
            return value
        else:
            logging.warning(f"No valid candidates found for position {pos}")
            return None
        
    def find_all_missing(self, start: int, end: int) -> Dict[int, int]:
        """Find all missing values in a range"""
        logging.info(f"Starting search for all missing values between {start} and {end}")
        
        missing = self.find_missing_positions(start, end)
        found_values = {}
        
        for pos in missing:
            value = self.find_missing_value(pos)
            if value is not None:
                found_values[pos] = value
                self.known_values[pos] = value  # Update known values
                logging.info(f"Added value for position {pos} to known values")
                
        logging.info(f"Found {len(found_values)} missing values")
        return found_values

def main():
    finder = SequenceFinder()
    
    print("Starting Sequence Analysis")
    print("=" * 80)
    
    # Find missing values between positions 66 and 105
    missing_values = finder.find_all_missing(66, 105)
    
    print("\nFound Missing Values:")
    print("-" * 80)
    for pos, value in sorted(missing_values.items()):
        print(f"Position {pos}: 0x{value:x}")
        
    print("\nAnalysis Summary:")
    print("-" * 80)
    print(f"Total positions analyzed: {105-66+1}")
    print(f"Known values: {len(finder.known_values)}")
    print(f"Found values: {len(missing_values)}")
    print(f"Remaining missing: {105-66+1 - len(finder.known_values)}")
        
if __name__ == "__main__":
    main() 