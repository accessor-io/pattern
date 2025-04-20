from typing import List
import math
import os
import datetime
import shutil

def save_implementation_version():
    """Save a versioned copy of the current implementation with full documentation"""
    if not os.path.exists('versions'):
        os.makedirs('versions')
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    version_header = f"""SEQUENCE GENERATOR - Version saved at {timestamp}\n"""
    with open('sequence_generator.py', 'r') as f:
        current_code = f.read()
    version_file = f'versions/sequence_generator_v{timestamp}.py'
    with open(version_file, 'w') as f:
        f.write(version_header)
        f.write(current_code)
    if os.path.exists('generated_sequence.txt'):
        seq_version_file = f'versions/sequence_{timestamp}.txt'
        shutil.copy2('generated_sequence.txt', seq_version_file)
    print(f"Saved implementation version to: {version_file}")

def list_versions():
    """List all saved versions of the implementation"""
    if not os.path.exists('versions'):
        print("No versions directory found.")
        return []
    versions = []
    for file in os.listdir('versions'):
        if file.startswith('sequence_generator_v') and file.endswith('.py'):
            version_time = file[20:-3]
            versions.append((version_time, file))
    versions.sort()
    print("\nAvailable versions:")
    for i, (timestamp, filename) in enumerate(versions):
        try:
            dt = datetime.datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
            readable_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            readable_time = timestamp
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
        backup_name = f'sequence_generator_backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
        shutil.copy2('sequence_generator.py', backup_name)
        shutil.copy2(version_path, 'sequence_generator.py')
        print(f"Loaded version: {filename}")
        print(f"Current implementation backed up to: {backup_name}")
        return True
    else:
        print("Invalid version number")
        return False

class SequenceGenerator:
    def __init__(self):
        self.initial_values = [0x1, 0x3, 0x7, 0x8, 0x15, 0x31, 0x4c, 0xe0]
        try:
            with open('data/32bHex.txt', 'r') as f:
                self.original_sequence = [line.strip() for line in f]
        except FileNotFoundError:
            self.original_sequence = []
    
    def _get_significant_bits(self, position: int) -> int:
        if position <= 7:
            return position + 1
        return min(64, position + 1)
    
    def _mask_to_significant_bits(self, value: int, position: int) -> int:
        sig_bits = self._get_significant_bits(position)
        mask = (1 << sig_bits) - 1
        return value & mask
    
    def _apply_bit_permutation(self, value: int, position: int) -> int:
        sig_bits = self._get_significant_bits(position)
        value = value & ((1 << sig_bits) - 1)
        # Simplified bit permutation logic
        # Example: reverse the bit order
        permuted = 0
        for i in range(sig_bits):
            permuted |= ((value >> i) & 1) << (sig_bits - 1 - i)
        return permuted
    
    def _apply_non_linear_transform(self, value: int, position: int) -> int:
        sig_bits = self._get_significant_bits(position)
        value = value & ((1 << sig_bits) - 1)
        # Simplified non-linear transformation
        # Example: XOR with a shifted version of itself
        shift = position % sig_bits
        transformed = (value ^ (value << shift)) & ((1 << sig_bits) - 1)
        return transformed
    
    def generate_next(self, prev_value: int, position: int) -> int:
        intermediate = self._apply_bit_permutation(prev_value, position)
        next_value = self._apply_non_linear_transform(intermediate, position)
        sig_bits = self._get_significant_bits(position)
        if bin(next_value ^ prev_value).count('1') < sig_bits // 4:
            next_value ^= (1 << (sig_bits - 1))
        return self._mask_to_significant_bits(next_value, position)
    
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
            print(f"{i:4d} | {sig_bits:8d} | {hex(gen_val):>16} | {hex(orig_val):>16} | {hex(diff):>16} | {match}")
        return hex_sequence

def main():
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
    save_implementation_version()
    generator = SequenceGenerator()
    sequence = generator.generate_sequence(160)
    print("\nGenerated sequence (160 values):")
    for i, value in enumerate(sequence):
        print(f"{value}")
    with open('generated_sequence.txt', 'w') as f:
        for value in sequence:
            f.write(f"{value}\n")
    print("\nSequence has been saved to generated_sequence.txt")
    print("\nUse --list to see available versions")
    print("Use --load [number] to load a specific version")

if __name__ == "__main__":
    main()