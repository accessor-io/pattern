import json
import os
import sys
from bitcoinlib.keys import Key

def pad_hex(hex_str):
    # Remove '0x' prefix if present and pad to 64 characters
    hex_str = hex_str.replace('0x', '')
    return hex_str.zfill(64)

def hex_to_bitcoin_address(hex_str):
    try:
        # Convert padded hex to private key and get compressed address
        private_key = Key(hex_str)
        return private_key.address()
    except Exception as e:
        return f"Error converting address: {str(e)}"

def process_json_file(filepath):
    print(f"\nProcessing file: {filepath}")
    print("=" * 50)
    
    try:
        # Read JSON file
        with open(filepath, 'r') as file:
            hex_values = json.load(file)
        
        # Process each hex value
        results = []
        for hex_value in hex_values:
            padded_hex = pad_hex(hex_value)
            bitcoin_address = hex_to_bitcoin_address(padded_hex)
            results.append({
                "original": hex_value,
                "padded": padded_hex,
                "address": bitcoin_address
            })
            print(f"Original: {hex_value}")
            print(f"Padded  : {padded_hex}")
            print(f"Address : {bitcoin_address}")
            print("-" * 50)
        
        return results
    
    except Exception as e:
        print(f"Error processing file {filepath}: {str(e)}")
        return []

def main():
    input_directory = "./"  # Directory containing input files
    log_file = "./output/output_log.txt"  # Log file for all terminal output

    # Ensure output directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Redirect standard output to a file
    with open(log_file, 'w') as log:
        sys.stdout = log  # Redirect all print statements to the log file

        print("Starting address processing...")
        print("=" * 50)

        all_results = []
        
        # Process only files named batch_<number>.json
        for filename in os.listdir(input_directory):
            if filename.startswith("batch_") and filename.endswith(".json"):
                try:
                    # Extract the number from the filename
                    number = filename.split("_")[1].split(".")[0]
                    if number.isdigit():  # Ensure it's a number
                        batch_number = int(number)
                        if 0 <= batch_number <= 5:  # Check range
                            filepath = os.path.join(input_directory, filename)
                            results = process_json_file(filepath)
                            all_results.extend(results)
                except ValueError:
                    # Skip files that don't match the expected format
                    continue
        
        # Save results as JSON to a separate file
        results_file = "./output/results_all.json"
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print("\nAll processing complete.")
        print(f"Results saved to: {results_file}")
        print(f"Log saved to: {log_file}")

if __name__ == "__main__":
    # Install bitcoinlib if not already installed
    try:
        import bitcoinlib
    except ImportError:
        print("Installing required library: bitcoinlib")
        os.system('pip install bitcoinlib')
        
    main()
