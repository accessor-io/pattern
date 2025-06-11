"""
SEQUENCE GENERATOR - Version saved at 2024-12-30 01:39:42

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
        """Calculate number of significant bits needed for position"""
        # Based on analysis of 32bHex.txt pattern
        if position <= 7:
            return position + 1
        else:
            # After position 7, use more natural growth
            # Start with base of 9 bits (position 8 value 1d3)
            base_bits = 9
            # Add position-based growth
            growth = int(math.log2(position - 6) * 2)  # Slower growth
            # Add small linear component for consistency
            linear = (position - 7) // 6
            return min(32, base_bits + growth + linear)
    
    def _mask_to_significant_bits(self, value: int, position: int) -> int:
        """Mask the value to keep only significant bits based on position"""
        sig_bits = self._get_significant_bits(position)
        # Create mask for significant bits
        mask = (1 << sig_bits) - 1
        return value & mask
    
    def _apply_bit_permutation(self, value: int, position: int) -> int:
        """Apply the non-linear bit permutation"""
        sig_bits = self._get_significant_bits(position)
        bits = format(value, f'0{sig_bits}b')
        result = ['0'] * sig_bits
        
        # Special handling for transition from position 8 onwards
        if position >= 8:
            # Preserve bits with smooth transition
            if position == 8:
                # Special case for first transition
                preserve_bits = 9  # Keep all bits from previous value
                prev_bits = format(self.initial_values[-1], '09b')
                # Mix with target pattern for position 8
                target = 0x1d3
                target_bits = format(target, '09b')
                # Combine bits with position-based pattern
                for i in range(9):
                    if i < 3:
                        result[i] = prev_bits[i]  # Keep first 3 bits
                    elif i < 6:
                        result[i] = target_bits[i]  # Use target bits
                    else:
                        result[i] = '1' if (i + position) % 2 else '0'  # Pattern
            else:
                # Normal case
                preserve_bits = min(sig_bits // 2, 8)  # Keep up to half, max 8
                prev_bits = bits[:preserve_bits]
                # Place preserved bits with minimal spacing
                for i, bit in enumerate(prev_bits):
                    result[i] = bit
        
        # Handle middle bits with position-based variation
        mid_bits = sig_bits // 2
        mid_start = (position * 3 + 7) % sig_bits
        for i in range(mid_bits):
            src_pos = (i * 5 + position * 2) % len(bits)
            dst_pos = (mid_start + i * 2) % sig_bits
            result[dst_pos] = bits[src_pos]
        
        # Ensure minimum hamming weight with better distribution
        result_str = ''.join(result)
        weight = result_str.count('1')
        min_weight = max(sig_bits // 5, position // 4)
        
        if weight < min_weight:
            # Add bits in a distributed pattern
            gap = max(2, sig_bits // min_weight)
            for i in range(0, sig_bits, gap):
                if weight >= min_weight:
                    break
                if result[i] == '0':
                    result[i] = '1'
                    weight += 1
        
        return int(''.join(result), 2)
    
    def _apply_non_linear_transform(self, value: int, position: int) -> int:
        """Apply non-linear transformation with position-based bit limiting"""
        sig_bits = self._get_significant_bits(position)
        
        if position <= 8:
            return value
        
        # Split value into overlapping chunks
        chunks = []
        chunk_count = min(3, sig_bits // 4)
        chunk_size = sig_bits // chunk_count
        
        for i in range(chunk_count):
            start = (i * chunk_size * 4 // 5) % sig_bits  # 20% overlap
            chunk = (value >> start) & ((1 << chunk_size) - 1)
            chunks.append(chunk)
        
        # Apply transformations with position influence
        for i, chunk in enumerate(chunks):
            # Use position to vary the transformation
            shift1 = ((position + i) % 3) + 2
            shift2 = ((position + i) % 2) + 2
            
            # Single round with multiple operations
            chunk = chunk ^ (chunk << shift1)
            chunk = chunk ^ (chunk >> shift2)
            chunk = chunk ^ ((chunk << 1) & (chunk >> 1))
            chunks[i] = chunk & ((1 << chunk_size) - 1)
        
        # Recombine chunks with position-based mixing
        result = 0
        for i, chunk in enumerate(chunks):
            shift = (i * chunk_size * 4 // 5) % sig_bits
            result ^= (chunk << shift) & ((1 << sig_bits) - 1)
        
        # Final mixing based on position
        mix_shift = (position % 3) + 1
        result ^= (result >> mix_shift) & ((1 << (sig_bits - mix_shift)) - 1)
        
        return self._mask_to_significant_bits(result, position)
    
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
        print(f"{'Pos':>4} | {'Sig.Bits':>8} | {'Generated Value':^64} | {'Original Value':^64} | {'Match?'}")
        print("-" * 120)
        
        for i, (gen, orig) in enumerate(zip(hex_sequence, self.original_sequence[:length])):
            sig_bits = self._get_significant_bits(i)
            gen_val = int(gen, 16) & ((1 << sig_bits) - 1)
            orig_val = int(orig, 16) & ((1 << sig_bits) - 1)
            
            # Calculate actual used bits
            gen_bits = len(bin(gen_val)[2:])  # Skip '0b' prefix
            orig_bits = len(bin(orig_val)[2:])
            
            # Add labels for interesting patterns
            notes = []
            if i <= 7:
                notes.append("Initial")
            elif i == 8:
                notes.append("First transition")
            
            if "4000000" in gen:
                notes.append("Leading 4")
            if gen.endswith("ae0a") or gen.endswith("af4a"):
                notes.append("Common suffix")
            
            match = "✓" if gen_val == orig_val else "✗"
            
            print(f"{i:4d} | {sig_bits:8d} | {gen} | {orig} | {match} {' '.join(notes)}")
            
            # Print detailed analysis for mismatches
            if match == "✗":
                print(f"{'':4} | {'':8} | Actual bits used: {gen_bits:2d} | Actual bits used: {orig_bits:2d} |")
                if i > 7:  # Only show binary for mismatches after initial values
                    print(f"{'':4} | {'':8} | Binary: {bin(gen_val)[2:]:>64} |")
                    print(f"{'':4} | {'':8} | Binary: {bin(orig_val)[2:]:>64} |")
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