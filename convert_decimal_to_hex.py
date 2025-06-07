input_file = 'all_wolfram_rules_combined.txt'
output_file = 'all_wolfram_rules_combined_hex.txt'

with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    for line in infile:
        if 'Decimall:' in line:
            parts = line.split('Decimall:')
            before = parts[0]
            after = parts[1].strip()
            # Extract the first number after 'Decimall:'
            num_str = ''
            for c in after:
                if c.isdigit():
                    num_str += c
                else:
                    break
            if num_str:
                hex_str = hex(int(num_str))
                # Replace only the first occurrence of the decimal number
                new_after = after.replace(num_str, hex_str, 1)
                new_line = before + 'Decimall:' + new_after + '\n'
                outfile.write(new_line)
            else:
                outfile.write(line)
        else:
            outfile.write(line) 