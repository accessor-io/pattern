#!/usr/bin/env python3
"""
01_sequence_analyzer.py - Core Sequence Analysis Framework

A comprehensive framework for analyzing numerical sequences with a focus on 
cryptographic properties and pattern detection. This module provides the 
foundation for all sequence analysis operations.

Features:
- Statistical analysis of sequence properties
- Bit-level pattern detection and analysis
- Security property assessment (rate-α, avalanche effect)
- Difference analysis between consecutive terms
- Block pattern analysis with configurable block size

Applications:
- Cryptographic sequence quality assessment
- Randomness evaluation
- Pattern identification for prediction
- Security validation for key generation algorithms
"""

import statistics
import math
from typing import List, Dict, Any, Tuple

class SequenceAnalyzer:
    """Core sequence analysis engine with comprehensive metrics"""
    
    def __init__(self, sequence: List[int]):
        """Initialize with a sequence of integer values"""
        self.sequence = sequence
        self.length = len(sequence)
        
    def analyze_consecutive_differences(self) -> Dict[str, float]:
        """
        Analyze differences between consecutive values in the sequence
        
        Returns:
            Dictionary containing statistical measures of differences
        """
        if self.length < 2:
            return {"mean": 0, "median": 0, "min": 0, "max": 0, "std_dev": 0}
        
        diffs = [self.sequence[i+1] - self.sequence[i] for i in range(self.length-1)]
        
        return {
            "mean": statistics.mean(diffs),
            "median": statistics.median(diffs),
            "min": min(diffs),
            "max": max(diffs),
            "std_dev": statistics.stdev(diffs) if len(diffs) > 1 else 0
        }
    
    def analyze_bit_patterns(self) -> List[Dict[str, Any]]:
        """
        Analyze bit-level patterns and transitions between consecutive values
        
        Returns:
            List of dictionaries containing bit transition details
        """
        results = []
        
        for i in range(self.length - 1):
            prev_value = self.sequence[i]
            curr_value = self.sequence[i+1]
            
            # Convert to binary and count transitions
            prev_bits = bin(prev_value)[2:]
            curr_bits = bin(curr_value)[2:]
            
            # Calculate Hamming distance
            max_len = max(len(prev_bits), len(curr_bits))
            prev_bits = prev_bits.zfill(max_len)
            curr_bits = curr_bits.zfill(max_len)
            
            bit_changes = sum(p != c for p, c in zip(prev_bits, curr_bits))
            
            # Calculate Hamming weight change
            prev_weight = prev_bits.count('1')
            curr_weight = curr_bits.count('1')
            
            results.append({
                "position": i,
                "prev_value": prev_bits,
                "curr_value": curr_bits,
                "bit_changes": bit_changes,
                "hamming_weight_change": curr_weight - prev_weight,
                "bit_length": max_len
            })
            
        return results
    
    def analyze_block_patterns(self, block_size: int = 4) -> List[Dict[str, Any]]:
        """
        Analyze patterns in fixed-size blocks of bits
        
        Args:
            block_size: Number of bits per block
            
        Returns:
            List of dictionaries containing block transition details
        """
        results = []
        
        for i in range(self.length - 1):
            prev_value = self.sequence[i]
            curr_value = self.sequence[i+1]
            
            # Convert to binary
            prev_bits = bin(prev_value)[2:]
            curr_bits = bin(curr_value)[2:]
            
            # Ensure even length for block division
            max_len = max(len(prev_bits), len(curr_bits))
            padded_len = ((max_len // block_size) + 1) * block_size
            
            prev_bits = prev_bits.zfill(padded_len)
            curr_bits = curr_bits.zfill(padded_len)
            
            # Analyze blocks
            block_changes = []
            for j in range(0, padded_len, block_size):
                prev_block = prev_bits[j:j+block_size]
                curr_block = curr_bits[j:j+block_size]
                
                changes = sum(p != c for p, c in zip(prev_block, curr_block))
                
                block_changes.append({
                    "block_position": j // block_size,
                    "prev_block": prev_block,
                    "curr_block": curr_block,
                    "changes": changes
                })
                
            results.append({
                "position": i,
                "block_changes": block_changes
            })
            
        return results
    
    def analyze_security_properties(self) -> Dict[str, float]:
        """
        Analyze cryptographic security properties of the sequence
        
        Returns:
            Dictionary containing security metrics
        """
        # Calculate Rate-α (measure of bit changes)
        bit_patterns = self.analyze_bit_patterns()
        
        if not bit_patterns:
            return {
                "rate_alpha": 1.0,
                "avg_bit_changes": 0,
                "avalanche_quality": 0,
                "permutation_estimate": 0
            }
        
        total_bits = sum(pattern["bit_length"] for pattern in bit_patterns)
        total_changes = sum(pattern["bit_changes"] for pattern in bit_patterns)
        
        # Calculate average bit changes
        avg_changes = total_changes / len(bit_patterns)
        
        # Rate-α: Ratio of bits that change between consecutive values
        rate_alpha = total_changes / total_bits if total_bits > 0 else 1.0
        
        # Avalanche quality (normalized to ideal of 0.5)
        ideal_change_rate = 0.5  # Ideal: half the bits change
        avalanche_quality = 1.0 - abs(rate_alpha - ideal_change_rate) * 2
        
        # Estimate minimum permutations (rough estimate)
        permutation_estimate = int(2 ** (rate_alpha * math.log2(total_bits)))
        
        return {
            "rate_alpha": rate_alpha,
            "avg_bit_changes": avg_changes,
            "avalanche_quality": avalanche_quality,
            "permutation_estimate": permutation_estimate
        } 