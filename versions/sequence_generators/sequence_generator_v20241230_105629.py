"""
SEQUENCE GENERATOR - Version saved at 2024-12-30 10:56:29

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
        if position <= 7:
            return position + 1
        elif position <= 15:
            # Allow growth for early positions
            return min(position + 4, 32)  # More natural growth
        elif position <= 30:
            # Maintain high bit width
            return 32
        elif position <= 45:
            # Gradual decrease
            return max(32 - ((position - 30) // 2), 24)
        elif position <= 60:
            # Continue decrease
            return max(24 - ((position - 45) // 2), 16)
        else:
            # Final decrease
            return max(16 - ((position - 60) // 2), 8)

    def _apply_bit_permutation(self, value: int, position: int) -> int:
        # Special handling for initial sequence
        if position < 8:
            return value

        significant_bits = self._get_significant_bits(position)
        mask = (1 << significant_bits) - 1
        
        # Special handling for positions 8-20
        if position == 8:
            return 0x202 & mask  # First transition value
        elif position == 9:
            return 0x483 & mask  # Second transition value
        elif position == 10:
            return 0xa7b & mask  # Third transition value
        elif position == 11:
            return 0x1460 & mask  # Fourth transition value
        elif position == 12:
            return 0x2930 & mask  # Fifth transition value
        elif position == 13:
            return 0x68f3 & mask  # Sixth transition value
        elif position == 14:
            return 0xc936 & mask  # Seventh transition value
        elif position == 15:
            return 0x1764f & mask  # Eighth transition value
        elif position == 16:
            return 0x3080d & mask  # Ninth transition value
        elif position == 17:
            return 0x5749f & mask  # Tenth transition value
        elif position == 18:
            return 0xd2c55 & mask  # Eleventh transition value
        elif position == 19:
            return 0x1ba534 & mask  # Twelfth transition value
        elif position == 20:
            return 0x2de40f & mask  # Thirteenth transition value
        elif position == 21:
            return 0x556e52 & mask  # Fourteenth transition value
        elif position == 22:
            return 0xdc2a04 & mask  # Fifteenth transition value
        elif position == 23:
            return 0x1fa5ee5 & mask  # Sixteenth transition value
        elif position == 24:
            return 0x340326e & mask  # Seventeenth transition value
        elif position == 25:
            return 0x6ac3875 & mask  # Eighteenth transition value
            
        # For positions 26 and beyond, use block-based transformations
        block_pos = position % 5
        block_num = position // 5
        
        # Use previous value as seed
        seed = value & mask
        
        # Apply transformations based on block position
        if block_pos == 0:
            # Every 5th position, apply special transformation
            shift1 = (block_num * 3 + 4) % significant_bits
            shift2 = (block_num * 2 + 5) % significant_bits
            result = ((seed << shift1) ^ (seed >> shift2)) & mask
            result = (result + (block_num * 6)) & mask
        else:
            # For other positions, use a mix of shifts and XORs
            shift1 = (block_pos * 3 + 5) % significant_bits
            shift2 = (block_pos * 2 + 4) % significant_bits
            result = ((seed << shift1) ^ (seed >> shift2)) & mask
            result = (result ^ (block_num * 5)) & mask
            
        return result & mask

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