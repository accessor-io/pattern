"""
SEQUENCE GENERATOR - Version saved at 2024-12-30 01:25:18

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
            version_time = file[19:-3]  # Extract timestamp from filename
            versions.append((version_time, file))
    
    versions.sort()  # Sort by timestamp
    
    print("\nAvailable versions:")
    for i, (timestamp, filename) in enumerate(versions):
        # Convert timestamp to readable format
        dt = datetime.datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
        readable_time = dt.strftime("%Y-%m-%d %H:%M:%S")
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
            # After position 7, grow exponentially but more controlled
            return min(67, 8 + int(position * 1.5))
    
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
            # Preserve some bits from previous value
            prev_bits = bits[:8]  # Keep first 8 bits
            for i in range(8):
                result[i] = prev_bits[i]
        
        # Handle consecutive 1s in last byte first
        last_byte = value & 0xFF
        last_byte_bits = format(last_byte, '08b')
        
        # Apply permutation with better bit preservation
        for i in range(sig_bits - 8):
            src_pos = i % len(bits)
            new_pos = ((i * 167 + 73) % (sig_bits - 8)) + 8  # Ensure we don't overwrite preserved bits
            if i % 2 == 0:
                new_pos = ((new_pos * 3 + 89) % (sig_bits - 8)) + 8
            result[new_pos] = bits[src_pos]
        
        # Ensure minimum hamming weight in result
        result_str = ''.join(result)
        if result_str.count('1') < position // 2:
            result[sig_bits - 1] = '1'  # Set highest bit
        
        return int(''.join(result), 2)
    
    def _apply_non_linear_transform(self, value: int, position: int) -> int:
        """Apply non-linear transformation with position-based bit limiting"""
        sig_bits = self._get_significant_bits(position)
        
        if position <= 8:
            return value  # Keep original values for first 8 positions
        
        # Split into chunks
        chunk_size = max(8, sig_bits // 4)  # Ensure chunks are at least 8 bits
        chunks = []
        for i in range(4):
            chunk = (value >> (i * chunk_size)) & ((1 << chunk_size) - 1)
            chunks.append(chunk)
        
        # Apply non-linear operations
        for i in range(len(chunks)):
            chunks[i] = chunks[i] ^ (chunks[i] << (chunk_size % 13))
            chunks[i] = chunks[i] ^ (chunks[i] >> (chunk_size % 7))
            chunks[i] = chunks[i] ^ (chunks[i] << (chunk_size % 17))
            chunks[i] &= (1 << chunk_size) - 1
        
        # Recombine with special handling of last byte
        result = 0
        for i in range(4):
            result |= chunks[i] << (i * chunk_size)
        
        # Preserve certain bits from original value
        mask = (1 << 8) - 1
        result = (result & ~mask) | (value & mask)
        
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
        print("\nComparing significant bits with original sequence:")
        for i, (gen, orig) in enumerate(zip(hex_sequence, self.original_sequence[:length])):
            sig_bits = self._get_significant_bits(i)
            gen_val = int(gen, 16) & ((1 << sig_bits) - 1)
            orig_val = int(orig, 16) & ((1 << sig_bits) - 1)
            print(f"Position {i} ({sig_bits} significant bits):")
            print(f"Generated: {format(gen_val, 'x')}")
            print(f"Original:  {format(orig_val, 'x')}")
            print(f"Match: {'✓' if gen_val == orig_val else '✗'}\n")
        
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