function generateNextKey(prevKey, index) {
    // Convert to 32-byte buffer for cryptographic operations
    const keyBuffer = bigIntToBuffer(prevKey);
    
    // Use HMAC-SHA256 with index-based salt
    const hmac = crypto.createHmac('sha256', `salt-${index}`);
    hmac.update(keyBuffer);
    
    // Return as BigInt from the first 32 bytes
    return bufferToBigInt(hmac.digest());
}

// Helper functions for BigInt <-> Buffer conversion
function bigIntToBuffer(bn) {
    const hex = bn.toString(16).padStart(64, '0');
    return Buffer.from(hex, 'hex');
}

function bufferToBigInt(buf) {
    return BigInt('0x' + buf.toString('hex'));
}

// Example generation for next 5 terms after 0x2832ed74f2b5e35ee
let currentKey = 0x2832ed74f2b5e35een;
for (let i = 0; i < 5; i++) {
    currentKey += BigInt([2,4,1,13,28][i % 5]);
    console.log(`Next key: 0x${currentKey.toString(16)}`);
    console.log(`ASCII: ${hexKeyToAscii(currentKey)}`);
} 