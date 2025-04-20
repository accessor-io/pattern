def process_hex_pairs(output_file="hex_pairs.txt", truncated_file="truncated_chars.txt"):
    """
    Processes KNOWN_SOLUTIONS values to:
    1. Write hex pairs to output_file
    2. Record truncated characters from odd-length hex strings to truncated_file
    """
    truncated_data = []
    
    with open(output_file, 'w') as pairs_file, open(truncated_file, 'w') as trunc_file:
        pairs_file.write("Index | Hex Pairs\n")
        pairs_file.write("------|----------\n")
        
        trunc_file.write("Index | Truncated Char | Original Hex\n")
        trunc_file.write("------|----------------|-------------\n")
        
        for idx in sorted(KNOWN_SOLUTIONS):
            value = KNOWN_SOLUTIONS[idx]
            hex_str = f"{value:x}".lower()  # Convert to lowercase hex without 0x
            
            # Handle odd-length hex strings
            truncated_char = None
            if len(hex_str) % 2 != 0:
                truncated_char = hex_str[-1]
                hex_str = hex_str[:-1]
                truncated_data.append((idx, truncated_char, f"{value:x}"))
            
            # Split into pairs
            pairs = [hex_str[i:i+2] for i in range(0, len(hex_str), 2)] if hex_str else []
            
            # Write to pairs file
            pairs_line = f"{idx:5} | {', '.join(pairs) or 'None'}"
            pairs_file.write(pairs_line + '\n')
            
        # Write truncated characters
        for idx, char, original in truncated_data:
            trunc_line = f"{idx:5} | {char:14} | {original}"
            trunc_file.write(trunc_line + '\n')

# Usage
process_hex_pairs()