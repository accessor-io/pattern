import os
import sys
import time
import signal
from bitcoin_math.schnorr_analysis import analyze_schnorr_properties
from elliptic_curves.secp256k1_analysis import analyze_curve_properties
from number_theory.modular_forms import analyze_modular_properties
from hash_chains.hash_sequence import analyze_hash_chains

def run_with_timeout(func, args, timeout=10):
    """Run a function with a timeout"""
    result = {'completed': False, 'data': None, 'error': None}
    
    def handler(signum, frame):
        raise TimeoutError(f"Analysis took longer than {timeout} seconds")
    
    # Set the signal handler and a timeout
    original_handler = signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)
    
    try:
        result['data'] = func(*args)
        result['completed'] = True
    except TimeoutError as e:
        result['error'] = str(e)
    except Exception as e:
        result['error'] = str(e)
    finally:
        signal.alarm(0)  # Disable the alarm
        signal.signal(signal.SIGALRM, original_handler)  # Restore original handler
    
    return result

def format_result_value(value):
    """Format a result value for output"""
    if isinstance(value, (list, tuple)):
        return "\n".join(f"  - {item}" for item in value)
    elif isinstance(value, dict):
        return "\n".join(f"  {k}: {v}" for k, v in value.items())
    else:
        return f"  {value}"

def write_analysis_results(f, analysis_type, result):
    """Write a single analysis result to the file"""
    f.write(f"\n=== {analysis_type.upper()} ANALYSIS ===\n")
    f.write("=" * 50 + "\n")
    
    if isinstance(result, dict):
        if 'error' in result:
            f.write(f"ERROR: {result['error']}\n")
        else:
            for key, value in result.items():
                f.write(f"\n{key}:\n")
                f.write("-" * 40 + "\n")
                f.write(format_result_value(value) + "\n")
    else:
        f.write(format_result_value(result) + "\n")
    
    f.write("\n" + "=" * 50 + "\n")

def comprehensive_analysis():
    print("Starting comprehensive analysis...")
    start_time = time.time()
    
    # Get absolute path to data file
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_file = os.path.join(root_dir, 'data', '32bHex.txt')
    print(f"Looking for data file at: {data_file}")
    
    try:
        if not os.path.exists(data_file):
            print(f"Error: Data file not found at {data_file}")
            sys.exit(1)
            
        with open(data_file, 'r') as f:
            hex_strings = [line.strip() for line in f if line.strip()]
        print(f"Read {len(hex_strings)} hex strings from file")
        
        # Run multiple analyses
        print("\nRunning analyses...")
        results = {}
        completed = 0
        
        # Reordered analyses to run faster ones first
        analyses = [
            ('schnorr', analyze_schnorr_properties, 5),  # 5 second timeout
            ('hash_chain', analyze_hash_chains, 5),      # 5 second timeout
            ('secp256k1', analyze_curve_properties, 10), # 10 second timeout
            ('modular', analyze_modular_properties, 15)  # 15 second timeout
        ]
        
        for i, (name, func, timeout) in enumerate(analyses, 1):
            print(f"\n{i}. Running {name} analysis...")
            analysis_start = time.time()
            
            try:
                result = run_with_timeout(func, [hex_strings], timeout)
                
                if result['completed']:
                    duration = time.time() - analysis_start
                    print(f"✓ {name} analysis completed in {duration:.2f} seconds")
                    results[name] = result['data']
                    completed += 1
                else:
                    print(f"✗ {name} analysis failed: {result['error']}")
                    results[name] = {'error': result['error']}
                    
                    if name == 'modular' and 'TimeoutError' in str(result['error']):
                        print("Skipping modular analysis due to timeout...")
                        continue
                        
            except Exception as e:
                print(f"✗ {name} analysis failed with error: {str(e)}")
                results[name] = {'error': str(e)}
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join(root_dir, 'output', 'comprehensive')
        os.makedirs(output_dir, exist_ok=True)
        print(f"\nCreated output directory: {output_dir}")
        
        # Write results
        output_file = os.path.join(output_dir, 'mathematical_analysis.txt')
        print(f"Writing results to: {output_file}")
        
        with open(output_file, 'w') as f:
            f.write("COMPREHENSIVE MATHEMATICAL ANALYSIS\n")
            f.write("=" * 50 + "\n")
            f.write(f"Analysis run on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total runtime: {time.time() - start_time:.2f} seconds\n")
            f.write(f"Successful analyses: {completed}/{len(analyses)}\n\n")
            
            for analysis_type, result in results.items():
                write_analysis_results(f, analysis_type, result)
        
        print(f"\nAnalysis complete! Total runtime: {time.time() - start_time:.2f} seconds")
        print(f"Successfully completed {completed} out of {len(analyses)} analyses")
        print(f"Results have been written to:\n  {output_file}")
        
    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e}")
    except PermissionError as e:
        print(f"Error: Permission denied - {e}")
    except Exception as e:
        print(f"Unexpected error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    comprehensive_analysis() 