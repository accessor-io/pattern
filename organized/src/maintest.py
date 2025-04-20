import logging
from pathlib import Path
from typing import List, Tuple
import hashlib
from collections import defaultdict

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SequenceAnalyzer:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.sequences: List[str] = []
        
    def read_sequence_file(self) -> bool:
        """
        Safely read sequences from file with proper error handling
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.sequences = [line.strip() for line in file if line.strip()]
            logger.info(f"Successfully read {len(self.sequences)} sequences from {self.file_path}")
            return True
        except FileNotFoundError:
            logger.error(f"File not found: {self.file_path}")
            return False
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            return False

    def analyze_pattern(self) -> Tuple[dict, list]:
        """
        Analyze sequence patterns and return statistics
        """
        if not self.sequences:
            logger.warning("No sequences to analyze")
            return {}, []

        pattern_stats = defaultdict(int)
        collision_check = set()
        collisions = []

        for sequence in self.sequences:
            # Generate secure hash for pattern comparison
            pattern_hash = hashlib.sha256(sequence.encode()).hexdigest()
            
            # Check for collisions
            if pattern_hash in collision_check:
                collisions.append(sequence)
            collision_check.add(pattern_hash)
            
            # Analyze pattern characteristics
            pattern_stats['total_length'] += len(sequence)
            pattern_stats['unique_chars'] = len(set(sequence))

        logger.info(f"Analysis complete. Found {len(collisions)} collisions")
        return dict(pattern_stats), collisions

    def write_analysis_results(self, output_file: str) -> bool:
        """
        Write analysis results to output file
        """
        try:
            stats, collisions = self.analyze_pattern()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("Sequence Analysis Results\n")
                f.write("========================\n\n")
                
                # Write statistics
                f.write("Pattern Statistics:\n")
                for key, value in stats.items():
                    f.write(f"{key}: {value}\n")
                
                # Write collision information
                f.write("\nCollisions Found:\n")
                for collision in collisions:
                    f.write(f"- {collision}\n")
                
            logger.info(f"Analysis results written to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing results: {str(e)}")
            return False

def main():
    # Initialize analyzer with input file
    analyzer = SequenceAnalyzer("data/32bHex.txt")
    
    # Read and analyze sequences
    if analyzer.read_sequence_file():
        # Write results to output file
        analyzer.write_analysis_results("analysis_results.txt")
    else:
        logger.error("Failed to process sequence file")

if __name__ == "__main__":
    main()