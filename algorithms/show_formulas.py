#!/usr/bin/env python3
import sys
sys.path.append('.')
from key_sequence_generator import analyze_sequence_transformations

def show_solution_formulas():
    print("=== ANALYZING BITCOIN PUZZLE SOLUTION FORMULAS ===\n")
    
    # Run the comprehensive analysis
    result = analyze_sequence_transformations(max_positions=68, verbose=False)
    
    print("\n=== SOLUTION FORMULAS FOR POSITIONS 1-68 ===\n")
    
    # Track pattern phases
    simple_arithmetic = []
    multiplicative = []
    bitshift = []
    no_formula = []
    
    for pos in sorted(range(2, 69)):
        if pos in result and result[pos]['matching_formulas']:
            formulas = result[pos]['matching_formulas']
            primary_formula = formulas[0] if formulas else 'None'
            
            # Categorize the formula type
            if any(word in primary_formula.lower() for word in ['<<', '>>', 'shift', 'rot']):
                bitshift.append(pos)
                category = "🔧 BITSHIFT"
            elif '*' in primary_formula and ('+' in primary_formula or '-' in primary_formula):
                multiplicative.append(pos)
                category = "⚡ MULT+ADD"
            elif '+' in primary_formula or '-' in primary_formula:
                simple_arithmetic.append(pos)
                category = "➕ ARITH"
            else:
                category = "🔍 OTHER"
            
            print(f"Position {pos:2d}: {primary_formula:<30} [{category}]")
            
            # Show alternative formulas if they exist
            if len(formulas) > 1:
                for alt_formula in formulas[1:3]:  # Show up to 2 alternatives
                    print(f"           Alt: {alt_formula}")
        else:
            no_formula.append(pos)
            print(f"Position {pos:2d}: ❌ No formula found")
    
    # Summary statistics
    print(f"\n=== PATTERN ANALYSIS SUMMARY ===")
    print(f"Simple Arithmetic (k ± constant): {len(simple_arithmetic)} positions")
    print(f"  Positions: {simple_arithmetic}")
    
    print(f"\nMultiplicative + Addition: {len(multiplicative)} positions") 
    print(f"  Positions: {multiplicative}")
    
    print(f"\nBitshift Operations: {len(bitshift)} positions")
    print(f"  Positions: {bitshift}")
    
    print(f"\nNo Formula Found: {len(no_formula)} positions")
    if no_formula:
        print(f"  Positions: {no_formula}")
    
    print(f"\nTotal Solved: {68 - len(no_formula)}/67 transitions")
    print(f"Success Rate: {((68 - len(no_formula))/67)*100:.1f}%")

if __name__ == "__main__":
    show_solution_formulas() 