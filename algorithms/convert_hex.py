import base64
import json
import math

def read_hex_strings(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]

def write_decimal(output_file, hex_strings):
    with open(output_file, 'w') as f:
        for hex_str in hex_strings:
            decimal = int(hex_str, 16)
            f.write(f"{decimal}\n")

def write_binary(output_file, hex_strings):
    with open(output_file, 'w') as f:
        for hex_str in hex_strings:
            binary = bin(int(hex_str, 16))[2:].zfill(256)  # 32 bytes = 256 bits
            f.write(f"{binary}\n")

def write_base64(output_file, hex_strings):
    with open(output_file, 'w') as f:
        for hex_str in hex_strings:
            bytes_data = bytes.fromhex(hex_str)
            base64_str = base64.b64encode(bytes_data).decode('utf-8')
            f.write(f"{base64_str}\n")

def write_int_array(output_file, hex_strings):
    with open(output_file, 'w') as f:
        f.write("[\n")
        for i, hex_str in enumerate(hex_strings):
            decimal = int(hex_str, 16)
            f.write(f"    {decimal}")
            if i < len(hex_strings) - 1:
                f.write(",")
            f.write("\n")
        f.write("]\n")

def write_octal(output_file, hex_strings):
    with open(output_file, 'w') as f:
        for hex_str in hex_strings:
            octal = oct(int(hex_str, 16))[2:]  # Remove '0o' prefix
            f.write(f"{octal}\n")

def write_scientific(output_file, hex_strings):
    with open(output_file, 'w') as f:
        for hex_str in hex_strings:
            decimal = int(hex_str, 16)
            scientific = f"{decimal:e}"
            f.write(f"{scientific}\n")

def write_hex_formatted(output_file, hex_strings):
    with open(output_file, 'w') as f:
        for hex_str in hex_strings:
            # Format with 0x prefix and groups of 2
            formatted = "0x" + " ".join(hex_str[i:i+2] for i in range(0, len(hex_str), 2))
            f.write(f"{formatted}\n")

def write_bytes_array(output_file, hex_strings):
    with open(output_file, 'w') as f:
        f.write("[\n")
        for i, hex_str in enumerate(hex_strings):
            bytes_array = [int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2)]
            f.write(f"    {bytes_array}")
            if i < len(hex_strings) - 1:
                f.write(",")
            f.write("\n")
        f.write("]\n")

def write_utf8_bytes(output_file, hex_strings):
    with open(output_file, 'w') as f:
        for hex_str in hex_strings:
            bytes_data = bytes.fromhex(hex_str)
            byte_string = " ".join(f"\\x{b:02x}" for b in bytes_data)
            f.write(f"b'{byte_string}'\n")

def write_binary_groups(output_file, hex_strings):
    with open(output_file, 'w') as f:
        for hex_str in hex_strings:
            binary = bin(int(hex_str, 16))[2:].zfill(256)
            # Group by bytes (8 bits)
            grouped = " ".join(binary[i:i+8] for i in range(0, len(binary), 8))
            f.write(f"{grouped}\n")

def write_properties(output_file, hex_strings):
    with open(output_file, 'w') as f:
        for i, hex_str in enumerate(hex_strings):
            decimal = int(hex_str, 16)
            f.write(f"Number {i+1}:\n")
            f.write(f"  Decimal: {decimal}\n")
            f.write(f"  Hex: 0x{hex_str}\n")
            f.write(f"  Binary Length: {len(bin(decimal)[2:])}\n")
            f.write(f"  Number of Digits: {len(str(decimal))}\n")
            f.write(f"  Is Prime: {is_prime(decimal)}\n")
            f.write(f"  Square Root: {math.sqrt(decimal):.2f}\n")
            f.write("\n")

def is_prime(n):
    if n < 2:
        return (False, None)
    i = 1
    primorial = 2
    current_prime = 2
    while primorial < n:
        i += 1
        current_prime = nextprime(current_prime)
        primorial *= current_prime
    return (primorial == n, i) if primorial == n else (False, None)

def write_csv(output_file, hex_strings):
    with open(output_file, 'w') as f:
        for hex_str in hex_strings:
            # Convert hex to binary sequence
            binary = bin(int(hex_str, 16))[2:].zfill(256)
            signal = np.array([int(b) for b in binary], dtype=float)
            
            f.write(f"Original hex: {hex_str}\n")
            
            # Basic signal properties
            f.write("\nSignal Properties:\n")
            f.write(f"  Number of bits: {len(signal)}\n")
            f.write(f"  Number of 1s: {np.sum(signal)}\n")
            f.write(f"  Number of 0s: {len(signal) - np.sum(signal)}\n")
            f.write(f"  Ratio of 1s: {np.mean(signal):.3f}\n")
            
            # Bit transitions
            transitions = np.diff(signal)
            f.write(f"  Number of transitions: {np.count_nonzero(transitions)}\n")
            f.write(f"  Transition rate: {np.count_nonzero(transitions)/len(transitions):.3f}\n")
            
            # Run length analysis
            runs = []
            current_run = 1
            for i in range(1, len(signal)):
                if signal[i] == signal[i-1]:
                    current_run += 1
                else:
                    runs.append(current_run)
                    current_run = 1
            runs.append(current_run)
            
            if runs:
                f.write("\nRun Length Analysis:\n")
                f.write(f"  Longest run: {max(runs)}\n")
                f.write(f"  Average run length: {np.mean(runs):.2f}\n")
                f.write(f"  Number of runs: {len(runs)}\n")
            
            # Frequency domain analysis
            fft_result = np.abs(np.fft.fft(signal))
            frequencies = np.fft.fftfreq(len(signal))
            
            f.write("\nFrequency Domain Analysis:\n")
            f.write(f"  DC component: {fft_result[0]:.3f}\n")
            
            # Find dominant frequencies (excluding DC)
            dominant_freqs = sorted(zip(frequencies[1:], fft_result[1:]), 
                                 key=lambda x: x[1], reverse=True)[:3]
            
            f.write("  Dominant frequencies (normalized):\n")
            for freq, mag in dominant_freqs:
                f.write(f"    Frequency: {freq:.3f}, Magnitude: {mag:.3f}\n")
            
            # Entropy calculation
            probabilities = np.bincount(signal.astype(int)) / len(signal)
            entropy = -np.sum(p * np.log2(p) if p > 0 else 0 for p in probabilities)
            f.write(f"\nInformation Content:\n")
            f.write(f"  Bit entropy: {entropy:.3f} bits\n")
            f.write(f"  Compression potential: {(1 - entropy/np.log2(2))*100:.1f}%\n")
            
            f.write("\n")

def write_audio_features(output_file, hex_strings):
    with open(output_file, 'w') as f:
        for hex_str in hex_strings:
            # Convert hex to binary sequence
            binary = bin(int(hex_str, 16))[2:].zfill(256)
            # Group bits into bytes for audio analysis
            bytes_data = [int(binary[i:i+8], 2) for i in range(0, len(binary), 8)]
            samples = np.array(bytes_data, dtype=float) / 128.0 - 1.0
            
            f.write(f"Original hex: {hex_str}\n")
            
            # Basic audio features
            f.write("\nAudio Features:\n")
            f.write(f"  Mean amplitude: {np.mean(samples):.3f}\n")
            f.write(f"  Peak amplitude: {np.max(np.abs(samples)):.3f}\n")
            f.write(f"  RMS level: {np.sqrt(np.mean(samples**2)):.3f}\n")
            
            # Spectral analysis
            if len(samples) >= 8:
                spectrum = np.abs(np.fft.fft(samples))
                freqs = np.fft.fftfreq(len(samples))
                
                # Find spectral peaks
                from scipy.signal import find_peaks
                peaks, _ = find_peaks(spectrum)
                if len(peaks) > 0:
                    f.write("\nSpectral Features:\n")
                    f.write(f"  Number of peaks: {len(peaks)}\n")
                    # Sort peaks by magnitude
                    peak_mags = [(freqs[p], spectrum[p]) for p in peaks]
                    peak_mags.sort(key=lambda x: x[1], reverse=True)
                    for freq, mag in peak_mags[:3]:  # Show top 3 peaks
                        f.write(f"    Frequency: {freq:.3f}, Magnitude: {mag:.3f}\n")
            
            f.write("\n")

def write_waveform_analysis(output_file, hex_strings):
    with open(output_file, 'w') as f:
        for hex_str in hex_strings:
            # Convert hex to binary sequence
            binary = bin(int(hex_str, 16))[2:].zfill(256)
            signal = np.array([int(b) for b in binary], dtype=float)
            
            f.write(f"Original hex: {hex_str}\n")
            
            # Basic waveform statistics
            f.write("\nWaveform Statistics:\n")
            f.write(f"  Mean level: {np.mean(signal):.3f}\n")
            f.write(f"  Peak level: {np.max(signal):.3f}\n")
            f.write(f"  RMS level: {np.sqrt(np.mean(signal**2)):.3f}\n")
            
            # Level distribution
            unique_levels, level_counts = np.unique(signal, return_counts=True)
            f.write("\nLevel Distribution:\n")
            for level, count in zip(unique_levels, level_counts):
                percentage = (count / len(signal)) * 100
                f.write(f"  Level {int(level)}: {count} samples ({percentage:.1f}%)\n")
            
            # Segment analysis (32-bit segments)
            segment_length = 32
            segments = [signal[i:i+segment_length] for i in range(0, len(signal), segment_length)]
            segment_means = [np.mean(seg) for seg in segments]
            segment_vars = [np.var(seg) for seg in segments]
            
            f.write(f"\nSegment Analysis ({segment_length}-bit segments):\n")
            f.write(f"  Number of segments: {len(segments)}\n")
            f.write(f"  Most active segment: {np.argmax(segment_vars) + 1}\n")
            f.write(f"  Least active segment: {np.argmin(segment_vars) + 1}\n")
            f.write(f"  Segment activity variation: {np.std(segment_vars):.3f}\n")
            
            f.write("\n")

def main():
    input_file = "data/32bHex.txt"
    hex_strings = read_hex_strings(input_file)
    
    # Create output directory if it doesn't exist
    import os
    os.makedirs("data", exist_ok=True)
    
    # Original conversions
    write_decimal("data/decimal_values.txt", hex_strings)
    write_binary("data/binary_values.txt", hex_strings)
    write_base64("data/base64_values.txt", hex_strings)
    write_int_array("data/int_array.json", hex_strings)
    write_float_representations("data/float_values.txt", hex_strings)
    write_ip_addresses("data/ip_addresses.txt", hex_strings)
    write_time_representations("data/timestamps.txt", hex_strings)
    write_uuid_representations("data/uuids.txt", hex_strings)
    write_coordinate_representations("data/coordinates.txt", hex_strings)
    write_color_representations("data/colors.txt", hex_strings)
    write_binary_data_types("data/binary_types.txt", hex_strings)
    write_text_encodings("data/text_encodings.txt", hex_strings)
    write_bitwise_analysis("data/bitwise_analysis.txt", hex_strings)
    
    # Mathematical conversions
    write_complex_numbers("data/complex_numbers.txt", hex_strings)
    write_rational_numbers("data/rational_numbers.txt", hex_strings)
    write_cryptographic_hashes("data/crypto_hashes.txt", hex_strings)
    write_extended_dates("data/extended_dates.txt", hex_strings)
    write_extended_coordinates("data/extended_coordinates.txt", hex_strings)
    write_extended_colors("data/extended_colors.txt", hex_strings)
    write_pattern_analysis("data/pattern_analysis.txt", hex_strings)
    
    # Audio/Signal analysis
    write_signal_analysis("data/signal_analysis.txt", hex_strings)
    write_audio_features("data/audio_features.txt", hex_strings)
    write_waveform_analysis("data/waveform_analysis.txt", hex_strings)

if __name__ == "__main__":
    main() 