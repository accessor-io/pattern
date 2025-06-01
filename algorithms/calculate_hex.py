from decimal import Decimal, getcontext

# Set precision for Decimal operations
getcontext().prec = 500

def hex_padded(n, length=64):
    """Convert an integer to a zero-padded hexadecimal string."""
    return format(n, 'X').zfill(length)

# Hexadecimal values for a(65) and a(70)
a65_hex = '1A838B13505B26867'
a70_hex = '349B84B6431A6C4EF1'

# Convert hexadecimal to Decimal
A = Decimal(int(a65_hex, 16))
B = Decimal(int(a70_hex, 16))

# Calculate the common ratio
m = (B / A) ** (Decimal(1) / Decimal(5))

# Generate and print a(n) for n from 65 to 160
results = []
for n in range(65, 161):
    exponent = Decimal(n - 65)
    an = A * (m ** exponent)
    an_int = int(an.to_integral_value(rounding='ROUND_HALF_UP'))
    an_hex = hex_padded(an_int, 64)
    results.append(f'a({n}) = {an_hex}')

# Output all results
for result in results:
    print(result)