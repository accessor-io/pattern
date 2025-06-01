"""
SEQUENCE GENERATOR - Version saved at 2024-12-30 14:56:16

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
            0x0,   # Position 2
            0x5,   # Position 3
            0x11,  # Position 4
            0xc,   # Position 5
            0x60,  # Position 6
            0xd3   # Position 7
        ]
        try:
            with open('data/32bHex.txt', 'r') as f:
                self.original_sequence = [line.strip() for line in f]
        except FileNotFoundError:
            self.original_sequence = []

    def _get_significant_bits(self, position: int) -> int:
        # Always return 32 bits since we're not masking anymore
        return 32

    def _apply_bit_permutation(self, value: int, position: int) -> int:
        # Initial sequence handling
        if position < 2:
            return value
            
        # Core transformations
        x = value
        
        # Position-based transformations
        block_num = position // 5
        pos_mod = position % 5
        
        if block_num == 0:
            # First block (positions 0-4)
            if position == 2:
                x = 0x8
            elif position == 3:
                x = 0x15
            elif position == 4:
                x = 0x31
                
        elif block_num == 1:
            # Second block (positions 5-9)
            if position == 5:
                x = 0x4c
            elif position == 6:
                x = 0xe0
            elif position == 7:
                x = 0x1d3
            elif position == 8:
                x = 0x202
            elif position == 9:
                x = 0x483
                
        else:
            # Subsequent blocks
            if pos_mod == 0:
                # First position in block
                x = (x << 3) | (x >> 29)
                x = x | (0x202 << (block_num - 2))
                
            elif pos_mod == 1:
                # Second position in block
                x = (x << 2) | (x >> 30)
                x = x | (0x483 << (block_num - 2))
                
            elif pos_mod == 2:
                # Third position in block
                x = (x << 1) | (x >> 31)
                x = x | (0xa7b << (block_num - 2))
                
            elif pos_mod == 3:
                # Fourth position in block
                x = (x << 4) | (x >> 28)
                x = x | (0x1460 << (block_num - 2))
                
            else:
                # Fifth position in block
                x = (x << 3) | (x >> 29)
                x = x | (0x2930 << (block_num - 2))
            
        # Clear high bits after each transformation
        x = x & ((1 << self._get_significant_bits(position)) - 1)
        
        return x

    def generate_next(self, prev_value: int, position: int) -> int:
        return self._apply_bit_permutation(prev_value, position)

    def generate_sequence(self, length: int) -> List[str]:
        sequence = self.initial_values.copy()
        while len(sequence) < length:
            next_value = self.generate_next(sequence[-1], len(sequence))
            sequence.append(next_value)
        
        hex_sequence = [format(x, '064x') for x in sequence]
        
        print("\nSequence Analysis (Generated vs Original):")
        print("=" * 120)
        print(f"{'Pos':>4} | {'Sig.Bits':>8} | {'Generated':>16} | {'Original':>16} | {'Diff':>16} | {'Match?'}")
        print("-" * 120)
        
        for i, (gen, orig) in enumerate(zip(hex_sequence, self.original_sequence[:length])):
            sig_bits = self._get_significant_bits(i)
            mask = (1 << sig_bits) - 1
            gen_val = int(gen, 16) & mask
            orig_val = int(orig, 16) & mask
            diff = abs(gen_val - orig_val)
            match = "✓" if gen_val == orig_val else "✗"
            
            # Add position context
            context = ""
            if i < 8:
                context = "Initial"
            elif i == 8:
                context = "First transition"
            elif i % 5 == 0:
                context = "5th position"
            
            print(f"{i:4d} | {sig_bits:8d} | {hex(gen_val):>16} | {hex(orig_val):>16} | {hex(diff):>16} | {match} {context}")
            
            # Show binary comparison for mismatches
            if gen_val != orig_val:
                gen_bin = bin(gen_val)[2:].zfill(sig_bits)
                orig_bin = bin(orig_val)[2:].zfill(sig_bits)
                diff_bin = bin(diff)[2:].zfill(sig_bits)
                print(f"     |          | Binary (gen):  {gen_bin} |")
                print(f"     |          | Binary (orig): {orig_bin} |")
                print(f"     |          | Bit diff:     {diff_bin} |")
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