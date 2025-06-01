#!/usr/bin/env python3
"""
🔍 ERROR CALCULATION VERIFICATION
Show exactly how the percentage errors are calculated for our ultra-precise formulas
"""

import math

# Known solutions
KNOWN_KEYS = {
    65: 0x1a838b13505b26867,
    70: 0x349b84b6431a6c4ef1,
    80: 0xea1a5c66dcc11b5ad180,
}

def verify_error_calculations():
    """Verify the exact error calculations for our best formulas"""
    print("🔍 VERIFYING ERROR CALCULATIONS")
    print("=" * 80)
    print("Showing exactly how percentage errors are calculated")
    print()
    
    # Position 65: k = 2^(n-1) * (1 + n/100)
    pos = 65
    actual_key = KNOWN_KEYS[pos]
    predicted_key = int((1 << (pos-1)) * (1 + pos/100))
    
    print(f"📊 POSITION {pos}: k = 2^(n-1) * (1 + n/100)")
    print(f"  Actual key:    0x{actual_key:x} = {actual_key:,}")
    print(f"  Predicted key: 0x{predicted_key:x} = {predicted_key:,}")
    print(f"  Difference:    {abs(actual_key - predicted_key):,}")
    
    error_65 = abs(actual_key - predicted_key) / actual_key * 100
    print(f"  Error = |{actual_key:,} - {predicted_key:,}| / {actual_key:,} * 100")
    print(f"  Error = {abs(actual_key - predicted_key):,} / {actual_key:,} * 100")
    print(f"  Error = {error_65:.6f}%")
    print()
    
    # Position 70: k = 2^(n-1) * φ (golden ratio)
    pos = 70
    actual_key = KNOWN_KEYS[pos]
    phi = (1 + math.sqrt(5))/2
    predicted_key = int((1 << (pos-1)) * phi)
    
    print(f"📊 POSITION {pos}: k = 2^(n-1) * φ (golden ratio)")
    print(f"  φ (phi) = (1 + √5)/2 = {phi:.10f}")
    print(f"  Actual key:    0x{actual_key:x} = {actual_key:,}")
    print(f"  Predicted key: 0x{predicted_key:x} = {predicted_key:,}")
    print(f"  Difference:    {abs(actual_key - predicted_key):,}")
    
    error_70 = abs(actual_key - predicted_key) / actual_key * 100
    print(f"  Error = |{actual_key:,} - {predicted_key:,}| / {actual_key:,} * 100")
    print(f"  Error = {abs(actual_key - predicted_key):,} / {actual_key:,} * 100")
    print(f"  Error = {error_70:.6f}%")
    print()
    
    # Position 80: k = 2^(n-1) * (1 + n/100)
    pos = 80
    actual_key = KNOWN_KEYS[pos]
    predicted_key = int((1 << (pos-1)) * (1 + pos/100))
    
    print(f"📊 POSITION {pos}: k = 2^(n-1) * (1 + n/100)")
    print(f"  Actual key:    0x{actual_key:x} = {actual_key:,}")
    print(f"  Predicted key: 0x{predicted_key:x} = {predicted_key:,}")
    print(f"  Difference:    {abs(actual_key - predicted_key):,}")
    
    error_80 = abs(actual_key - predicted_key) / actual_key * 100
    print(f"  Error = |{actual_key:,} - {predicted_key:,}| / {actual_key:,} * 100")
    print(f"  Error = {abs(actual_key - predicted_key):,} / {actual_key:,} * 100")
    print(f"  Error = {error_80:.6f}%")
    print()
    
    print("=" * 80)
    print("✅ VERIFIED ERROR CALCULATIONS:")
    print(f"  Position 65: {error_65:.1f}% error")
    print(f"  Position 70: {error_70:.1f}% error") 
    print(f"  Position 80: {error_80:.1f}% error")
    print()
    print("📝 FORMULA USED:")
    print("  Percentage Error = |Actual - Predicted| / Actual × 100%")
    print("  This is the standard relative error calculation")
    print("  showing how close our predictions are to reality!")

if __name__ == "__main__":
    verify_error_calculations() 