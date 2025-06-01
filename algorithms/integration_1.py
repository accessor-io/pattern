"""
Integration module for Bitcoin key search

This module provides functions to integrate the advanced Bitcoin-specific
candidate generation with the main continuous adaptive search algorithm.
"""

import sys
import os
import logging

# Add parent directory to path to allow imports from main module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Import functions from main module (dynamically)
    import importlib.util
    spec = importlib.util.spec_from_file_location("search", os.path.join(parent_dir, "68_continuous_adaptive_search.py"))
    search = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(search)
    
    # Import the candidate generator
    from bitcoin_utils.candidate_generator import generate_bitcoin_focused_candidates
    
    logger.info("Successfully imported main search module and candidate generator")
except Exception as e:
    logger.error(f"Error importing modules: {e}")
    raise

def generate_enhanced_candidates(count, base_candidates=None):
    """
    Generate enhanced candidates using both the original algorithm and our
    Bitcoin-specific knowledge.
    
    Args:
        count: Number of candidates to generate
        base_candidates: Optional list of existing candidates
        
    Returns:
        List of high-quality candidates
    """
    # Get the previous term constant from the main module
    prev_term = search.PREV_TERM_67_INT
    
    # Generate Bitcoin-focused candidates
    bitcoin_candidates = generate_bitcoin_focused_candidates(
        count=count//2,  # Use half the count for Bitcoin-specific candidates
        prev_term=prev_term,
        base_candidates=base_candidates
    )
    
    # Generate other candidates using the original function
    # Make sure to avoid duplicates
    original_candidates = search.generate_high_quality_candidates(
        count=count - len(bitcoin_candidates),
        base_candidates=[c for c in base_candidates if c not in bitcoin_candidates] if base_candidates else None
    )
    
    # Combine and deduplicate
    all_candidates = list(bitcoin_candidates)
    for c in original_candidates:
        if c not in all_candidates:
            all_candidates.append(c)
    
    logger.info(f"Generated {len(all_candidates)} enhanced candidates: {len(bitcoin_candidates)} Bitcoin-specific, {len(original_candidates)} using original algorithm")
    
    return all_candidates[:count]

def patch_search_algorithm():
    """
    Patch the main search algorithm to use our enhanced candidate generator.
    This dynamically modifies the generate_high_quality_candidates function
    in the main module.
    """
    try:
        # Store the original function
        original_generator = search.generate_high_quality_candidates
        
        # Replace with our enhanced function
        search.generate_high_quality_candidates = generate_enhanced_candidates
        
        logger.info("Successfully patched search algorithm with enhanced candidate generator")
        return True
    except Exception as e:
        logger.error(f"Error patching search algorithm: {e}")
        return False

if __name__ == "__main__":
    print("Patching search algorithm with enhanced candidate generator...")
    success = patch_search_algorithm()
    print(f"Patch {'successful' if success else 'failed'}")
    
    if success:
        print("You can now run the main search algorithm with enhanced candidate generation.")
        print("Example: python 68_continuous_adaptive_search.py --duration 24") 