import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import hashlib

# Input data (first 70 values)
KH = [
    "0x1", "0x3", "0x7", "0x8", "0x15", "0x31", "0x4C", "0xE0", "0x1D3", "0x202",
    "0x483", "0xA7B", "0x1460", "0x2930", "0x68f3", "0xc936", "0x1764f", "0x3080d",
    "0x57491", "0xd2c55", "0x1ba534", "0x2de40f", "0xc2a04", "0x1fa5ee5", "0x340326e",
    "0x6ac3875", "0xd916ce8", "0x172551f", "0xd94cd64", "0x7d4fe747", "0x862a62e",
    "0x1a96ca8d8", "0x966200", "0x34a03911d", "0x4aed21170", "0xde820a7c",
    "0x17577a36a", "0x22382fecd", "0x465f83ee2", "0x9e4933dd0", "0x153859acc5b",
    "0x221c58d8f", "0x3b627c591", "0x2b335a0f", "0x12fca143c05", "0x2ec18388d544",
    "0x61cb533cba", "0xade6d7ce3b9b", "0x174176b01f54d", "0x2bd43c2e9354",
    "0x75070a1a309d4", "0x8efae164cb9e3c", "0x185788e47e326c", "0x236f6d3ad1f43",
    "0x1f5bf87e67e114", "0x18b63ac4ffdf", "0x1eb25c90795d61c", "0x2b79852183a21",
    "0x7436cbb87cab44f", "0xfc07a1182367bbe", "0x13c96a3742f64906",
    "0x363d541eb611abee", "0x7cce5efdaccf6808", "0x70f1127b09112d4",
    "0x1a838b13505b26867", "0x2832ed74f2b5e35ee", "0x730fc232c1942c1ac",
    "0x6ebb3940cd6c1491", "0x101d83275f2bc7e0c", "0x349b84b6431a6c4f1"
]

# Known future mapping (every 5 indices after 70)
KNOWN_FUTURE = {
    60: "0x7cce5efdaccf6808",
    65: "0x1a838b13505b26867",
    70: "0x349b84b6431a6c4f1",
    75: "0x4c5ce114686a1336e07",
    80: "0xea1a5c66dcc11b5ad180",
    85: "0x11720c4f018d51b8cebba8",
    90: "0x2ce00bb2136a445c71e85bf",
    95: "0x527a792b183c7f64a0e8b1f4",
    100: "0xaf55fc59c335c8ec67ed24826",
    105: "0x16f14fc2054cd87ee6396b33df3",
    110: "0x35c0d7234df7deb0f20cf7062444",
    115: "0x60f4d11574f5deee49961d9609ac6",
    120: "0xb10f22572c497a836ea187f2e1fc23",
    125: "0x1c533b6bb7f0804e09960225e44877ac",
    130: "0x33e7665705359f04f28b88cf897c603c9"
}

# Mapping from index to value for all known keys (1-based index)
ALL_KNOWN = {i+1: KH[i] for i in range(len(KH))}
ALL_KNOWN.update(KNOWN_FUTURE)

PREFIX_BYTES = 10
KNOWN_INDEXES = sorted(ALL_KNOWN.keys())
MAX_BITS = 256
MAX_VALUE = 2**MAX_BITS - 1

def hex_xor(a, b):
    if isinstance(a, str):
        a = int(a, 16)
    if isinstance(b, str):
        b = int(b, 16)
    return a ^ b

def format_prediction(val):
    return f"0x{val:064x}"

def prefix_bytes(val, n=PREFIX_BYTES):
    hex_str = format_prediction(val)[2:]
    return hex_str[:n*2]

def build_difference_table():
    table = []
    current_level = list(KH)
    table.append([int(x, 16) for x in current_level])
    while len(current_level) > 1:
        next_level = [hex_xor(current_level[i], current_level[i + 1]) for i in range(len(current_level) - 1)]
        if not next_level:
            break
        table.append(next_level)
        current_level = next_level
    return table

def analyze_patterns():
    values = [int(x, 16) for x in KH]
    diff_table = build_difference_table()
    xor_diffs = diff_table[1]
    bit_patterns = []
    for i in range(len(values)-1):
        xor_val = values[i] ^ values[i+1]
        bit_patterns.append(xor_val.bit_length() - 1 if xor_val else 0)
    
    # Analyze transition from index 70 to 75
    if 70 in ALL_KNOWN and 75 in ALL_KNOWN:
        last_value = int(ALL_KNOWN[70], 16)
        known_75 = int(ALL_KNOWN[75], 16)
        xor_to_75 = last_value ^ known_75
        bit_diff_75 = bin(xor_to_75).count('1')
        print(f"Transition 70->75: XOR diff = {hex(xor_to_75)}, Bit length diff = {bit_diff_75}")
    
    return {
        'values': values,
        'xor_diffs': xor_diffs,
        'bit_patterns': bit_patterns,
        'diff_table': diff_table
    }

def hash_prediction(start_value, num_predictions, use_index=False, start_index=1):
    preds = []
    current = start_value
    for i in range(num_predictions):
        if use_index:
            input_str = str(start_index + i).encode()
        else:
            input_str = format_prediction(current).encode()
        hash_val = int(hashlib.sha256(input_str).hexdigest(), 16)
        preds.append(hash_val % MAX_VALUE)
        current = hash_val
    return preds

def mask_to_index(val, idx):
    max_val = (1 << min(8 * idx, MAX_BITS)) - 1
    return val & max_val

def predict_entire_chain(analysis, total_indexes=160):
    known_map = ALL_KNOWN.copy()
    chain = []
    avg_xor = sum(analysis['xor_diffs']) // len(analysis['xor_diffs']) if analysis['xor_diffs'] else 0
    
    for idx in range(1, total_indexes + 1):
        if idx in known_map:
            chain.append(mask_to_index(int(known_map[idx], 16), idx))
        else:
            prev_idx = idx - 1
            prev_val = chain[prev_idx - 1] if prev_idx >= 1 else 1
            # Use a rotating XOR difference from xor_diffs to avoid repetition
            diff_idx = (idx - 1) % len(analysis['xor_diffs']) if analysis['xor_diffs'] else 0
            next_value = (prev_val ^ analysis['xor_diffs'][diff_idx]) % MAX_VALUE
            next_value = mask_to_index(next_value, idx)
            chain.append(next_value)
    
    # 5-step transition from 70 to 75
    if 70 in known_map and 75 in known_map:
        val_70 = chain[69]  # Index 70 (0-based 69)
        val_75 = int(known_map[75], 16)
        xor_total = val_70 ^ val_75
        # Distribute XOR over 5 steps using a fraction of xor_total
        step_xor = xor_total // 5
        for i in range(71, 75):
            chain[i-1] = (chain[i-2] ^ step_xor) % MAX_VALUE
        chain[74] = val_75  # Ensure index 75 is exact
    return chain

def analyze_prediction_accuracy_full(chain):
    print("\nPrediction Analysis for Known Future Values (Full Chain):")
    print("---------------------------------------------------------")
    prefix_matches = []
    for idx in KNOWN_INDEXES:
        if idx not in KNOWN_FUTURE:
            continue
        hex_val = KNOWN_FUTURE[idx]
        known_val = int(hex_val, 16)
        pred_idx = idx - 1
        if 0 <= pred_idx < len(chain):
            aligned_match = chain[pred_idx]
            aligned_prefix = prefix_bytes(aligned_match)
            known_prefix = prefix_bytes(known_val)
            aligned_prefix_match = sum(a == b for a, b in zip(aligned_prefix, known_prefix))
            prefix_matches.append(aligned_prefix_match)
            xor_diff = aligned_match ^ known_val
            total_bits = max(aligned_match.bit_length(), known_val.bit_length())
            matching_bits = total_bits - bin(xor_diff).count('1')
            similarity_percent = (matching_bits / total_bits) * 100 if total_bits > 0 else 0
            print(f"\nAligned prediction for index {idx} (chain[{pred_idx}]):")
            print(f"Predicted: {format_prediction(aligned_match)}")
            print(f"Actual:    {hex_val}")
            print(f"Prefix match: {aligned_prefix_match}/{PREFIX_BYTES*2} hex chars")
            print(f"Predicted prefix: {aligned_prefix}")
            print(f"Actual prefix:    {known_prefix}")
            print(f"Bit similarity: {similarity_percent:.2f}%")
            print(f"Match: {aligned_match == known_val}")
        best_match = None
        best_match_idx = None
        best_prefix_match = 0
        for i, pred in enumerate(chain):
            pred_prefix = prefix_bytes(pred)
            known_prefix = prefix_bytes(known_val)
            match = sum(a == b for a, b in zip(pred_prefix, known_prefix))
            if match > best_prefix_match:
                best_prefix_match = match
                best_match = pred
                best_match_idx = i
        if best_match is not None:
            print(f"Best prefix match: Prediction {best_match_idx+1} (chain[{best_match_idx}]): {format_prediction(best_match)}")
            print(f"Prefix match: {best_prefix_match}/{PREFIX_BYTES*2} hex chars")
            print(f"Predicted prefix: {prefix_bytes(best_match)}")
            print(f"Actual prefix:    {prefix_bytes(known_val)}")
            xor_diff = best_match ^ known_val
            total_bits = max(best_match.bit_length(), known_val.bit_length())
            matching_bits = total_bits - bin(xor_diff).count('1')
            similarity_percent = (matching_bits / total_bits) * 100 if total_bits > 0 else 0
            print(f"Bit similarity: {similarity_percent:.2f}%")
    print("\nAll predictions and prefixes (indexes 1-160):")
    for i, pred in enumerate(chain):
        idx = i + 1
        print(f"Prediction {idx}: {format_prediction(pred)} | Prefix: {prefix_bytes(pred)}", end="")
        if idx in KNOWN_FUTURE:
            print(f" <== KNOWN KEY (Actual: {KNOWN_FUTURE[idx]})")
        else:
            print()
    plt.figure(figsize=(10, 6))
    plt.bar([idx for idx in KNOWN_INDEXES if idx in KNOWN_FUTURE], prefix_matches, color='blue')
    plt.xlabel('Index')
    plt.ylabel('Prefix Match (Hex Chars)')
    plt.title('Prefix Matches for Known Future Values')
    plt.ylim(0, PREFIX_BYTES*2)
    plt.grid(True)
    plt.savefig('prefix_matches.png')
    plt.close()

def visualize_patterns(analysis):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 20))
    values = analysis['values']
    ax1.plot(values, label='Values', color='blue')
    ax1.plot(analysis['xor_diffs'], label='XOR Differences', color='red')
    ax1.set_title('Values and XOR Differences')
    ax1.legend()
    ax2.plot(analysis['bit_patterns'], label='Bit Patterns', color='green')
    ax2.set_title('Bit Patterns')
    ax2.legend()
    ax3.plot([v1 - v0 for v0, v1 in zip(values[:-1], values[1:])], label='Regular Differences', color='purple')
    ax3.set_title('Regular Differences')
    ax3.legend()
    bit_lengths = [x.bit_length() for x in values]
    ax4.plot(bit_lengths, label='Bit Lengths', color='orange')
    ax4.set_title('Bit Length Progression')
    ax4.legend()
    plt.tight_layout()
    plt.savefig('key_pattern_analysis.png')
    plt.close()

def plot_predictions(chain, known_future):
    plt.figure(figsize=(12, 8))
    known_indices = sorted(known_future.keys())
    known_values = [int(known_future[i], 16) for i in known_indices]
    pred_indices = [i for i in known_indices if 0 <= i - 1 < len(chain)]
    pred_values = [chain[i - 1] for i in pred_indices]
    plt.plot(range(1, len(chain)+1), chain, label='Predicted Chain', marker='o', linestyle='--', alpha=0.5)
    plt.plot(known_indices, known_values, label='Actual Known', marker='x', linestyle='None', color='red')
    plt.yscale('log')
    plt.xlabel('Index')
    plt.ylabel('Value (log scale)')
    plt.title('Predicted Chain (1-160) vs Actual Known Values')
    plt.legend()
    plt.grid(True)
    plt.savefig('prediction_comparison.png')
    plt.close()

def main():
    analysis = analyze_patterns()
    print("\nPattern Analysis Results:")
    print("------------------------")
    print(f"Number of values analyzed: {len(analysis['values'])}")
    chain = predict_entire_chain(analysis, total_indexes=160)
    print("\nPredicted chain (indexes 1-160):")
    for i, pred in enumerate(chain):
        idx = i + 1
        print(f"Prediction {idx}: {format_prediction(pred)} | Prefix: {prefix_bytes(pred)}", end="")
        if idx in KNOWN_FUTURE:
            print(f" <== KNOWN KEY (Actual: {KNOWN_FUTURE[idx]})")
        else:
            print()
    analyze_prediction_accuracy_full(chain)
    visualize_patterns(analysis)
    plot_predictions(chain, KNOWN_FUTURE)
    print("\nVisualizations saved as 'key_pattern_analysis.png', 'prediction_comparison.png', and 'prefix_matches.png'")

if __name__ == "__main__":
    main()