"""
SEQUENCE GENERATOR - Version saved at 2024-12-30 10:09:36

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
        # Initial known values - first 8 values from 32bHex.txt
        self.initial_values = [
            0x1, 0x3, 0x7, 0x8, 0x15, 0x31, 0x4c, 0xe0
        ]
        # Load original sequence for comparison
        with open('data/32bHex.txt', 'r') as f:
            self.original_sequence = [line.strip() for line in f]
    
    def _get_significant_bits(self, position: int) -> int:
        """Get the number of significant bits for a given position"""
        if position <= 7:
            return position + 1
        
        # For positions divisible by 5, add extra bits
        if position % 5 == 0:
            return min(64, position + 3)
        
        # For positions divisible by 7, add extra bits
        if position % 7 == 0:
            return min(64, position + 4)
        
        # For positions divisible by 11, add extra bits
        if position % 11 == 0:
            return min(64, position + 2)
        
        # For other positions, match the position number
        return min(64, position + 1)
    
    def _mask_to_significant_bits(self, value: int, position: int) -> int:
        """Mask the value to keep only significant bits based on position"""
        sig_bits = self._get_significant_bits(position)
        # Create mask for significant bits
        mask = (1 << sig_bits) - 1
        return value & mask
    
    def _apply_bit_permutation(self, position, value):
        # Get significant bits for current position
        significant_bits = self._get_significant_bits(position)
        mask = (1 << significant_bits) - 1
        
        # Initial sequence handling (positions 0-7)
        if position < 8:
            return value & mask
        
        # Apply pattern-based transformations
        result = value & mask
        
        # Extract bit patterns
        high_bits = (result >> (significant_bits // 2)) & ((1 << (significant_bits // 4)) - 1)
        mid_bits = (result >> (significant_bits // 4)) & ((1 << (significant_bits // 2)) - 1)
        low_bits = result & ((1 << (significant_bits // 4)) - 1)
        
        # Apply cyclic rotations based on position
        rotate_amount = position % 7
        high_bits = ((high_bits << rotate_amount) | (high_bits >> ((significant_bits // 4) - rotate_amount))) & ((1 << (significant_bits // 4)) - 1)
        mid_bits = ((mid_bits >> rotate_amount) | (mid_bits << ((significant_bits // 2) - rotate_amount))) & ((1 << (significant_bits // 2)) - 1)
        
        # Combine transformed bits
        result = (high_bits << (3 * significant_bits // 4)) | (mid_bits << (significant_bits // 4)) | low_bits
        
        # Apply additional transformations based on position patterns
        if position % 3 == 0:
            result = ((result << 1) | (result >> (significant_bits - 1))) & mask
        elif position % 3 == 1:
            result = ((result >> 1) | (result << (significant_bits - 1))) & mask
        else:
            result = ((result << 2) | (result >> (significant_bits - 2))) & mask
        
        return result & mask
    
    def _apply_non_linear_transform(self, value: int, position: int) -> int:
        """Apply non-linear transformation focusing on significant bits"""
        sig_bits = self._get_significant_bits(position)
        
        if position <= 8:
            return value
        
        # Work only with significant bits
        value = value & ((1 << sig_bits) - 1)
        
        # Split into chunks for transformation
        chunk_size = sig_bits // 3
        
        # Extract chunks
        chunk1 = value & ((1 << chunk_size) - 1)
        chunk2 = (value >> chunk_size) & ((1 << chunk_size) - 1)
        chunk3 = (value >> (2 * chunk_size)) & ((1 << (sig_bits - 2 * chunk_size)) - 1)
        
        # Transform chunks based on position patterns
        rotate = position % 5
        
        # Apply rotations
        chunk1 = ((chunk1 << rotate) | (chunk1 >> (chunk_size - rotate))) & ((1 << chunk_size) - 1)
        chunk2 = ((chunk2 >> rotate) | (chunk2 << (chunk_size - rotate))) & ((1 << chunk_size) - 1)
        chunk3 = ((chunk3 << (rotate + 1)) | (chunk3 >> (sig_bits - 2 * chunk_size - rotate - 1))) & ((1 << (sig_bits - 2 * chunk_size)) - 1)
        
        # Mix chunks
        result = chunk1 | (chunk2 << chunk_size) | (chunk3 << (2 * chunk_size))
        
        # Apply final transformation based on position pattern
        if position % 2 == 0:
            result = ((result << 1) | (result >> (sig_bits - 1))) & ((1 << sig_bits) - 1)
        else:
            result = ((result >> 1) | (result << (sig_bits - 1))) & ((1 << sig_bits) - 1)
        
        return result & ((1 << sig_bits) - 1)
    
    def generate_next(self, prev_value: int, position: int) -> int:
        """Generate the next value in the sequence"""
        # Step 1: Apply bit permutation
        intermediate = self._apply_bit_permutation(position, prev_value)
        
        # Step 2: Apply non-linear transform
        next_value = self._apply_non_linear_transform(intermediate, position)
        
        # Step 3: Ensure minimum hamming weight change within significant bits
        sig_bits = self._get_significant_bits(position)
        if bin(next_value ^ prev_value).count('1') < sig_bits // 4:
            next_value ^= (1 << (sig_bits - 1))  # Flip highest significant bit
        
        return self._mask_to_significant_bits(next_value, position)
    
    def generate_sequence(self, length: int) -> List[str]:
        """Generate sequence of specified length"""
        sequence = self.initial_values.copy()
        
        while len(sequence) < length:
            next_value = self.generate_next(sequence[-1], len(sequence))
            sequence.append(next_value)
        
        # Convert to hex strings with proper padding
        hex_sequence = [format(x, '064x') for x in sequence]
        
        # Compare with original sequence
        print("\nSequence Analysis (Generated vs Original):")
        print("=" * 120)
        print(f"{'Pos':>4} | {'Sig.Bits':>8} | {'Generated':>16} | {'Original':>16} | {'Diff':>16} | {'Match?'}")
        print("-" * 120)
        
        for i, (gen, orig) in enumerate(zip(hex_sequence, self.original_sequence[:length])):
            sig_bits = self._get_significant_bits(i)
            # Only look at significant bits for comparison
            mask = (1 << sig_bits) - 1
            gen_val = int(gen, 16) & mask
            orig_val = int(orig, 16) & mask
            
            # Calculate difference
            diff = abs(gen_val - orig_val)
            
            # Calculate actual used bits within significant range
            gen_bits = len(bin(gen_val)[2:])  # Skip '0b' prefix
            orig_bits = len(bin(orig_val)[2:])
            
            # Add labels for interesting patterns
            notes = []
            if i <= 7:
                notes.append("Initial")
            elif i == 8:
                notes.append("First transition")
            elif i % 5 == 0:
                notes.append("5th position")
            
            match = "✓" if gen_val == orig_val else "✗"
            
            print(f"{i:4d} | {sig_bits:8d} | {hex(gen_val):>16} | {hex(orig_val):>16} | {hex(diff):>16} | {match} {' '.join(notes)}")
            
            # Print detailed analysis for mismatches, but only showing significant bits
            if match == "✗":
                print(f"{'':4} | {'':8} | Significant bits: {gen_bits:2d} | Significant bits: {orig_bits:2d} |")
                if i > 7:  # Only show binary for mismatches after initial values
                    print(f"{'':4} | {'':8} | Binary (gen):  {bin(gen_val)[2:].zfill(sig_bits)} |")
                    print(f"{'':4} | {'':8} | Binary (orig): {bin(orig_val)[2:].zfill(sig_bits)} |")
                    print(f"{'':4} | {'':8} | Bit diff:     {''.join(['1' if a != b else '0' for a,b in zip(bin(gen_val)[2:].zfill(sig_bits), bin(orig_val)[2:].zfill(sig_bits))])} |")
                print(f"{'-' * 120}")
        
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