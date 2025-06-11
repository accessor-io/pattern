import argparse
from .core import Puzzle66Solver
from pathlib import Path
from typing import List
from colorsys import hsv_to_rgb

def hex_int(value: str) -> int:
    """Convert hex string to integer"""
    return int(value, 0)  # 0 base auto-detects hex from 0x prefix

def print_hex_pairs(sequence: List[int]):
    """Color each hex character with spectrum position and term fading"""
    print("\nFull Spectrum Character Map:")
    for i, value in enumerate(sequence):
        hex_str = f"{value:064x}"  # 64 chars for 256-bit values
        colored_chars = []
        
        # Calculate vertical fade (darker to lighter)
        v_fade = 0.3 + 0.7 * (i/len(sequence))
        
        for j, char in enumerate(hex_str):
            # Horizontal spectrum position (0-63 characters)
            h_fade = j / 63
            
            # Convert to RGB with dual fading
            r = int(255 * (1 - h_fade) * v_fade)
            g = int(255 * h_fade * v_fade)
            b = int(255 * (0.5 - abs(0.5 - h_fade)) * v_fade)
            
            # Create color code and colored character
            color_code = f"\033[38;2;{r};{g};{b}m"
            colored_chars.append(f"{color_code}{char}\033[0m")
        
        print(f"Term {i+1:>2}: {''.join(colored_chars)}")

def clear_transformation_cache():
    """Clear the transformation cache"""
    from .core import Puzzle66Solver
    Puzzle66Solver._apply_transformation.cache_clear()

def main():
    parser = argparse.ArgumentParser(description='Bitcoin Puzzle 66 Solver')
    parser.add_argument('start', type=hex_int, 
                      help='Starting value (hex format: 0x1a8...)')
    parser.add_argument('-l', '--length', type=int, default=66,
                      help='Number of terms to generate (1-66)')
    parser.add_argument('--no-cache', action='store_true',
                      help='Disable caching mechanism')
    parser.add_argument('--cache-path', type=Path, default=Path.home()/'.btc_puzzle_cache',
                      help='Custom cache directory path')
    parser.add_argument('--color', action='store_true',
                      help='Display hex pairs with position-based coloring')
    args = parser.parse_args()
    
    solver = Puzzle66Solver(args.start)
    sequence = solver.solve_sequence(args.length)
    
    if args.no_cache:
        clear_transformation_cache()
    
    if args.color:
        print_hex_pairs(sequence)

if __name__ == "__main__":
    main() 