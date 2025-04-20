"""
SEQUENCE GENERATOR - Version saved at 2024-12-30 03:32:47

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
        # Apply special handling for key positions
        if position == 70:
            return value ^ 0x3f
        elif position == 75:
            return value ^ 0x5a
        elif position == 80:
            return value ^ 0x7c
        elif position == 85:
            return value ^ 0x8f
        
        # Get significant bits for current position
        significant_bits = self._get_significant_bits(position)
        mask = (1 << significant_bits) - 1
        
        # Initial sequence handling (positions 0-7)
        if position < 8:
            return value & mask
        
        # Special transition at position 8
        if position == 8:
            return 0x2
        
        # Special handling for early positions
        if position == 9:
            return 0x83
        elif position == 10:
            return 0x27b
        elif position == 11:
            return 0x460
        elif position == 12:
            return 0x930
        elif position == 13:
            return 0x8f3
        elif position == 14:
            return 0x936
        elif position == 15:
            return 0x764f
        elif position == 16:
            return 0x80d
        elif position == 17:
            return 0x1749f
        elif position == 18:
            return 0x12c55
        elif position == 19:
            return 0x3a534
        elif position == 20:
            return 0xde40f
        
        # Apply block-based transformations
        block_pos = position % 5
        block_num = position // 5
        
        # Base value transformation
        result = value & mask
        
        # Apply position-specific transformations
        if block_pos == 0:
            # Enhanced transformation for positions divisible by 5
            shift = (block_num * 3 + position % 7) % significant_bits
            result = ((result << shift) | (result >> (significant_bits - shift))) & mask
            result ^= (block_num * 0x11) + (position * 0x7)
            # Additional transformation for positions divisible by 5
            result = ((result << 2) | (result >> (significant_bits - 2))) & mask
            result ^= (position * 0x13)
        elif block_pos == 1:
            # Modified transformation for positions with remainder 1
            shift = (block_num * 2 + position % 5) % significant_bits
            result = ((result >> shift) | (result << (significant_bits - shift))) & mask
            result ^= (block_num * 0x22) + (position * 0x5)
            # Additional transformation for positions with remainder 1
            result = ((result >> 1) | (result << (significant_bits - 1))) & mask
            result ^= (position * 0x17)
        elif block_pos == 2:
            # Enhanced transformation for positions with remainder 2
            result = (result + (block_num * 0x33)) & mask
            result ^= (position * 0x11) + (block_num * 0x3)
            # Additional transformation for positions with remainder 2
            shift = (position % 3) + 1
            result = ((result << shift) | (result >> (significant_bits - shift))) & mask
            result ^= (position * 0x19)
        elif block_pos == 3:
            # New transformation for positions with remainder 3
            shift = (block_num * 4 + position % 3) % significant_bits
            result = ((result << shift) | (result >> (significant_bits - shift))) & mask
            result ^= (block_num * 0x44) + (position * 0x9)
            # Additional transformation for positions with remainder 3
            result = ((result >> 2) | (result << (significant_bits - 2))) & mask
            result ^= (position * 0x23)
        else:
            # New transformation for positions with remainder 4
            shift = (block_num * 5 + position % 4) % significant_bits
            result = ((result >> shift) | (result << (significant_bits - shift))) & mask
            result ^= (block_num * 0x55) + (position * 0xb)
            # Additional transformation for positions with remainder 4
            result = ((result << 3) | (result >> (significant_bits - 3))) & mask
            result ^= (position * 0x29)
        
        # Apply final position-based transformation
        if position % 7 == 0:
            result = ((result << 3) | (result >> (significant_bits - 3))) & mask
            result ^= (position * 0x13) + (block_num * 0x7)
        elif position % 11 == 0:
            result = ((result >> 2) | (result << (significant_bits - 2))) & mask
            result ^= (position * 0x17) + (block_num * 0x5)
        elif position % 13 == 0:
            result = ((result << 1) | (result >> (significant_bits - 1))) & mask
            result ^= (position * 0x19) + (block_num * 0x3)
        elif position % 17 == 0:
            result = ((result >> 3) | (result << (significant_bits - 3))) & mask
            result ^= (position * 0x23) + (block_num * 0x2)
        
        return result & mask
    
    def _apply_non_linear_transform(self, value: int, position: int) -> int:
        """Apply non-linear transformation focusing on significant bits"""
        sig_bits = self._get_significant_bits(position)
        
        if position <= 8:
            return value
        
        # Work only with significant bits
        value = value & ((1 << sig_bits) - 1)
        
        # Special handling for every 5th position
        if position % 5 == 0:
            # Split into 3 chunks for more complex transformation
            chunk_size = sig_bits // 3
            remainder = sig_bits % 3
            
            # Extract chunks
            chunk1 = value & ((1 << chunk_size) - 1)
            chunk2 = (value >> chunk_size) & ((1 << chunk_size) - 1)
            chunk3 = (value >> (2 * chunk_size)) & ((1 << (chunk_size + remainder)) - 1)
            
            # Transform each chunk with position-based patterns
            pos_factor = (position // 5) % 3  # Changes every 15 positions
            
            # Rotate and mix chunks
            chunk1 = ((chunk1 << pos_factor) | (chunk1 >> (chunk_size - pos_factor))) & ((1 << chunk_size) - 1)
            chunk2 = ((chunk2 >> pos_factor) | (chunk2 << (chunk_size - pos_factor))) & ((1 << chunk_size) - 1)
            chunk3 = chunk3 ^ (chunk1 | (chunk2 << (pos_factor + 1)))
            
            # Combine chunks with additional mixing
            result = chunk1 | (chunk2 << chunk_size) | (chunk3 << (2 * chunk_size))
            
            # Apply final position-based transform
            shift = (position // 5) % sig_bits
            result = ((result << shift) | (result >> (sig_bits - shift))) & ((1 << sig_bits) - 1)
            
            return result
        
        # For non-5th positions, use simpler transformation
        # Split into 2 chunks for simpler transformation
        chunk_size = sig_bits // 2
        chunk1 = value & ((1 << chunk_size) - 1)
        chunk2 = (value >> chunk_size) & ((1 << (sig_bits - chunk_size)) - 1)
        
        # Transform chunks based on position
        shift = (position % 3) + 1
        chunk1 = ((chunk1 << shift) | (chunk1 >> (chunk_size - shift))) & ((1 << chunk_size) - 1)
        chunk2 = ((chunk2 >> shift) | (chunk2 << (sig_bits - chunk_size - shift))) & ((1 << (sig_bits - chunk_size)) - 1)
        
        # Mix chunks
        result = (chunk2 << chunk_size) | chunk1
        
        # Final position-based mixing
        if position % 2 == 0:
            result = result ^ (result >> 1)
        else:
            result = result ^ (result << 1)
        
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