import sys
import logging
from crypto_data import CRYPTO_MAPPINGS
from command_protocol import CommandProtocol
from helix_visualizer import visualize_helix_pattern
from helix_chain_mapper import map_command_paths
from crypto_master_decoder import CryptoDecoder
from crypto_chain_analyzer import analyze_crypto_chains

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_system():
    """Initialize all system components"""
    logger.info("Initializing system components...")
    
    # Initialize command protocol
    protocol = CommandProtocol()
    
    # Initialize crypto decoder
    decoder = CryptoDecoder()
    initial_state = decoder.initialize_from_master()
    
    logger.info(f"System initialized with master key: {initial_state['address']}")
    return protocol, decoder

def run_analysis_pipeline():
    """Run the complete analysis pipeline"""
    logger.info("Starting analysis pipeline...")
    
    # Get the first address for analysis
    master_address = CRYPTO_MAPPINGS[0][0]
    
    # Run helix pattern analysis
    patterns = visualize_helix_pattern(master_address)
    logger.info(f"Generated {len(patterns)} helix patterns")
    
    # Map command paths
    paths = map_command_paths(master_address)
    logger.info(f"Mapped {len(paths)} possible command paths")
    
    # Analyze crypto chains
    analyze_crypto_chains()
    
    return patterns, paths

def main():
    try:
        # Initialize system
        protocol, decoder = initialize_system()
        
        # Run analysis pipeline
        patterns, paths = run_analysis_pipeline()
        
        # Interpret protocol
        protocol.interpret_protocol()
        
        logger.info("System startup complete. Ready for commands.")
        
        # Keep system running
        while True:
            command = input("Enter command (or 'exit' to quit): ")
            if command.lower() == 'exit':
                break
            
            # Process command through protocol
            protocol.interpret_protocol()
            
    except KeyboardInterrupt:
        logger.info("System shutdown initiated by user")
    except Exception as e:
        logger.error(f"Error during system execution: {e}")
        sys.exit(1)
    finally:
        logger.info("System shutdown complete")

if __name__ == "__main__":
    main() 