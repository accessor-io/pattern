from math import comb

# Calculate total possibilities for 256-bit numbers with 67 '1' bits
total = comb(256, 67)
print(f"Total possible 256-bit numbers with 67 '1' bits: {total}")

# Read sequence
with open('data/32bHex.txt', 'r') as f:
    sequence = [int(line.strip(), 16) for line in f]

# Calculate growth ratios
ratios = [sequence[i+1]/sequence[i] for i in range(len(sequence)-1)]
avg_ratio = sum(ratios)/len(ratios)

print(f"\nAverage growth ratio: {avg_ratio}")
print(f"Number of values in sequence: {len(sequence)}")
print(f"\nRatio of total space to valid numbers: 1:{2**256//total}") 