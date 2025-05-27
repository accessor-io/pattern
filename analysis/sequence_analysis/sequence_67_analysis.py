from math import comb
import numpy as np

def analyze_67_possibilities():
    # Total possible 256-bit numbers with 67 '1' bits
    total_possibilities = comb(256, 67)
    print(f"Total possible 256-bit numbers with 67 '1' bits: {total_possibilities}")
    
    # Read existing sequence
    with open('data/32bHex.txt', 'r') as f:
        sequence = [int(line.strip(), 16) for line in f]
    
    # Calculate ratios
    ratios = [sequence[i+1]/sequence[i] for i in range(len(sequence)-1)]
    print("\nGrowth pattern analysis:")
    print(f"Average ratio: {np.mean(ratios)}")
    print(f"Median ratio: {np.median(ratios)}")
    
    # Polynomial fit
    x = np.array(range(len(sequence)))
    y = np.log(sequence)
    z = np.polyfit(x, y, 3)
    p = np.poly1d(z)
    
    # Predict position 67
    predicted_log = p(67)
    predicted_value = np.exp(predicted_log)
    
    print(f"\nPolynomial approximation for position 67:")
    print(f"Predicted value: {predicted_value:.2e}")

if __name__ == "__main__":
    analyze_67_possibilities() 