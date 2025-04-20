#!/usr/bin/python3

def math_analysis(hex_string):
    """Analyze mathematical properties"""
    num = int(hex_string, 16)
    binary = bin(num)[2:].zfill(256)
    
    return {
        'is_power_of_two': (num & (num - 1) == 0) if num != 0 else False,
        'trailing_zeros': len(binary) - len(binary.rstrip('0')),
        'leading_zeros': len(binary) - len(binary.lstrip('0')),
        'prime_factors': get_prime_factors(num),
        'is_palindrome': binary == binary[::-1],
        'modulo_properties': {
            'mod_2': num % 2,
            'mod_4': num % 4,
            'mod_8': num % 8,
            'mod_16': num % 16
        }
    } 