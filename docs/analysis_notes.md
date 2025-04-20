# RowHammer Search Analysis Notes

This document tracks progress, insights, and best candidates found during the search for Term 68's private key.

## Target Information
- **Target Bitcoin Address**: `1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ`
- **Previous Term (67)**: `0x730fc235c1942c1ae`

## Best Candidates

| Candidate (Hex) | Bitcoin Address | Similarity | Notes |
|-----------------|----------------|------------|-------|
| 0x730fc235c1942c0ae | 1ADH9iFQpnTeHkY967i4TbYLGFa2fdSqbZ | 0.079559 | Bit flip at position 8 |
| 0x730fc235c1943c1ae | 1CMFGLm3qJRvEKdF4v9XDeMnQyDv7vw5iR | 0.056912 | Bit flip at position 16 |
| 0x730fc235c1942c1be | 1KWMjgoDC9bSbyi4rxUCnEpXLWg4S3ybB5 | 0.058088 | Bit flip at position 4 |
| 0x730fc235c1942c1af | 1Exiwi6txowk7CpyPiD5MgRdxCmh1pBT4n | 0.029412 | Bit flip at position 0 |
| 0x734fc235c1940c1af | 1en6BBwp3f68JxNVNqs4Ym25ktmPbiDkM | 0.058824 | Modified base from debug |

## Search Insights

### Bit Position Analysis

Based on our testing, bit flips at the following positions seem most promising:
- Position 8: Highest similarity (0.079559)
- Position 16: Good similarity (0.056912)
- Position 4: Good similarity (0.058088)

The pattern suggests that modifying bits in positions 4-16 has the most impact on address similarity, which aligns with how Bitcoin address generation works (bits in certain positions have greater influence on the final hash).

### RowHammer Attack Patterns

Different attack patterns from the Hammulator paper show varying effectiveness:

1. **Systematic RowHammer**: Good for wide exploration
2. **Double-sided hammering**: More effective for targeted bit flips
3. **Half-double attack**: Provides unique bit-flip patterns not found by other methods

### Search Parameter Optimization

The optimal parameters found so far:
- ADJACENT_INFLUENCE: 3-4 (bits adjacent to aggressor)
- FLIP_PROBABILITY: 0.05-0.1 (higher values lead to too many flips)
- ACTIVATION_THRESHOLD: 75-100 (lower thresholds create excessive candidates)

## Future Search Directions

1. **Focused Target Range**: Focus on bit flip combinations in the identified effective positions (4-16)
2. **Mutation Strategy**: Apply sequential mutations to the best candidates
3. **Similarity Threshold**: Maintain a higher threshold (>0.05) to focus on promising paths
4. **Regional Hammering**: Hammer specific regions of bits that show better results

## References

- Original Hammulator paper: https://dramsec.ethz.ch/papers/hammulator.pdf
- Bitcoin address generation algorithm: https://en.bitcoin.it/wiki/Technical_background_of_version_1_Bitcoin_addresses 