"""
Focused Search for Position 67
"""

import math
import logging
import json
import os
from typing import Set, List
from integrated_analysis import IntegratedAnalyzer

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Position67Finder:
    def __init__(self):
        self.analyzer = IntegratedAnalyzer()
        # Known adjacent values
        self.pos_66 = 0x2832ed74f2b5e35ee
        self.pos_70 = 0x349b84b6431a6c4ef1
        
        # Create output directory
        os.makedirs('candidates', exist_ok=True)
        
    def save_candidates(self, candidates: Set[int], batch_num: int):
        """Save a batch of candidates to disk"""
        filename = f'candidates/batch_{batch_num}.json'
        with open(filename, 'w') as f:
            # Convert to hex strings for JSON serialization
            hex_candidates = [hex(c) for c in candidates]
            json.dump(hex_candidates, f)
        logging.info(f"Saved {len(candidates)} candidates to {filename}")
        
    def load_candidates(self, batch_num: int) -> Set[int]:
        """Load a batch of candidates from disk"""
        filename = f'candidates/batch_{batch_num}.json'
        if not os.path.exists(filename):
            return set()
            
        with open(filename, 'r') as f:
            hex_candidates = json.load(f)
            # Convert back from hex strings
            return {int(h, 16) for h in hex_candidates}
            
    def save_progress(self, current_pos: int, total_positions: int):
        """Save current progress"""
        with open('candidates/progress.json', 'w') as f:
            json.dump({
                'current_position': current_pos,
                'total_positions': total_positions,
                'percentage': (current_pos / total_positions) * 100
            }, f)
            
    def load_progress(self) -> dict:
        """Load saved progress"""
        if os.path.exists('candidates/progress.json'):
            with open('candidates/progress.json', 'r') as f:
                return json.load(f)
        return None
        
    def analyze_bit_patterns(self) -> dict:
        """Analyze bit patterns between positions 66 and 70"""
        bin_66 = format(self.pos_66, 'b').zfill(256)
        bin_70 = format(self.pos_70, 'b').zfill(256)
        
        changes = []
        patterns = []
        current_pattern = []
        
        for i in range(len(bin_66)):
            if bin_66[i] != bin_70[i]:
                changes.append(i)
                current_pattern.append(1)
            else:
                current_pattern.append(0)
                
            if len(current_pattern) == 8:
                patterns.append(current_pattern)
                current_pattern = []
                
        logging.info(f"Found {len(changes)} bit changes between pos 66 and 70")
        
        # Save bit pattern analysis
        with open('candidates/bit_patterns.json', 'w') as f:
            json.dump({
                'changes': changes,
                'patterns': patterns,
                'total_changes': len(changes)
            }, f)
            
        return {
            'changes': changes,
            'patterns': patterns,
            'total_changes': len(changes)
        }
        
    def predict_candidates(self) -> Set[int]:
        """Generate candidate values for position 67"""
        patterns = self.analyze_bit_patterns()
        
        # Position 67 is 1/4 of the way between 66 and 70
        expected_changes = int(patterns['total_changes'] * 0.25)
        logging.info(f"Expecting {expected_changes} bit changes for position 67")
        
        # Check for existing progress
        progress = self.load_progress()
        if progress:
            logging.info(f"Resuming from position {progress['current_position']}")
            
        candidates = set()
        bin_66 = format(self.pos_66, 'b').zfill(256)
        batch_size = 1000000  # Save every million candidates
        batch_num = 0
        
        def generate_candidates(base_value: str, changes_needed: int, 
                              positions: List[int], current_pos: int = 0,
                              current_value: str = None):
            nonlocal candidates, batch_num
            
            if current_value is None:
                current_value = base_value
                
            if changes_needed == 0:
                candidates.add(int(current_value, 2))
                if len(candidates) >= batch_size:
                    self.save_candidates(candidates, batch_num)
                    batch_num += 1
                    candidates = set()
                return
                
            if current_pos >= len(positions) or changes_needed > len(positions) - current_pos:
                return
                
            # Save progress
            total_positions = len(positions)
            self.save_progress(current_pos, total_positions)
                
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
        generate_candidates(bin_66, expected_changes, patterns['changes'])
        
        # Save any remaining candidates
        if candidates:
            self.save_candidates(candidates, batch_num)
            
        # Count total candidates
        total_candidates = 0
        for i in range(batch_num + 1):
            batch = self.load_candidates(i)
            total_candidates += len(batch)
            
        logging.info(f"Generated {total_candidates} total candidates")
        return candidates
        
    def validate_candidate(self, candidate: int) -> bool:
        """Validate a candidate value"""
        # Check with position 66
        prev_valid = self.analyzer.verify_sequence_properties(
            self.pos_66,
            candidate
        )['valid']
        
        # Check with position 70
        next_valid = self.analyzer.verify_sequence_properties(
            candidate,
            self.pos_70
        )['valid']
        
        return prev_valid and next_valid
        
    def find_position_67(self) -> int:
        """Find the value for position 67"""
        logging.info("Starting search for position 67")
        
        # Generate candidates if not already generated
        if not os.path.exists('candidates/bit_patterns.json'):
            self.predict_candidates()
            
        # Load and validate candidates batch by batch
        batch_num = 0
        valid_candidates = []
        
        while True:
            candidates = self.load_candidates(batch_num)
            if not candidates:
                break
                
            logging.info(f"Validating batch {batch_num} ({len(candidates)} candidates)")
            for candidate in candidates:
                if self.validate_candidate(candidate):
                    valid_candidates.append(candidate)
                    logging.info(f"Found valid candidate: 0x{candidate:x}")
                    
            batch_num += 1
                
        if valid_candidates:
            # Save valid candidates
            with open('candidates/valid_candidates.json', 'w') as f:
                json.dump([hex(c) for c in valid_candidates], f)
                
            # Choose the smallest valid value
            value = min(valid_candidates)
            logging.info(f"Selected value for position 67: 0x{value:x}")
            return value
        else:
            logging.warning("No valid candidates found")
            return None

def main():
    finder = Position67Finder()
    
    print("Starting Focused Search for Position 67")
    print("=" * 80)
    
    value = finder.find_position_67()
    
    if value is not None:
        print(f"\nFound value for position 67: 0x{value:x}")
        print(f"Decimal: {value}")
        print(f"Binary: {format(value, 'b').zfill(256)}")
        
        # Save final result
        with open('candidates/position_67.json', 'w') as f:
            json.dump({
                'position': 67,
                'value_hex': hex(value),
                'value_decimal': value,
                'value_binary': format(value, 'b').zfill(256)
            }, f)
    else:
        print("\nNo valid value found for position 67")
        
if __name__ == "__main__":
    main() 