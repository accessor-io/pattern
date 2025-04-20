"""
SEQUENCE GENERATOR - Version saved at 2024-12-30 15:25:19

This is an automatically saved version of the sequence generator implementation.
Each version is preserved exactly as it was at the time of saving, including all
functions, algorithms, and documentation.

IMPLEMENTATION DETAILS:
----------------------
- Initial values: First 8 values from 32bHex.txt
- Significant bits calculation: Position-based growth
- Bit permutation: Non-linear with position-based preservation
- Transformation: Chunk-based non-linear operations

KEY ALGORITHMS:
-------------
1. Significant Bits:
   - Position ≤ 7: bits = position + 1
   - Position > 7: bits = min(67, 8 + int(position * 1.5))

2. Bit Permutation:
   - Special handling for position ≥ 8
   - Preserves first 8 bits from previous value
   - Uses prime number based position mixing

3. Non-linear Transform:
   - Chunk-based processing
   - Position-dependent chunk sizes
   - Special handling of last byte

ORIGINAL CHANGELOG:

CHANGELOG:

Version 1.0 (Initial)
- Basic sequence generator with first 8 known values
- Simple bit permutation and non-linear transform

Version 1.1
- Added significant bits calculation
- Added bit masking based on position
- Improved comparison with original sequence

Version 1.2
- Modified growth rate for significant bits after position 7
- Added special handling for transition after position 8
- Improved bit preservation in permutation
- Added minimum hamming weight requirements

Version 1.3
- Fixed bit permutation bug with bin() operation
- Added version control system
- Added sequence output saving
- Extended sequence generation to 160 values

Current Version: 1.3

"""

from typing import List
import math
import os
import datetime
import shutil

def save_implementation_version():
    """Save a versioned copy of the current implementation with full documentation"""
    # Create versions directory if it doesn't exist
    if not os.path.exists('versions'):
        os.makedirs('versions')
    
    # Get current timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create version header
    version_header = f'''"""
SEQUENCE GENERATOR - Version saved at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This is an automatically saved version of the sequence generator implementation.
Each version is preserved exactly as it was at the time of saving, including all
functions, algorithms, and documentation.

IMPLEMENTATION DETAILS:
----------------------
- Initial values: First 8 values from 32bHex.txt
- Significant bits calculation: Position-based growth
- Bit permutation: Non-linear with position-based preservation
- Transformation: Chunk-based non-linear operations

KEY ALGORITHMS:
-------------
1. Significant Bits:
   - Position ≤ 7: bits = position + 1
   - Position > 7: bits = min(67, 8 + int(position * 1.5))

2. Bit Permutation:
   - Special handling for position ≥ 8
   - Preserves first 8 bits from previous value
   - Uses prime number based position mixing

3. Non-linear Transform:
   - Chunk-based processing
   - Position-dependent chunk sizes
   - Special handling of last byte

ORIGINAL CHANGELOG:
{open('sequence_generator.py', 'r').read().split('"""')[1]}
"""

'''
    
    # Read current implementation
    with open('sequence_generator.py', 'r') as f:
        current_code = f.read()
    
    # Create new version with header
    version_file = f'versions/sequence_generator_v{timestamp}.py'
    with open(version_file, 'w') as f:
        f.write(version_header)
        f.write(current_code[current_code.find('from typing'):])  # Skip original docstring
    
    # Also save the generated sequence if it exists
    if os.path.exists('generated_sequence.txt'):
        seq_version_file = f'versions/sequence_{timestamp}.txt'
        shutil.copy2('generated_sequence.txt', seq_version_file)
    
    print(f"\nSaved implementation version to: {version_file}")

def list_versions():
    """List all saved versions of the implementation"""
    if not os.path.exists('versions'):
        print("No versions directory found.")
        return []
    
    versions = []
    for file in os.listdir('versions'):
        if file.startswith('sequence_generator_v') and file.endswith('.py'):
            # Extract timestamp, removing 'sequence_generator_v' prefix and '.py' suffix
            version_time = file[20:-3]  # Skip 'sequence_generator_v' prefix
            versions.append((version_time, file))
    
    versions.sort()  # Sort by timestamp
    
    print("\nAvailable versions:")
    for i, (timestamp, filename) in enumerate(versions):
        try:
            # Convert timestamp to readable format
            dt = datetime.datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
            readable_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            readable_time = timestamp  # Use raw timestamp if parsing fails
        print(f"{i+1}. {readable_time} - {filename}")
    
    return versions

def load_version(version_number=None):
    """Load a specific version of the implementation"""
    versions = list_versions()
    if not versions:
        return False
    
    if version_number is None:
        version_number = input("\nEnter version number to load (or press Enter for latest): ")
        if not version_number:
            version_number = len(versions)
        else:
            version_number = int(version_number)
    
    if 1 <= version_number <= len(versions):
        _, filename = versions[version_number - 1]
        version_path = os.path.join('versions', filename)
        
        # Backup current file
        backup_name = f'sequence_generator_backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
        shutil.copy2('sequence_generator.py', backup_name)
        
        # Load chosen version
        shutil.copy2(version_path, 'sequence_generator.py')
        print(f"\nLoaded version: {filename}")
        print(f"Current implementation backed up to: {backup_name}")
        return True
    else:
        print("\nInvalid version number")
        return False

class SequenceGenerator:
    def __init__(self):
        self.initial_values = [
            0x1,   # Position 0
            0x3,   # Position 1
            0x7,   # Position 2
            0x8,   # Position 3
            0x15,  # Position 4
            0x31,  # Position 5
            0x4c,  # Position 6
            0xe0   # Position 7
        ]
        try:
            with open('data/32bHex.txt', 'r') as f:
                self.original_sequence = [line.strip() for line in f]
                # Read first 8 values as initial values if available
                if len(self.original_sequence) >= 8:
                    self.initial_values = [int(val, 16) for val in self.original_sequence[:8]]
        except FileNotFoundError:
            pass  # Use hardcoded initial values

    def _get_significant_bits(self, position: int) -> int:
        if position <= 7:
            return position + 1
        else:
            return 8 + int(position * 1.5)

    def _apply_bit_permutation(self, value: int, position: int) -> int:
        if position < len(self.initial_values):
            return self.initial_values[position]
        
        # For positions after initial values, use dynamic pattern analysis
        prev_value = self.sequence[-1]
        
        # Get the position of the highest set bit
        def highest_bit_pos(n):
            return len(bin(n)) - 3  # -3 for '0b' prefix and 0-based index
        
        prev_high_bit = highest_bit_pos(prev_value)
        
        # Calculate base growth factor based on position
        base_growth = 2.0 - (position % 5) * 0.1  # Varies between 1.6x and 2.0x
        base = int(prev_value * base_growth)
        
        # Apply position-specific transformations
        block_position = position % 5  # Position within each 5-value block
        
        if block_position == 0:
            # Start of new block: emphasize high bits
            shift = prev_high_bit // 3
            new_value = (base << 1) | (base >> shift)
        elif block_position == 1:
            # Second position: mix with previous
            new_value = base ^ (prev_value >> 2)
        elif block_position == 2:
            # Middle position: preserve some structure
            mask = (1 << (prev_high_bit // 2)) - 1
            new_value = (base & ~mask) | (prev_value & mask)
        elif block_position == 3:
            # Fourth position: add controlled variation
            new_value = base ^ ((position * 0x111) & ((1 << prev_high_bit) - 1))
        else:
            # Last position: combine patterns
            new_value = base | (prev_value & ((1 << (prev_high_bit // 2)) - 1))
        
        # Apply block-based transformations
        block_number = position // 5
        if block_number > 0:
            # Mix with previous block's pattern
            if len(self.sequence) >= 5:
                five_back = self.sequence[-5]
                new_value ^= five_back >> (block_number % 3)
        
        # Ensure minimum growth
        if new_value <= prev_value:
            # If not growing, apply a different transformation
            shift = prev_high_bit // 4
            new_value = prev_value + (prev_value >> shift) + (position * 0x111)
        
        return new_value

    def generate_next(self, prev_value: int, position: int) -> int:
        return self._apply_bit_permutation(prev_value, position)

    def generate_sequence(self, length: int) -> List[str]:
        self.sequence = self.initial_values.copy()
        while len(self.sequence) < length:
            next_value = self.generate_next(self.sequence[-1], len(self.sequence))
            self.sequence.append(next_value)
        
        # Let hex strings grow naturally with no padding
        hex_sequence = [hex(x)[2:] for x in self.sequence]
        
        # Compare with original sequence
        print("\nSequence Analysis (Generated vs Original):")
        print("=" * 120)
        print(f"{'Pos':>4} | {'Sig.Bits':>8} | {'Generated':>64} | {'Original':>64} | {'Diff':>64} | {'Match?'}")
        print("-" * 120)
        
        for i in range(min(length, len(self.original_sequence))):
            sig_bits = self._get_significant_bits(i)
            sig_mask = (1 << sig_bits) - 1
            gen_val = self.sequence[i] & sig_mask  # Only mask during comparison
            orig_val = int(self.original_sequence[i], 16) & sig_mask
            diff = gen_val ^ orig_val
            match = "✓" if gen_val == orig_val else "✗"
            
            # Let the hex strings grow in the display too
            print(f"{i:4d} | {sig_bits:8d} | {hex(gen_val)[2:]} | {hex(orig_val)[2:]} | {hex(diff)[2:]} | {match}")
            print("-" * 120)
        
        return hex_sequence

def main():
    # Add command line argument handling
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == '--list':
            list_versions()
            return
        elif sys.argv[1] == '--load':
            version_num = int(sys.argv[2]) if len(sys.argv) > 2 else None
            if load_version(version_num):
                print("Please restart the script to use the loaded version")
            return
    
    # Normal execution
    save_implementation_version()
    generator = SequenceGenerator()
    sequence = generator.generate_sequence(160)
    
    # Print all 160 values in the same format as 32bHex.txt
    print("\nGenerated sequence (160 values):")
    for i, value in enumerate(sequence):
        print(f"{value}")
    
    # Save to file
    with open('generated_sequence.txt', 'w') as f:
        for value in sequence:
            f.write(f"{value}\n")
    
    print("\nSequence has been saved to generated_sequence.txt")
    print("\nUse --list to see available versions")
    print("Use --load [number] to load a specific version")

if __name__ == "__main__":
    main() 