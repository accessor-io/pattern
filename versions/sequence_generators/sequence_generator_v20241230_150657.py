class SequenceGenerator:
    def __init__(self):
        self.original_sequence = []
        self.initial_values = []
        self.sequence = []  # Initialize self.sequence here
        try:
            with open('data/32bHex.txt', 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
                self.original_sequence = lines
                if len(lines) >= 8:
                    self.initial_values = [int(val, 16) for val in lines[:8]]
                else:
                    raise ValueError("Not enough initial values in the file.")
        except FileNotFoundError:
            print("File '32bHex.txt' not found. Using default initial values.")
            self.initial_values = [0x1, 0x3, 0x0, 0x5, 0x11, 0xc, 0x60, 0xd3]

    def _get_significant_bits(self, position: int) -> int:
        if position <= 7:
            return position + 1
        else:
            return min(67, 8 + int(position * 1.5))

    def _apply_bit_permutation(self, prev_value: int, position: int) -> int:
        # Preserve first 8 bits from the previous value
        preserved_bits = (prev_value & 0xFF)  # first 8 bits

        # Generate a permutation sequence based on primes
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
        permutation = []
        for i in range(32):  # Adjusted for 32-bit values
            permutation.append((primes[i % len(primes)] * i) % 32)

        # Apply permutation to the value
        permuted_value = 0
        for i in range(32):
            bit = (prev_value >> i) & 1
            permuted_value |= (bit << permutation[i])

        # Combine with preserved bits
        permuted_value = (preserved_bits << 24) | (permuted_value & 0x00FFFFFF)  # Adjusted for 32-bit

        # Apply non-linear transformation
        transformed_value = permuted_value ^ (position * 0xdeadbeef)

        # Mask with significant bits
        sig_bits = self._get_significant_bits(position)
        transformed_value = transformed_value & ((1 << sig_bits) - 1)

        return transformed_value

    def generate_next(self, prev_value: int, position: int) -> int:
        return self._apply_bit_permutation(prev_value, position)

    def generate_sequence(self, length: int) -> List[str]:
        self.sequence = self.initial_values.copy()
        while len(self.sequence) < length:
            next_value = self.generate_next(self.sequence[-1], len(self.sequence))
            self.sequence.append(next_value)

        hex_sequence = [format(x, '08x') for x in self.sequence]  # Corrected to 08x for 32-bit

        # Compare with original sequence
        print("\nSequence Analysis (Generated vs Original):")
        print("=" * 120)
        print(f"{'Pos':>4} | {'Sig.Bits':>8} | {'Generated':>16} | {'Original':>16} | {'Diff':>16} | {'Match?'}")
        print("-" * 120)

        for i in range(min(length, len(self.original_sequence))):
            sig_bits = self._get_significant_bits(i)
            gen_val = self.sequence[i] & ((1 << sig_bits) - 1)
            orig_val = int(self.original_sequence[i], 16) & ((1 << sig_bits) - 1)
            diff = gen_val ^ orig_val
            match = "✓" if gen_val == orig_val else "✗"

            print(f"{i:4d} | {sig_bits:8d} | {hex(gen_val):>16} | {hex(orig_val):>16} | {hex(diff):>16} | {match}")
            print("-" * 120)

        return hex_sequence