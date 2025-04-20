import math
from decimal import Decimal, getcontext
getcontext().prec = 50  # High precision for calculations

def analyze_advanced_patterns():
    # Read sequence
    with open('organized/data/32bHex.txt') as f:
        numbers = [int(line.strip(), 16) for line in f]
    
    print("Advanced Pattern Analysis")
    print("=" * 50)
    
    # 1. Check for polynomial growth patterns
    print("\n1. Polynomial Growth Analysis:")
    diffs = []
    current = numbers
    for order in range(1, 5):
        next_diffs = []
        for i in range(1, len(current)):
            next_diffs.append(current[i] - current[i-1])
        diffs.append(next_diffs)
        current = next_diffs
        
        # Check if differences stabilize
        if len(next_diffs) > 3:
            variance = sum((x - sum(next_diffs)/len(next_diffs))**2 for x in next_diffs) / len(next_diffs)
            print(f"Order {order} difference variance: {variance}")
    
    # 2. Look for recurrence relations
    print("\n2. Recurrence Relation Analysis:")
    for window in range(2, 6):
        for start in range(len(numbers) - window):
            subsequence = numbers[start:start+window]
            next_val = numbers[start+window]
            # Try to find linear combination
            coeffs = []
            try:
                # Simple linear combination check
                total = sum(subsequence)
                if abs(next_val - total) < total * 0.1:
                    print(f"Possible recurrence at pos {start}, window {window}")
                    print(f"Values: {[hex(x) for x in subsequence]} -> {hex(next_val)}")
            except:
                continue
    
    # 3. Analyze bit patterns
    print("\n3. Bit Pattern Analysis:")
    for i in range(min(10, len(numbers))):
        num = numbers[i]
        bits = bin(num)[2:]
        ones = bits.count('1')
        zeros = len(bits) - ones
        leading_zeros = len(bits) - len(bits.lstrip('0'))
        print(f"\nPosition {i}:")
        print(f"Number: {hex(num)}")
        print(f"Bit length: {len(bits)}")
        print(f"1s/0s ratio: {ones}/{zeros}")
        print(f"Leading zeros: {leading_zeros}")
    
    # 4. Check for multiplicative persistence patterns
    print("\n4. Multiplicative Persistence Analysis:")
    def digit_product(n):
        prod = 1
        while n > 0:
            prod *= (n % 16)
            n //= 16
        return prod
    
    for i in range(min(5, len(numbers))):
        num = numbers[i]
        steps = 0
        while num >= 16:
            num = digit_product(num)
            steps += 1
        print(f"Position {i} persistence: {steps}")
    
    # 5. Analyze digit frequency patterns
    print("\n5. Hexadecimal Digit Frequency Analysis:")
    digit_freq = {hex(i)[2:]: 0 for i in range(16)}
    total_digits = 0
    
    for num in numbers[:10]:  # First 10 numbers
        hex_str = hex(num)[2:]
        for digit in hex_str:
            digit_freq[digit] += 1
            total_digits += 1
    
    print("\nDigit frequencies in first 10 numbers:")
    for digit, freq in digit_freq.items():
        if freq > 0:
            print(f"Digit {digit}: {freq/total_digits:.3f}")

if __name__ == '__main__':
    analyze_advanced_patterns() 