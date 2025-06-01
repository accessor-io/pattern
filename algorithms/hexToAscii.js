function hexKeyToAscii(key) {
    // Base case: empty string when no bytes left
    if (key === 0n) return '';
    
    // Get least significant byte (last 8 bits)
    const byte = Number(key & 0xFFn);
    // Convert to character or dot if non-printable
    const char = (byte >= 0x20 && byte <= 0x7E) ? String.fromCharCode(byte) : '.';
    
    // Recursively process remaining bytes (shift right by 8 bits)
    return hexKeyToAscii(key >> 8n) + char;
}

// Example usage for index 23 (0x556e52 -> "UnR")
// console.log(hexKeyToAscii(0x556e52n));  // Outputs "UnR" 