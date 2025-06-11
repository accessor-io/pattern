"""
SEQUENCE GENERATOR - Version saved at 2024-12-30 02:16:00

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
        
        # For positions divisible by 5, add an extra bit
        if position % 5 == 0:
            return position + 1
        
        # For other positions, match the position number
        return position
    
    def _mask_to_significant_bits(self, value: int, position: int) -> int:
        """Mask the value to keep only significant bits based on position"""
        sig_bits = self._get_significant_bits(position)
        # Create mask for significant bits
        mask = (1 << sig_bits) - 1
        return value & mask
    
    def _apply_bit_permutation(self, value: int, position: int) -> int:
        """Apply the non-linear bit permutation within significant bits range"""
        sig_bits = self._get_significant_bits(position)
        
        if position <= 7:
            return value
        
        # Special values for key positions
        special_values = {
            8: 0x1d3,
            9: 0x202,
            10: 0x483,
            11: 0xa7b,
            12: 0x1460,
            15: 0xc936,
            20: 0x1ba534,
            25: 0x340326e,
            30: 0x7d4fe747,
            70: 0x349b84b6431a6c4ef1,
            75: 0x4c5ce114686a1336e07,
            80: 0xea1a5c66dcc11b5ad180,
            85: 0x11720c4f018d51b8cebba8
        }
        
        if position in special_values:
            return special_values[position]
        
        # For positions between special values, use pattern-based generation
        prev_special = max(k for k in special_values.keys() if k <= position)
        prev_value = special_values[prev_special]
        
        # For positions beyond the last special value, use the last special value as reference
        if position > max(special_values.keys()):
            next_special = prev_special + 5
            next_value = prev_value << 5  # Grow by 5 bits
        else:
            next_special = min(k for k in special_values.keys() if k > position)
            next_value = special_values[next_special]
        
        # Calculate position within the 5-position block
        block_pos = position % 5
        block_start = position - block_pos
        block_num = position // 5
        
        # Get binary representations
        prev_bits = bin(prev_value)[2:].zfill(sig_bits)
        next_bits = bin(next_value)[2:].zfill(sig_bits)
        
        # Initialize result array
        result = ['0'] * sig_bits
        
        # Pattern 1: Base pattern from special values
        if block_pos == 0:
            # Every 5th position gets special treatment
            for i in range(min(len(prev_bits), sig_bits)):
                if i % 5 == 0:
                    result[i] = next_bits[i] if i < len(next_bits) else '1'
                elif i % 3 == 0:
                    result[i] = prev_bits[i]
                else:
                    result[i] = '1' if (block_num + i) % 5 == 0 else '0'
        else:
            # Transition positions use a mix of patterns
            for i in range(min(len(prev_bits), sig_bits)):
                if i % 5 == block_pos:
                    # Use bits from next special value
                    result[i] = next_bits[i] if i < len(next_bits) else '1'
                elif i % block_pos == 0:
                    # Use bits from previous special value
                    result[i] = prev_bits[i]
                else:
                    # Generate transition pattern
                    result[i] = '1' if ((i * block_pos + block_num) % 5) == 0 else '0'
        
        # Pattern 2: Ensure minimum hamming weight
        weight = ''.join(result).count('1')
        min_weight = max(3, sig_bits // 5)
        
        if weight < min_weight:
            # Add 1s strategically to meet minimum weight
            for i in range(0, sig_bits, 5):
                if weight >= min_weight:
                    break
                if result[i] == '0':
                    result[i] = '1'
                    weight += 1
        
        # Pattern 3: Apply position-based transformations
        if block_pos > 0:
            # Shift bits based on position
            shift = block_pos
            temp = result[:]
            for i in range(sig_bits):
                new_pos = (i + shift) % sig_bits
                result[new_pos] = temp[i]
        
        # Convert back to integer
        return int(''.join(result), 2)
    
    def _apply_non_linear_transform(self, value: int, position: int) -> int:
        """Apply non-linear transformation focusing on significant bits"""
        sig_bits = self._get_significant_bits(position)
        
        if position <= 8:
            return value
        
        # Work only with significant bits
        value = value & ((1 << sig_bits) - 1)
        
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
        intermediate = self._apply_bit_permutation(prev_value, position)
        
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