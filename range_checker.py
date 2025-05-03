import sys

# These lines run ONLY ONCE when the script/module is loaded
LOWER_BOUND = 1 << 72      # Calculated once
UPPER_BOUND = (1 << 73) - 1 # Calculated once

def is_in_specific_hex_range(number_to_check: int) -> bool:
    """
    Checks if the given integer falls within the specific range
    corresponding to 19-digit hexadecimal numbers starting with '1'.

    This range is [2^72, 2^73 - 1].

    Args:
        number_to_check: The integer to check.

    Returns:
        True if the number is within the range, False otherwise.
    """
    if not isinstance(number_to_check, int):
        raise TypeError("Input must be an integer.")

    # This check uses the pre-calculated constants and is very fast
    return LOWER_BOUND <= number_to_check <= UPPER_BOUND

# Example Usage (optional, can be run if the script is executed directly)
if __name__ == "__main__":
    # Example numbers
    num_in_range = (1 << 72) + 500  # Slightly above lower bound
    num_at_lower_bound = 1 << 72
    num_at_upper_bound = (1 << 73) - 1
    num_below_range = (1 << 72) - 1 # Just below lower bound
    num_above_range = 1 << 73     # Just above upper bound
    small_num = 100

    print(f"Lower Bound (decimal): {LOWER_BOUND}")
    print(f"Upper Bound (decimal): {UPPER_BOUND}")
    print("-" * 20)

    print(f"Is {num_in_range} in range? {is_in_specific_hex_range(num_in_range)}")
    print(f"Is {num_at_lower_bound} in range? {is_in_specific_hex_range(num_at_lower_bound)}")
    print(f"Is {num_at_upper_bound} in range? {is_in_specific_hex_range(num_at_upper_bound)}")
    print(f"Is {num_below_range} in range? {is_in_specific_hex_range(num_below_range)}")
    print(f"Is {num_above_range} in range? {is_in_specific_hex_range(num_above_range)}")
    print(f"Is {small_num} in range? {is_in_specific_hex_range(small_num)}")

    # Example with hexadecimal input interpretation
    hex_str_lower = "10000000000000000"
    hex_str_upper = "1fffffffffffffffff"
    hex_str_mid   = "1abcdef0123456789"
    hex_str_below = "ffffffffffffffff" # 18 digits
    hex_str_above = "20000000000000000" # Starts with 2

    print("-" * 20)
    print(f"Checking hex values:")
    print(f"Is 0x{hex_str_lower} in range? {is_in_specific_hex_range(int(hex_str_lower, 16))}")
    print(f"Is 0x{hex_str_upper} in range? {is_in_specific_hex_range(int(hex_str_upper, 16))}")
    print(f"Is 0x{hex_str_mid} in range? {is_in_specific_hex_range(int(hex_str_mid, 16))}")
    print(f"Is 0x{hex_str_below} in range? {is_in_specific_hex_range(int(hex_str_below, 16))}")
    print(f"Is 0x{hex_str_above} in range? {is_in_specific_hex_range(int(hex_str_above, 16))}")

    # Test type checking
    try:
        is_in_specific_hex_range("not an integer")
    except TypeError as e:
        print(f"Caught expected error: {e}") 