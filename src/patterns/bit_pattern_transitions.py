#!/usr/bin/python3

def transition_analysis(hex_string):
    """Analyze transitions between bit patterns"""
    hex_string = hex_string.zfill(64)
    num = int(hex_string, 16)
    binary = format(num, '0256b')
    
    transitions = {
        '00->01': 0, '00->10': 0, '00->11': 0,
        '01->00': 0, '01->10': 0, '01->11': 0,
        '10->00': 0, '10->01': 0, '10->11': 0,
        '11->00': 0, '11->01': 0, '11->10': 0
    }
    
    for i in range(0, 254, 2):
        current = binary[i:i+2]
        next_pattern = binary[i+2:i+4]
        transition = f"{current}->{next_pattern}"
        if transition in transitions:
            transitions[transition] += 1
    
    return transitions 