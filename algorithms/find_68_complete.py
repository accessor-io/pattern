import json
import logging
import os
import sys
from typing import Dict, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import from there
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
logger.info(f"Added to path: {parent_dir}")

# Import the Position67Analyzer from the correct location
try:
    from find_67_with_hex import Position67Analyzer
    logger.info(f"Successfully imported Position67Analyzer")
except ImportError as e:
    logger.error(f"Failed to import Position67Analyzer: {e}")
    # Explicitly set the full path if the relative import fails
    analysis_path = '/home/dot/pattern/organized/analysis'
    sys.path.append(analysis_path)
    logger.info(f"Added absolute path to sys.path: {analysis_path}")
    logger.info(f"Current sys.path: {sys.path}")
    try:
        from find_67_with_hex import Position67Analyzer
        logger.info(f"Successfully imported Position67Analyzer after adding absolute path")
    except ImportError as e:
        logger.error(f"Still failed to import Position67Analyzer: {e}")
        raise

class Position68Analyzer(Position67Analyzer):
    def __init__(self):
        super().__init__()
        # Update known values with position 67
        self.known_values[67] = 0x730fc235c1942c1ae
        self.target_position = 68
        
    def analyze_constraints(self) -> Dict:
        """Adjust constraints for position 68"""
        constraints = super().analyze_constraints()
        
        # Tighten constraints based on position 67's properties
        constraints.update({
            'min_bit_changes': 256 * 0.15,  # Reduced from 25%
            'max_bit_changes': 256 * 0.35,  # Reduced from 75%
            'min_byte_changes': 4,          # Reduced from 8
            'max_byte_changes': 12,         # Reduced from 24
            'growth_rate': {
                'min': 1.1,                 # Reduced from 1.2
                'max': 1.5                  # Reduced from 2.0
            }
        })
        return constraints
        
    def analyze_bit_patterns(self) -> Dict:
        """Analyze patterns between 67 and 70"""
        val67 = self.known_values[67]
        val70 = self.known_values[70]
        
        bin67 = format(val67, 'b').zfill(256)
        bin70 = format(val70, 'b').zfill(256)
        
        # Analyze changes
        changes = []
        patterns = []
        current_pattern = []
        
        for i in range(256):
            if bin67[i] != bin70[i]:
                changes.append(i)
                current_pattern.append(1)
            else:
                current_pattern.append(0)
                
            if len(current_pattern) == 8:
                patterns.append(current_pattern)
                current_pattern = []
                
        # Analyze byte-level changes
        bytes67 = [bin67[i:i+8] for i in range(0, 256, 8)]
        bytes70 = [bin70[i:i+8] for i in range(0, 256, 8)]
        
        byte_changes = []
        for i in range(32):
            if bytes67[i] != bytes70[i]:
                byte_changes.append({
                    'position': i,
                    'from': bytes67[i],
                    'to': bytes70[i],
                    'changes': sum(1 for j in range(8) if bytes67[i][j] != bytes70[i][j])
                })
                
        analysis = {
            'bit_changes': {
                'positions': changes,
                'total': len(changes),
                'ratio': len(changes)/256
            },
            'byte_changes': {
                'changes': byte_changes,
                'total': len(byte_changes),
                'ratio': len(byte_changes)/32
            },
            'patterns': patterns
        }
        
        with open('analysis_68/bit_patterns.json', 'w') as f:
            json.dump(analysis, f, indent=2)
            
        return analysis
        
    def generate_candidates(self) -> None:
        """Generate candidates for position 68"""
        patterns = self.analyze_bit_patterns()
        constraints = self.analyze_constraints()
        
        # Expected changes between 67 and 68
        expected_changes = int(patterns['bit_changes']['total'] * 0.33)
        logging.info(f"Expecting {expected_changes} bit changes")
        
        # Generate candidates from position 67
        bin67 = format(self.known_values[67], 'b').zfill(256)
        # ... rest of generation logic similar to parent class but using 67 as base ...
        
    def find_position_68(self) -> Optional[int]:
        """Find the value for position 68"""
        logging.info("Starting comprehensive search for position 68")
        
        # Update analysis directory
        self.analysis_dir = 'analysis_68'
        os.makedirs(self.analysis_dir, exist_ok=True)
        
        # Perform analysis and candidate generation
        self.analyze_sequence_properties()
        self.analyze_bit_patterns()
        self.generate_candidates()
        
        # ... rest of validation logic similar to parent class ... 
        
        # After finding the value, print addresses
        if valid_candidates:
            value = min(valid_candidates)
            logging.info(f"Selected value for position 68: 0x{value:x}")
            
            # Print compressed and non-compressed addresses
            self.print_addresses(value)
            
            return value
        else:
            logging.warning("No valid candidates found")
            return None
            
    def print_addresses(self, value: int) -> None:
        """Print both compressed and non-compressed addresses for the value"""
        # Convert value to hex string (remove '0x' prefix)
        hex_value = format(value, 'x')
        
        # Import the necessary library for address generation
        try:
            import hashlib
            from base58 import b58encode
            
            # Generate private key from hex
            private_key = bytes.fromhex(hex_value.zfill(64))
            
            # Create compressed and uncompressed public keys
            # Note: This is a simplified implementation
            # Compressed address
            compressed_prefix = b'\x02' if (value % 2) == 0 else b'\x03'
            compressed_public_key = compressed_prefix + hashlib.sha256(private_key).digest()[:32]
            compressed_hash = hashlib.new('ripemd160', hashlib.sha256(compressed_public_key).digest()).digest()
            compressed_address = b'\x00' + compressed_hash
            compressed_checksum = hashlib.sha256(hashlib.sha256(compressed_address).digest()).digest()[:4]
            compressed_address += compressed_checksum
            compressed_address_str = b58encode(compressed_address).decode('utf-8')
            
            # Uncompressed address
            uncompressed_prefix = b'\x04'
            uncompressed_public_key = uncompressed_prefix + hashlib.sha256(private_key).digest()[:64]
            uncompressed_hash = hashlib.new('ripemd160', hashlib.sha256(uncompressed_public_key).digest()).digest()
            uncompressed_address = b'\x00' + uncompressed_hash
            uncompressed_checksum = hashlib.sha256(hashlib.sha256(uncompressed_address).digest()).digest()[:4]
            uncompressed_address += uncompressed_checksum
            uncompressed_address_str = b58encode(uncompressed_address).decode('utf-8')
            
            # Print the addresses
            print(f"\nAddresses for position 68 value:")
            print(f"Compressed address:   {compressed_address_str}")
            print(f"Uncompressed address: {uncompressed_address_str}")
            
            # Also save to file
            with open('analysis_68/addresses.json', 'w') as f:
                json.dump({
                    'position': 68,
                    'value_hex': hex(value),
                    'compressed_address': compressed_address_str,
                    'uncompressed_address': uncompressed_address_str
                }, f, indent=2)
                
            logging.info(f"Addresses saved to analysis_68/addresses.json")
            
        except ImportError:
            logging.warning("Could not import required libraries for address generation")
            print("\nCould not generate addresses. Please install required libraries:")
            print("pip install base58")

if __name__ == "__main__":
    logger.info("Starting Position68Analyzer")
    try:
        # Create an instance of the analyzer
        analyzer = Position68Analyzer()
        
        # Run the analysis to find position 68
        result = analyzer.find_position_68()
        
        if result:
            print(f"\nSuccess! Found value for position 68: {hex(result)}")
            # Check if the address matches our target
            analyzer.print_addresses(result)
        else:
            print("\nNo valid candidate found for position 68")
    except Exception as e:
        logger.error(f"Error running Position68Analyzer: {e}")
        import traceback
        traceback.print_exc() 