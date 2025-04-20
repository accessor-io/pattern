const fs = require('fs');
const readline = require('readline');
const crypto = require('crypto');

function hexKeyToAscii(key) {
    if (key === 0n) return '';
    const byte = Number(key & 0xFFn);
    const char = (byte >= 0x20 && byte <= 0x7E) ? String.fromCharCode(byte) : '.';
    return hexKeyToAscii(key >> 8n) + char;
}

async function processFile(inputFile, outputFile) {
    const fileStream = fs.createReadStream(inputFile);
    const rl = readline.createInterface({
        input: fileStream,
        crlfDelay: Infinity
    });

    const outputStream = fs.createWriteStream(outputFile);

    for await (const line of rl) {
        const processedLine = processLine(line);
        outputStream.write(processedLine + '\n');
    }

    console.log(`Processing complete. Output written to ${outputFile}`);
}

function processLine(line) {
    const match = line.match(/Key:\s+(0x[\da-f]+)/i);
    if (!match) return line;
    
    try {
        const hexKey = BigInt(match[1]);
        const ascii = hexKeyToAscii(hexKey);
        return line.replace(/=> ASCII: \S+/, `=> ASCII: ${ascii}`);
    } catch (error) {
        console.error(`Error processing line: ${line}`);
        return line;
    }
}

function predictNextTerms(seedKey, startIndex, count) {
    let current = BigInt(seedKey);
    const results = [];
    
    for (let i = 0; i < count; i++) {
        current = generateNextKey(current, startIndex + i);
        results.push({
            index: startIndex + i + 1,
            key: `0x${current.toString(16).padStart(64, '0')}`,
            ascii: hexKeyToAscii(current)
        });
    }
    
    return results;
}

// Usage: node hexToAsciiProcessor.js input.txt output.txt
const [inputFile, outputFile] = process.argv.slice(2);
if (!inputFile || !outputFile) {
    console.log('Usage: node hexToAsciiProcessor.js <input-file> <output-file>');
    process.exit(1);
}

processFile(inputFile, outputFile).catch(console.error); 