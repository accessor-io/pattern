# Bitcoin Puzzle - Known Facts Summary

## Overview
The Bitcoin puzzle is a sequence of Bitcoin addresses with increasing private key difficulty. The puzzle creator has revealed some positions as hints.

## Puzzle Creation Transaction

The Bitcoin puzzle was created on **January 15, 2015** in a single transaction:
- **Transaction ID**: [08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15](https://www.blockchain.com/btc/tx/08389f34c98c606322740c0be6a7125d9860bb8d5cb182c02f98461e5fa6cd15)
- **Date**: January 15, 2015 10:07 AM
- **Block Hash**: 0000000000000000188de542fd76b1676c4be6c380b39ddea119358c290cebd7
- **Total Value Sent**: 32.896 BTC
- **Fee**: 0.004 BTC

### Funding Pattern
Each puzzle address received BTC equal to its position number divided by 1000:
- Position 1: 0.001 BTC
- Position 2: 0.002 BTC
- Position 3: 0.003 BTC
- ...
- Position n: n/1000 BTC

At least 256 addresses were funded in this initial transaction.

## Verified/Known Positions

### Fully Known Range
- **Positions 1-68**: All have been solved (mostly through brute force for lower positions)
- **Position 69**: Unknown (gap in sequence)

### Hint Positions (ending in 0 or 5)
From position 70 onwards, only positions ending in 0 or 5 have been revealed by the puzzle creator:
- 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, etc.

### Unknown Positions
All positions not ending in 0 or 5 after position 68 are unknown:
- 71-74, 76-79, 81-84, 86-89, 91-94, 96-99, 101-104, 106-109, etc.

## Pattern Analysis (Positions 1-68)

The sequence uses a pattern where each private key is derived from the previous one:
```
key[n] = key[n-1] + constant[n]
```

### Early Position Constants (Working Patterns)
- Position 1→2: +2
- Position 2→3: +4
- Position 3→4: +1
- Position 4→5: +13
- Position 5→6: +28
- Position 6→7: +27
- Position 7→8: +148
- Position 8→9: +243
- Position 9→10: +47
- Position 10→11: +641
- Position 11→12: +1,528
- Position 12→13: +2,533
- Position 13→14: +5,328
- Position 14→15: +16,323
- Position 15→16: +24,643
- Position 16→17: +44,313
- Position 17→18: +102,846

### Growth Pattern
The constants grow exponentially but with high variability:
- Early positions (1-10): Small constants, irregular growth
- Middle positions (10-30): Exponential growth with factor ~1.5-3x
- Later positions (30+): More consistent exponential growth

### Positions 70+ (5/0 positions only)
Growth between consecutive 5/0 positions averages around 30-40x:
- 70→75: difference of ~2.16 × 10^22
- 75→80: difference of ~1.08 × 10^24 (50x growth)
- 80→85: difference of ~2.00 × 10^25 (18x growth)
- Pattern continues with similar magnitudes

## Key Insights

1. **Cannot Predict Unknown Positions**: The positions between the 5/0 hints (like 71-74, 76-79) cannot be predicted without solving the actual puzzle.

2. **Pattern Discovery Works for Early Positions**: The transformation pattern `k[n] = k[n-1] + constant[n]` successfully describes positions 1-68.

3. **Constants Must Be Known**: Without knowing the specific constant for each position, we cannot generate the next key.

4. **No Simple Formula**: There's no simple mathematical formula that generates all constants - they appear to be chosen specifically by the puzzle creator.

## Technical Implementation

The successful pattern discovery script (`key_sequence_generator.py`) uses:
- Thousands of mathematical transformation formulas
- Bitshift operations for complex patterns
- Verification against known Bitcoin addresses
- Custom RIPEMD160 implementation for address generation

The script successfully identifies patterns for positions where we have consecutive known keys but cannot predict unsolved positions. 