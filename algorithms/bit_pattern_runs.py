#!/usr/bin/python3

def run_length_analysis(hex_string):
    """Analyze runs of 0s and 1s"""
    hex_string = hex_string.zfill(64)
    num = int(hex_string, 16)
    binary = format(num, '0256b')
    
    runs = []
    current_bit = binary[0]
    current_length = 1
    
    for bit in binary[1:]:
        if bit == current_bit:
            current_length += 1
        else:
            runs.append({
                'bit': current_bit,
                'length': current_length
            })
            current_bit = bit
            current_length = 1
    
    runs.append({
        'bit': current_bit,
        'length': current_length
    })
    
    return {
        'runs': runs,
        'longest_0_run': max((run['length'] for run in runs if run['bit'] == '0'), default=0),
        'longest_1_run': max((run['length'] for run in runs if run['bit'] == '1'), default=0),
        'total_runs': len(runs)
    } 