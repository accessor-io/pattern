# -*- coding: utf-8 -*-

import time
import random
import hashlib
from colorama import init, Fore, Style
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from matrix_sync import MatrixSync

# Initialize colorama
init()

class MatrixVisualizer:
    def __init__(self):
        self.matrix = MatrixSync()
        self.MATRIX_CHARS = "⟘⟙⟚⟛⟜⟝⟞⟟⟠⟡⟢⟣⟤⟥⟦⟧⟨⟩⟪⟫⟬⟭⟮⟯"
        self.HEX_MARKERS = "⎔⎕⎖⎗⎘⎙⎚⎛⎜⎝⎞⎟⎠⎡⎢⎣⎤⎥⎦⎧⎨⎩⎪⎫⎬⎭"
        
    def visualize_sync_states(self, hex_string=None):
        """
        Modified to include address sequence analysis
        """
        if hex_string is None:
            hex_string = "0" * 63 + random.choice("123456789abcdef")
        
        print(f"\n{Fore.CYAN}Matrix Sync State Visualization - Hex Mode{Style.RESET_ALL}")
        print("=" * 50)
        
        # Get 4-char string from address sequence
        result_string = self.analyze_address_sequence(hex_string)
        
        # Original visualization code...
        chunk_size = 8
        for i in range(0, len(hex_string), chunk_size):
            chunk = hex_string[i:i+chunk_size]
            matrix_char = random.choice(self.MATRIX_CHARS)
            hex_marker = random.choice(self.HEX_MARKERS)
            print(f"{Fore.GREEN}{matrix_char} {Fore.YELLOW}{chunk} {Fore.GREEN}{hex_marker}{Style.RESET_ALL}")
        
        # Display state transitions with new result string
        self._display_state_transitions(hex_string, result_string)
        self._display_sync_matrix(hex_string)
        self._display_sync_patterns(hex_string)

    def compare_sequences(self):
        """
        Compare and visualize patterns between different hex sequences
        """
        sequences = [
            ("0" * 63 + "1", "Base"),
            ("0" * 63 + "2", "Double"),
            ("0" * 63 + "3", "Triple"),
            ("0" * 63 + "5", "Prime"),
            ("0" * 63 + "7", "Prime2"),
            ("0" * 63 + "a", "Hex-A"),
            ("0" * 63 + "b", "Hex-B"),
            ("0" * 63 + "d", "Hex-D"),
            ("0" * 63 + "f", "Max")
        ]

        print(f"\n{Fore.CYAN}Matrix Sequence Pattern Analysis{Style.RESET_ALL}")
        print("=" * 50)

        for hex_string, label in sequences:
            self._display_sequence_analysis(hex_string, label)
            time.sleep(0.5)

    def _display_state_transitions(self, hex_string, result_string):
        print("\nState Transitions:")
        print("=" * 20)
        
        # Use result string to influence transitions
        for i, (state, binary) in enumerate(self.matrix.sync_states.items()):
            state_hash = hashlib.sha256(state.encode()).hexdigest()[:8]
            # Use result string character to influence transition pattern
            transition_char = result_string[i % 4]
            transition_pattern = self._get_transition_pattern(transition_char)
            print(f"{Fore.GREEN}{state:8} {Fore.CYAN}{transition_pattern} {Fore.YELLOW}{state_hash} {Fore.WHITE}{binary}{Style.RESET_ALL}")

    def _display_sync_matrix(self, hex_string):
        print("\nSync Matrix:")
        print("=" * 20)
        
        matrix_size = 4
        for i in range(matrix_size):
            row = []
            for j in range(matrix_size):
                pos = (i * matrix_size + j) * 2
                hex_val = hex_string[pos:pos+2] if pos < len(hex_string) else '00'
                marker = random.choice(self.HEX_MARKERS) if random.random() > 0.5 else '·'
                row.append(f"{Fore.GREEN}{marker}{Fore.YELLOW}{hex_val}")
            print(" ".join(row) + Style.RESET_ALL)

    def _display_sync_patterns(self, hex_string):
        print("\nSync Patterns with Hex Mapping:")
        print("=" * 30)
        for pattern, binary in self.matrix.sync_patterns.items():
            pattern_hash = hashlib.sha256(pattern.encode()).hexdigest()[:8]
            print(f"{Fore.CYAN}{pattern} {Fore.GREEN}⟺ {Fore.YELLOW}{pattern_hash} {Fore.WHITE}{binary}{Style.RESET_ALL}")

    def _display_sequence_analysis(self, hex_string, label):
        compressed, uncompressed = self.matrix.map_address(hex_string)
        
        pattern = "⎯".join([
            f"{Fore.GREEN}◉{Style.RESET_ALL}",
            f"{Fore.YELLOW}{hex_string[-1]}{Style.RESET_ALL}",
            f"{Fore.CYAN}⟁{Style.RESET_ALL}"
        ])
        
        print(f"\n{Fore.WHITE}{label}{Style.RESET_ALL}")
        print(f"Pattern: {pattern}")
        print(f"Compressed: {Fore.GREEN}{compressed[:8]}...{compressed[-8:]}{Style.RESET_ALL}")
        print(f"Uncompressed: {Fore.YELLOW}{uncompressed[:8]}...{uncompressed[-8:]}{Style.RESET_ALL}")
        
        state = self.matrix.get_state(bin(int(hex_string[-1], 16))[2:].zfill(4))
        print(f"Sync State: {Fore.CYAN}{state}{Style.RESET_ALL}")
        
        print(f"{Fore.BLUE}{'· ' * 25}{Style.RESET_ALL}")

    def analyze_address_sequence(self, hex_string):
        """
        Analyze address sequence to generate pattern and 4-char string
        """
        compressed, uncompressed = self.matrix.map_address(hex_string)
        
        # Extract pattern from addresses
        def extract_pattern(address):
            if address == "ERROR_ADDRESS":
                return None
            
            # Take specific positions from address to create pattern
            positions = [8, 16, 24, 32]  # Key positions in address
            pattern = ''.join(address[i] if i < len(address) else '0' for i in positions)
            return pattern
        
        comp_pattern = extract_pattern(compressed)
        uncomp_pattern = extract_pattern(uncompressed)
        
        # Generate 4-char string using both patterns
        def generate_4char_string(pattern1, pattern2):
            if not pattern1 or not pattern2:
                return "XXXX"
            
            # XOR the patterns together
            combined = ''
            for c1, c2 in zip(pattern1, pattern2):
                # Convert characters to numbers and XOR them
                num = (int(c1, 36) ^ int(c2, 36)) % 36
                # Convert back to char (0-9, A-Z)
                combined += '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'[num]
            
            return combined
        
        result_string = generate_4char_string(comp_pattern, uncomp_pattern)
        
        # Visual representation
        print(f"\n{Fore.CYAN}Address Sequence Analysis{Style.RESET_ALL}")
        print("=" * 40)
        print(f"Compressed Pattern:   {Fore.GREEN}{comp_pattern}{Style.RESET_ALL}")
        print(f"Uncompressed Pattern: {Fore.YELLOW}{uncomp_pattern}{Style.RESET_ALL}")
        print(f"Result String:        {Fore.MAGENTA}{result_string}{Style.RESET_ALL}")
        
        # Show pattern formation
        print("\nPattern Formation:")
        print(f"{Fore.GREEN}{compressed[:8]}...{compressed[-8:]}{Style.RESET_ALL}")
        print(f"       ↓  ↓  ↓  ↓")
        print(f"{Fore.CYAN}{' '.join(result_string)}{Style.RESET_ALL}")
        print(f"       ↑  ↑  ↑  ↑")
        print(f"{Fore.YELLOW}{uncompressed[:8]}...{uncompressed[-8:]}{Style.RESET_ALL}")
        
        return result_string

    def _get_transition_pattern(self, char):
        """
        Generate transition pattern based on character
        """
        patterns = {
            '0': '⟷⟷', '1': '⟺⟺', '2': '⟹⟸', '3': '⟸⟹',
            '4': '⟷⟺', '5': '⟺⟷', '6': '⟹⟹', '7': '⟸⟸',
            '8': '⟷⟹', '9': '⟷⟸', 'A': '⟺⟹', 'B': '⟺⟸',
            'C': '⟹⟷', 'D': '⟸⟷', 'E': '⟹⟺', 'F': '⟸⟺'
        }
        return patterns.get(char, '⟷⟷')

    def analyze_from_address(self, address):
        """
        Analyze patterns starting from a Bitcoin address
        """
        print(f"\n{Fore.CYAN}Address-Based Pattern Analysis{Style.RESET_ALL}")
        print("=" * 50)
        
        # Extract key positions from address
        positions = [0, 8, 16, 24, 32]  # Important positions in address
        key_chars = [address[i:i+8] for i in positions if i < len(address)]
        
        # Generate pattern from address
        pattern = ''.join([char[0] for char in key_chars])
        
        # Create 4-char string from pattern
        result_string = ''
        for i in range(0, len(pattern), 2):
            if i+1 < len(pattern):
                # Combine pairs of characters
                char_pair = pattern[i:i+2]
                # Convert to hex-like character
                num = sum(ord(c) for c in char_pair) % 16
                result_string += hex(num)[2:].upper()
        
        # Ensure 4 characters
        result_string = (result_string + "0000")[:4]
        
        # Visual display
        print(f"\nInput Address: {Fore.YELLOW}{address}{Style.RESET_ALL}")
        print(f"Key Positions: {Fore.GREEN}{' → '.join(key_chars)}{Style.RESET_ALL}")
        print(f"Pattern: {Fore.CYAN}{pattern}{Style.RESET_ALL}")
        print(f"Result String: {Fore.MAGENTA}{result_string}{Style.RESET_ALL}")
        
        # Show pattern formation
        print("\nPattern Formation:")
        for i, char in enumerate(result_string):
            print(f"{Fore.CYAN}Position {i}: {Fore.GREEN}{key_chars[i]}{Fore.YELLOW} → {Fore.MAGENTA}{char}{Style.RESET_ALL}")
        
        # Display matrix representation
        self._display_matrix_from_string(result_string)
        return result_string

    def _display_matrix_from_string(self, result_string):
        """
        Display matrix representation of the result string
        """
        print(f"\n{Fore.CYAN}Matrix Representation:{Style.RESET_ALL}")
        print("=" * 20)
        
        matrix_size = 4
        for i in range(matrix_size):
            row = []
            for j in range(matrix_size):
                char_index = (i * matrix_size + j) % len(result_string)
                char = result_string[char_index]
                marker = random.choice(self.HEX_MARKERS) if random.random() > 0.5 else '·'
                row.append(f"{Fore.GREEN}{marker}{Fore.YELLOW}{char}")
            print(" ".join(row) + Style.RESET_ALL)

    def analyze_correlation(self, hex_string, address):
        """
        Enhanced correlation analysis between hex string and Bitcoin address
        """
        print(f"\n{Fore.CYAN}Correlation Analysis{Style.RESET_ALL}")
        print("=" * 50)
        
        try:
            # Generate addresses from hex string
            compressed, uncompressed = self.matrix.map_address(hex_string)
            
            print(f"\nHex String: {Fore.YELLOW}{hex_string[:6]}...{hex_string[-6:]}{Style.RESET_ALL}")
            print(f"Input Address: {Fore.GREEN}{address}{Style.RESET_ALL}")
            
            print(f"\nGenerated Addresses:")
            print(f"Compressed:   {Fore.CYAN}{compressed}{Style.RESET_ALL}")
            print(f"Uncompressed: {Fore.CYAN}{uncompressed}{Style.RESET_ALL}")
            
            # Pattern Analysis
            def analyze_pattern(addr):
                return {
                    'prefix': addr[0],
                    'checksum': addr[-4:],
                    'body': addr[1:-4],
                    'key_positions': [addr[i] for i in [0, 8, 16, 24, 32] if i < len(addr)]
                }
            
            input_pattern = analyze_pattern(address)
            comp_pattern = analyze_pattern(compressed)
            uncomp_pattern = analyze_pattern(uncompressed)
            
            print(f"\n{Fore.CYAN}Detailed Pattern Analysis:{Style.RESET_ALL}")
            print("=" * 30)
            
            # Compare patterns
            print(f"\nPrefix Analysis:")
            print(f"Input:       {Fore.GREEN}{input_pattern['prefix']}{Style.RESET_ALL}")
            print(f"Compressed:  {Fore.YELLOW}{comp_pattern['prefix']}{Style.RESET_ALL}")
            print(f"Uncompressed:{Fore.YELLOW}{uncomp_pattern['prefix']}{Style.RESET_ALL}")
            
            print(f"\nKey Position Markers:")
            print(f"Input:       {Fore.GREEN}{' '.join(input_pattern['key_positions'])}{Style.RESET_ALL}")
            print(f"Compressed:  {Fore.YELLOW}{' '.join(comp_pattern['key_positions'])}{Style.RESET_ALL}")
            print(f"Uncompressed:{Fore.YELLOW}{' '.join(uncomp_pattern['key_positions'])}{Style.RESET_ALL}")
            
            # Calculate similarity scores
            def calculate_similarity(pattern1, pattern2):
                matches = sum(1 for c1, c2 in zip(pattern1['key_positions'], pattern2['key_positions']) if c1 == c2)
                total = len(pattern1['key_positions'])
                return (matches / total) if total > 0 else 0
            
            comp_similarity = calculate_similarity(input_pattern, comp_pattern)
            uncomp_similarity = calculate_similarity(input_pattern, uncomp_pattern)
            
            print(f"\n{Fore.CYAN}Similarity Analysis:{Style.RESET_ALL}")
            print("=" * 30)
            print(f"Compressed Similarity:   {Fore.YELLOW}{comp_similarity:.2%}{Style.RESET_ALL}")
            print(f"Uncompressed Similarity: {Fore.YELLOW}{uncomp_similarity:.2%}{Style.RESET_ALL}")
            
            # Visual pattern matching
            print(f"\n{Fore.CYAN}Pattern Matching:{Style.RESET_ALL}")
            print("=" * 30)
            def show_pattern_match(addr1, addr2):
                result = []
                for i, (c1, c2) in enumerate(zip(addr1, addr2)):
                    if c1 == c2:
                        result.append(f"{Fore.GREEN}█{Style.RESET_ALL}")
                    else:
                        result.append(f"{Fore.RED}▁{Style.RESET_ALL}")
                return ''.join(result)
            
            print(f"Compressed:   {show_pattern_match(address, compressed)}")
            print(f"             {address}")
            print(f"             {compressed}")
            print(f"\nUncompressed: {show_pattern_match(address, uncompressed)}")
            print(f"             {address}")
            print(f"             {uncompressed}")
            
            return {
                'compressed_similarity': comp_similarity,
                'uncompressed_similarity': uncomp_similarity,
                'patterns': {
                    'input': input_pattern,
                    'compressed': comp_pattern,
                    'uncompressed': uncomp_pattern
                }
            }
        
        except Exception as e:
            print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
            return None

    def compare_address_patterns(self, addr1, addr2):
        """
        Compare patterns between two addresses
        """
        print(f"\n{Fore.CYAN}Address Pattern Comparison{Style.RESET_ALL}")
        print("=" * 50)
        
        # Split into chunks and get patterns
        def get_chunks(addr):
            return [addr[i:i+8] for i in range(0, len(addr), 8)]
        
        chunks1 = get_chunks(addr1)
        chunks2 = get_chunks(addr2)
        
        pattern1 = ''.join(chunk[0] for chunk in chunks1 if chunk)
        pattern2 = ''.join(chunk[0] for chunk in chunks2 if chunk)
        
        print(f"Address 1: {Fore.GREEN}{addr1}{Style.RESET_ALL}")
        print(f"Pattern 1: {Fore.YELLOW}{pattern1}{Style.RESET_ALL}")
        print(f"\nAddress 2: {Fore.GREEN}{addr2}{Style.RESET_ALL}")
        print(f"Pattern 2: {Fore.YELLOW}{pattern2}{Style.RESET_ALL}")
        
        # Compare first characters of each chunk
        print("\nPosition Analysis:")
        for i, (c1, c2) in enumerate(zip(pattern1, pattern2)):
            match = "✓" if c1 == c2 else "✗"
            color = Fore.GREEN if c1 == c2 else Fore.RED
            print(f"Position {i}: {color}{c1} vs {c2} {match}{Style.RESET_ALL}")

    def analyze_pattern_relationship(self, addr1, addr2):
        """
        Analyze the relationship between two address patterns
        """
        print(f"\n{Fore.CYAN}Deep Pattern Analysis{Style.RESET_ALL}")
        print("=" * 50)
        
        def get_pattern_info(addr):
            chunks = [addr[i:i+8] for i in range(0, len(addr), 8)]
            pattern = ''.join(chunk[0] for chunk in chunks if chunk)
            positions = {i: char for i, char in enumerate(pattern)}
            return {
                'pattern': pattern,
                'chunks': chunks,
                'positions': positions,
                'hex_values': [hex(ord(c))[2:] for c in pattern]
            }
        
        addr1_info = get_pattern_info(addr1)
        addr2_info = get_pattern_info(addr2)
        
        print(f"Address 1: {Fore.GREEN}{addr1[:8]}...{addr1[-8:]}{Style.RESET_ALL}")
        print(f"Pattern: {Fore.YELLOW}{addr1_info['pattern']}{Style.RESET_ALL}")
        print(f"Hex: {' '.join(addr1_info['hex_values'])}")
        
        print(f"\nAddress 2: {Fore.GREEN}{addr2[:8]}...{addr2[-8:]}{Style.RESET_ALL}")
        print(f"Pattern: {Fore.YELLOW}{addr2_info['pattern']}{Style.RESET_ALL}")
        print(f"Hex: {' '.join(addr2_info['hex_values'])}")
        
        # Compare hex differences
        print("\nPattern Differences:")
        for i in range(min(len(addr1_info['pattern']), len(addr2_info['pattern']))):
            if i in addr1_info['positions'] and i in addr2_info['positions']:
                c1 = addr1_info['positions'][i]
                c2 = addr2_info['positions'][i]
                hex_diff = abs(ord(c1) - ord(c2))
                print(f"Position {i}: {c1} vs {c2} (Diff: {hex_diff:02x})")

        return addr1_info, addr2_info

    def analyze_hex_address_markers(self, hex_string, address):
        """
        Analyze and visualize relationship between hex string segments and address markers
        """
        print(f"\n{Fore.CYAN}Hex-Address Marker Analysis{Style.RESET_ALL}")
        print("=" * 50)

        # Split hex into significant segments
        hex_segments = []
        current_segment = ""
        for i in range(0, len(hex_string), 8):
            segment = hex_string[i:i+8]
            if segment != "00000000" or current_segment:
                current_segment += segment
            hex_segments.append(segment)

        # Get address chunks
        addr_chunks = [address[i:i+8] for i in range(0, len(address), 8)]
        pattern = ''.join(chunk[0] for chunk in addr_chunks if chunk)

        # Visual alignment
        print("\nHex String Segments:")
        for i, segment in enumerate(hex_segments):
            marker = "→" if segment != "00000000" else " "
            color = Fore.YELLOW if segment != "00000000" else Fore.WHITE
            print(f"{color}{segment}{Style.RESET_ALL} {marker}")

        print("\nAddress Chunks:")
        for i, chunk in enumerate(addr_chunks):
            if i < len(pattern):
                print(f"{Fore.GREEN}{chunk}{Style.RESET_ALL} → {Fore.CYAN}{pattern[i]}{Style.RESET_ALL}")

        # Correlation map
        print("\nCorrelation Map:")
        print("=" * 30)
        
        # Find first non-zero segment
        first_nonzero = next(i for i, seg in enumerate(hex_segments) if seg != "00000000")
        
        print(f"\n{Fore.YELLOW}Hex Transitions:{Style.RESET_ALL}")
        print(f"First non-zero: Segment {first_nonzero} ({hex_segments[first_nonzero]})")
        print(f"Middle segment: {hex_segments[-2]}")
        print(f"Final segment:  {hex_segments[-1]}")
        
        print(f"\n{Fore.GREEN}Address Markers:{Style.RESET_ALL}")
        print(f"Start marker:  {pattern[0]} (Standard Bitcoin address)")
        print(f"Value marker:  {pattern[1]} (Marks first non-zero)")
        print(f"Trans marker:  {pattern[2]} (Transition point)")
        print(f"End marker:    {pattern[-1]} (Final segment)")

        # Visual correlation
        print(f"\n{Fore.CYAN}Pattern Alignment:{Style.RESET_ALL}")
        print("=" * 30)
        
        def create_arrow(length, position):
            return " " * position + "↓" + " " * (length - position - 1)

        # Hex string (abbreviated)
        hex_abbrev = "0000...{first}...{mid}...{end}".format(
            first=hex_segments[first_nonzero],
            mid=hex_segments[-2],
            end=hex_segments[-1]
        )
        
        # Show alignment
        print(f"{Fore.YELLOW}{hex_abbrev}{Style.RESET_ALL}")
        print(create_arrow(len(hex_abbrev), hex_abbrev.find(hex_segments[first_nonzero][:4])))
        print(f"{Fore.GREEN}{address}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{' '.join(pattern)}{Style.RESET_ALL}")

        return {
            'hex_segments': hex_segments,
            'address_pattern': pattern,
            'first_nonzero': first_nonzero
        }

    def extract_hex_pattern_from_address(self, address):
        """
        Extract pattern and generate corresponding hex string from Bitcoin address
        """
        print(f"\n{Fore.CYAN}Address Pattern Extraction{Style.RESET_ALL}")
        print("=" * 50)
        
        if len(address) < 26:
            print(f"{Fore.RED}Error: Invalid Bitcoin address length. Address must be at least 26 characters.{Style.RESET_ALL}")
            return None
        
        chunks = [address[i:i+8] for i in range(0, len(address), 8)]
        pattern = ''.join(chunk[0] for chunk in chunks if chunk)
        
        # Generate hex string based on pattern
        def generate_hex_string(pattern):
            # Start with leading zeros
            hex_string = ["0"] * 64  # 64 characters for 32 bytes
            
            # Map pattern positions to hex positions
            position_map = {
                0: 0,    # First character position
                1: 16,   # First non-zero position
                2: 32,   # Data block start
                3: 48    # End segment
            }
            
            # Convert pattern characters to hex values
            for i, char in enumerate(pattern):
                if i in position_map:
                    pos = position_map[i]
                    # Convert character to hex value
                    hex_val = hex(ord(char))[2:].zfill(2)
                    hex_string[pos:pos+2] = hex_val
            
            # Ensure last byte is non-zero
            if hex_string[-2:] == ["0", "0"]:
                hex_string[-2:] = "01"
            
            return "".join(hex_string)
        
        generated_hex = generate_hex_string(pattern)
        
        # Add verification step using MatrixSync
        print(f"\n{Fore.CYAN}Verification Step:{Style.RESET_ALL}")
        print("=" * 40)
        
        # Get both compressed and uncompressed addresses from generated hex
        compressed, uncompressed = self.matrix.map_address(generated_hex)
        
        print(f"\nOriginal Address:  {Fore.GREEN}{address}{Style.RESET_ALL}")
        print(f"Generated Hex:    {Fore.YELLOW}{generated_hex}{Style.RESET_ALL}")
        print(f"Mapped Compressed:   {Fore.CYAN}{compressed}{Style.RESET_ALL}")
        print(f"Mapped Uncompressed: {Fore.CYAN}{uncompressed}{Style.RESET_ALL}")
        
        # Check if either mapped address matches the pattern
        original_pattern = pattern
        compressed_pattern = ''.join(compressed[i] for i in range(0, len(compressed), 8))
        uncompressed_pattern = ''.join(uncompressed[i] for i in range(0, len(uncompressed), 8))
        
        print(f"\nPattern Analysis:")
        print(f"Original Pattern:    {Fore.GREEN}{original_pattern}{Style.RESET_ALL}")
        print(f"Compressed Pattern:  {Fore.YELLOW}{compressed_pattern}{Style.RESET_ALL}")
        print(f"Uncompressed Pattern:{Fore.YELLOW}{uncompressed_pattern}{Style.RESET_ALL}")
        
        # Calculate pattern similarity
        def pattern_similarity(p1, p2):
            return sum(a == b for a, b in zip(p1, p2)) / max(len(p1), len(p2))
        
        comp_similarity = pattern_similarity(original_pattern, compressed_pattern)
        uncomp_similarity = pattern_similarity(original_pattern, uncompressed_pattern)
        
        print(f"\nPattern Similarity:")
        print(f"Compressed:   {Fore.CYAN}{comp_similarity:.2%}{Style.RESET_ALL}")
        print(f"Uncompressed: {Fore.CYAN}{uncomp_similarity:.2%}{Style.RESET_ALL}")
        
        # Display results
        print(f"\n{Fore.GREEN}Input Address: {address}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Generated Hex: {generated_hex}{Style.RESET_ALL}")
        print("\nPattern Breakdown:")
        
        for i, (chunk, marker) in enumerate(zip(chunks, pattern)):
            print(f"\n{Fore.YELLOW}Segment {i+1}:{Style.RESET_ALL}")
            print(f"Chunk:  {Fore.CYAN}{chunk}{Style.RESET_ALL}")
            print(f"Marker: {Fore.MAGENTA}{marker}{Style.RESET_ALL}")
            hex_pos = i * 16 if i < 4 else 48
            hex_segment = generated_hex[hex_pos:hex_pos+16]
            print(f"Hex:    {Fore.GREEN}{hex_segment}{Style.RESET_ALL}")
            
            if i == 0:
                print("Meaning: Bitcoin address prefix (1)")
            elif i == 1 and len(pattern) > 1:
                print("Meaning: First non-zero hex segment position")
                print(f"Suggests: Hex starts changing after position {hex_pos}")
            elif i == 2 and len(pattern) > 2:
                print("Meaning: Main data block begins")
            else:
                print("Meaning: Continuation/end of data segment")
        
        print(f"\n{Fore.CYAN}Hex Structure Analysis:{Style.RESET_ALL}")
        print("=" * 40)
        
        # Analyze hex structure
        hex_segments = [generated_hex[i:i+16] for i in range(0, len(generated_hex), 16)]
        for i, segment in enumerate(hex_segments):
            zeros = segment.count("0")
            print(f"Segment {i+1}: {Fore.YELLOW}{segment}{Style.RESET_ALL} ({zeros} zeros)")
        
        return {
            'pattern': pattern,
            'generated_hex': generated_hex,
            'verification': {
                'compressed_address': compressed,
                'uncompressed_address': uncompressed,
                'pattern_similarity': {
                    'compressed': comp_similarity,
                    'uncompressed': uncomp_similarity
                }
            },
            'structure': {
                'pattern_hex_mapping': {
                    char: hex(ord(char))[2:].zfill(2) 
                    for char in pattern
                },
                'hex_segments': hex_segments,
                'pattern_positions': {
                    i: char for i, char in enumerate(pattern)
                }
            }
        }

def main():
    visualizer = MatrixVisualizer()
    
    print(f"\n{Fore.CYAN}Bitcoin Address Pattern Analyzer{Style.RESET_ALL}")
    print("=" * 50)
    print("1. Visualize Single Sequence")
    print("2. Compare Multiple Sequences")
    print("3. Address Sequence Analysis")
    print("4. Analyze from Bitcoin Address")
    print("5. Analyze Hex-Address Correlation")
    print("6. Analyze Hex-Address Markers")
    print("7. Extract Hex Pattern from Address")
    
    choice = input(f"\n{Fore.GREEN}Select visualization mode (1-7):{Style.RESET_ALL} ")
    
    if choice == "7":
        print("\nEnter Bitcoin address (or press Enter for example addresses)")
        address = input(f"{Fore.YELLOW}Address:{Style.RESET_ALL} ").strip()
        
        if not address:
            print(f"\n{Fore.CYAN}Example addresses:{Style.RESET_ALL}")
            examples = [
                "13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so",
                "1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9"
            ]
            for i, addr in enumerate(examples, 1):
                print(f"{i}. {addr}")
            choice = input(f"\n{Fore.GREEN}Select example (1-2) or enter custom address:{Style.RESET_ALL} ")
            address = examples[int(choice)-1] if choice.isdigit() and 1 <= int(choice) <= 2 else choice
        
        if address:
            visualizer.extract_hex_pattern_from_address(address)
        else:
            print(f"{Fore.RED}No address provided{Style.RESET_ALL}")
    
    if choice == "1":
        hex_input = input("Enter hex string (press Enter for random): ").strip()
        hex_string = hex_input if hex_input else None
        visualizer.visualize_sync_states(hex_string)
    elif choice == "2":
        visualizer.compare_sequences()
    elif choice == "3":
        hex_input = input("Enter hex string (press Enter for random): ").strip()
        hex_string = hex_input if hex_input else None
        visualizer.analyze_address_sequence(hex_string or ("0" * 63 + "1"))
    elif choice == "4":
        address = input("Enter Bitcoin address: ").strip()
        if not address:
            print(f"{Fore.RED}Error: Address required for this mode{Style.RESET_ALL}")
            return
        visualizer.analyze_from_address(address)
    elif choice == "5":
        hex_string = input("Enter hex string: ").strip()
        address = input("Enter Bitcoin address: ").strip()
        if not hex_string or not address:
            print(f"{Fore.RED}Error: Both hex string and address required{Style.RESET_ALL}")
            return
        visualizer.analyze_correlation(hex_string, address)
    elif choice == "6":
        hex_string = "000000000000000000000000000000000000000000000002832ed74f2b5e35ee"
        address = "13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so"
        visualizer.analyze_hex_address_markers(hex_string, address)
    else:
        print(f"{Fore.RED}Invalid choice{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 