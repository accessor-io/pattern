#!/usr/bin/env python3

def analyze_hex_sequence(input_file, output_file):
    try:
        # Read from input file
        with open(input_file, 'r') as infile:
            hex_strings = [line.strip() for line in infile]

        # Write analysis to output file
        with open(output_file, 'w') as outfile:
            outfile.write(f"Analysis of {input_file}:\n")
            outfile.write("Index  Decimal               Hex(last 8)     Diff from prev    Ratio\n")
            outfile.write("-" * 75 + "\n")

            prev = 0
            for i, hex_str in enumerate(hex_strings):
                current = int(hex_str, 16)
                diff = current - prev if i > 0 else 0
                ratio = current/prev if prev != 0 else 0
                
                line = f"{i:2d}     {current:<20} {hex_str[-8:]}        "
                if i > 0:
                    line += f"{diff:<15} {ratio:.3f}\n"
                else:
                    line += "    -              -\n"
                    
                outfile.write(line)
                prev = current
                
        print(f"Analysis completed! Saved to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Could not find input file {input_file}")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python3 analyze_sequence.py <input_file> <output_file>")
        print("Example: python3 analyze_sequence.py data/32bHex.txt analysis.txt")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    analyze_hex_sequence(input_file, output_file) 