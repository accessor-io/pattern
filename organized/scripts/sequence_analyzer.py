import math

def analyze_full_sequence():
    """
    Analyze a sequence of 32-bit hex numbers from a file, searching for patterns
    such as constant difference, geometric progression, polynomial growth, exponential,
    and logarithmic behaviors. Also predicts potential next values based on
    the identified patterns.
    """

    def read_numbers_from_file(file_path):
        """
        Reads hexadecimal numbers from a file where each line
        contains a single hex value.

        :param str file_path: The path to the file containing hex values.
        :return: A list of integers parsed from the file.
        :rtype: list
        """
        with open(file_path, 'r') as f:
            return [int(line.strip(), 16) for line in f]

    def calculate_differences(sequence):
        """
        Calculates first-order differences relative to the first element in the sequence.

        :param list sequence: The list of integer values.
        :return: A list of differences from the first element.
        :rtype: list
        """
        if not sequence:
            return []
        return [sequence[i] - sequence[0] for i in range(1, len(sequence))]

    def print_differences(order, diffs):
        """
        Prints the differences for the given order, showcasing a subset from the start and end.

        :param int order: The current order of differences being analyzed.
        :param list diffs: The list of differences.
        """
        print(f"\nOrder {order} differences (first 5 and last 5):")
        for i in range(min(5, len(diffs))):
            print(f"Start {i}: {hex(diffs[i])} ({diffs[i]})")
        print("...")
        for i in range(max(0, len(diffs) - 5), len(diffs)):
            print(f"End {i}: {hex(diffs[i])} ({diffs[i]})")

    def predict_next_difference(diffs):
        """
        Predicts the next difference value by returning the last known difference. 
        This is a simplistic approach and can be improved.

        :param list diffs: The list of differences.
        :return: Last difference if available, otherwise None.
        """
        if len(diffs) < 2:
            return None
        return diffs[-1]

    def predict_next_value(sequence, diffs):
        """
        Predicts the next sequence value by adding the predicted difference 
        to the last known sequence value.

        :param list sequence: The original sequence of values.
        :param list diffs: The list of differences.
        :return: The predicted next value if it can be determined, otherwise None.
        """
        if not diffs:
            return None
        last_value = sequence[-1]
        predicted_diff = predict_next_difference(diffs)
        if predicted_diff is not None:
            return last_value + predicted_diff
        return None

    def analyze_patterns(diffs, order):
        """
        Analyzes various numeric patterns in the given differences (constant, geometric, 
        polynomial, exponential, and logarithmic).

        :param list diffs: The list of differences.
        :param int order: The order of differences (e.g., 0 for the original sequence,
                          1 for first-order differences, etc.).
        :return: True if a recognized pattern is found or signaled, otherwise False.
        :rtype: bool
        """
        if len(diffs) < 2:
            return False

        # Calculate average ratio for basic pattern diagnostics
        ratios = [
            diffs[i] / diffs[i - 1] if diffs[i - 1] != 0 else float('inf')
            for i in range(1, len(diffs))
        ]
        finite_ratios = [r for r in ratios if r != float('inf')]
        avg_ratio = sum(finite_ratios) / len(finite_ratios) if finite_ratios else 0
        print(f"\nAverage ratio between consecutive differences: {avg_ratio:.4f}")

        # Check for constant difference pattern
        all_same = all(abs(d - diffs[0]) < abs(diffs[0] * 0.1) for d in diffs if diffs[0] != 0)
        if all_same and diffs:
            print(f"Found constant difference pattern at order {order}!")
            print(f"Approximate constant value: {sum(diffs) / len(diffs)}")
            return True

        # Check for possible geometric progression at order == 1
        if order == 1 and len(diffs) >= 3:
            for i in range(len(diffs) - 2):
                if diffs[i] != 0 and diffs[i + 1] != 0:
                    ratio1 = diffs[i + 1] / diffs[i]
                    ratio2 = diffs[i + 2] / diffs[i + 1]
                    if abs(ratio1 - ratio2) < 0.1:
                        print(f"\nPossible geometric progression found at position {i}")
                        print(f"Ratio: {ratio1:.4f}")

        # Check for quadratic (second-order) pattern
        if order == 2 and len(diffs) >= 2:
            second_order_diffs = [diffs[i] - diffs[i - 1] for i in range(1, len(diffs))]
            if second_order_diffs:
                base_diff = second_order_diffs[0]
                if all(
                    abs(d - base_diff) < abs(base_diff * 0.1)
                    for d in second_order_diffs if base_diff != 0
                ):
                    print(f"Found quadratic pattern at order {order}!")
                    print(f"Approximate quadratic coefficient: {sum(second_order_diffs) / len(second_order_diffs)}")

        # Exponential growth check for orders > 2
        if order > 2:
            exponential_growth = all(diffs[i] > diffs[i - 1] for i in range(1, len(diffs)))
            if exponential_growth:
                print(f"Exponential growth pattern detected at order {order}!")
                return True

        # Logarithmic pattern check for orders > 1
        if order > 1 and len(diffs) >= 2:
            log_diffs = [math.log(abs(d)) if d != 0 else float('-inf') for d in diffs]
            valid_logs = all(ld != float('-inf') for ld in log_diffs)
            if valid_logs and all(abs(log_diffs[i] - log_diffs[i - 1]) < 0.1 for i in range(1, len(log_diffs))):
                print(f"Logarithmic pattern detected at order {order}!")
                return True

        return False

    def check_irregularity(diffs, order):
        """
        Checks if the differences become too irregular by calculating a measure
        of deviation from a simple 'twice the previous difference' pattern.

        :param list diffs: The list of differences.
        :param int order: The order of differences.
        :return: True if the sequence is deemed too irregular, otherwise False.
        :rtype: bool
        """
        if len(diffs) < 3:
            return False

        irregularity = sum(
            abs(diffs[i] - 2 * diffs[i - 1]) for i in range(1, len(diffs))
        ) / len(diffs)
        if irregularity > 1000000:
            print(f"\nDifferences become too irregular at order {order}")
            return True

        return False

    # Read the original sequence from file
    numbers = read_numbers_from_file('organized/data/32bHex.txt')
    if not numbers:
        print("No numbers to analyze. Check the file path or contents.")
        return

    print(f"Analyzing all {len(numbers)} numbers in sequence...")
    current = numbers

    # Iterate through different orders of difference (up to a controlled limit)
    for order in range(-1, 161):
        diffs = calculate_differences(current)
        print_differences(order, diffs)

        # Stop if we find a recognized pattern or if irregularity is high
        if analyze_patterns(diffs, order) or check_irregularity(diffs, order):
            break

        predicted_diff = predict_next_difference(diffs)
        if predicted_diff is not None:
            print(f"Predicted next difference for order {order}: {predicted_diff}")

        predicted_value = predict_next_value(current, diffs)
        if predicted_value is not None:
            print(f"Predicted next value for order {order}: {predicted_value}")

        # Move to the next order's data set
        current = diffs

    # Final prediction based on the original sequence
    final_predicted_value = predict_next_value(numbers, calculate_differences(numbers))
    if final_predicted_value is not None:
        print(f"\nFinal predicted next value: {final_predicted_value}")

if __name__ == '__main__':
    analyze_full_sequence()