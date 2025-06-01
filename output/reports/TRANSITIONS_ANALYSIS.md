# Bitcoin Key Sequence Transitions Analysis

This document summarizes the analysis of transitions between consecutive private keys in the known sequence.

## Key Findings

1. **Basic Transitions Analysis**:
   - Key #1 to Key #2: The difference is exactly 2 (from 1 to 3)
   - Key #2 to Key #3: The difference is 4 (from 3 to 7)
   - Position 2 has a special pattern: Key + sum of prime factors (2) at position 2
   - Position 10 has special handling: the key is not doubled as might be expected

2. **Character Influence Patterns**:
   - Some differences appear to be multiples of their positions (particularly multiple of 2)
   - Character ASCII values seem to influence the differences in some cases
   - No direct correlation was found between Base58 indices and differences

3. **Key Derivation Method**:
   - First key's address (1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH) is not derived from the private key 0x1 using standard RIPEMD-160 hashing
   - This suggests a custom derivation method for the entire sequence

4. **Formula Patterns**:
   - Several different formulas were tested across the first 10 transitions 
   - 8 exact matches were found among tested formulas
   - Notable formulas include:
     - Key * 3 (position 2)
     - Key + sum of prime factors (position 2) 

5. **No Control Characters**:
   - No control characters were found in the analyzed portion of the string

## Next Steps

1. **Investigate custom hash160 implementation**:
   - The first key does not derive to the expected address using standard methods
   - Need to determine what custom hashing scheme is being used

2. **Expand analysis to more keys**:
   - Analyze a larger set of transitions to identify consistent patterns
   - Focus on positions that follow mathematical sequences (primes, powers of 2, etc.)

3. **Build a transition model**:
   - Based on the identified patterns, create a model that can predict the next key
   - Test against additional known keys to validate the model

4. **Test special operation combinations**:
   - The pattern likely involves multiple operations (multiplication, addition, etc.)
   - Need to test various combinations of operations based on position and character values

## Raw Observations

The strongest patterns observed in the first 10 transitions:

| Position | Character | Previous Key | Current Key | Difference | Notable Pattern |
|----------|-----------|--------------|-------------|------------|-----------------|
| 2        | C         | 1            | 3           | 2          | Key * 3; Key + prime factors(2) |
| 3        | 9         | 3            | 7           | 4          | Key + 4 |
| 4        | E         | 7            | 8           | 1          | Key + 1 |
| 5        | E         | 8            | 21          | 13         | None obvious |
| 6        | P         | 21           | 49          | 28         | None obvious |
| 7        | M         | 49           | 76          | 27         | None obvious |
| 8        | M         | 76           | 224         | 148        | None obvious |
| 9        | C         | 224          | 467         | 243        | None obvious |
| 10       | L         | 467          | 514         | 47         | Not doubled at this position |
| 11       | P         | 514          | 1155        | 641        | None obvious | 