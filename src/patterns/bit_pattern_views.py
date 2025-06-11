def analyze_bit_views(hex_string):
    """Analyze a hex string in different bit views."""
    # Convert hex to binary string (256 bits)
    binary = bin(int(hex_string, 16))[2:].zfill(256)
    
    # Count set bits and their indices
    set_bits = []
    for i, bit in enumerate(binary):
        if bit == '1':
            set_bits.append(i)
    
    result = {
        'hex': hex_string,
        'bits_set': len(set_bits),
        'set_bit_indices': set_bits,
        'views': {
            'byte': [],    # 8-bit chunks
            'word': [],    # 16-bit chunks
            'dword': [],   # 32-bit chunks
            'qword': []    # 64-bit chunks
        }
    }
    
    # Byte view (8-bit chunks)
    for i in range(0, 256, 8):
        chunk = binary[i:i+8]
        result['views']['byte'].append({
            'index': i // 8,
            'range': f"{i}-{i+7}",
            'bits': chunk
        })
    
    # Word view (16-bit chunks)
    for i in range(0, 256, 16):
        chunk = binary[i:i+16]
        result['views']['word'].append({
            'index': i // 16,
            'range': f"{i}-{i+15}",
            'bits': chunk
        })
    
    # Double word view (32-bit chunks)
    for i in range(0, 256, 32):
        chunk = binary[i:i+32]
        result['views']['dword'].append({
            'index': i // 32,
            'range': f"{i}-{i+31}",
            'bits': chunk
        })
    
    # Quad word view (64-bit chunks)
    for i in range(0, 256, 64):
        chunk = binary[i:i+64]
        result['views']['qword'].append({
            'index': i // 64,
            'range': f"{i}-{i+63}",
            'bits': chunk
        })
    
    return result

def format_bit_views(analysis):
    """Format the bit views analysis into a readable string."""
    output = []
    output.append(f"Hex:   {analysis['hex']}")
    output.append(f"Bits:  {analysis['bits_set']} bits set")
    output.append(f"Index: {analysis['set_bit_indices']}\n")
    
    # Byte view
    output.append("Byte view (8-bit chunks):")
    for chunk in analysis['views']['byte']:
        output.append(f"[{chunk['index']:2d}] {chunk['range']:>7} : {chunk['bits']}")
        if chunk['index'] % 8 == 7:
            output.append("")
    
    # Word view
    output.append("\nWord view (16-bit chunks):")
    for chunk in analysis['views']['word']:
        output.append(f"[{chunk['index']:2d}] {chunk['range']:>7} : {chunk['bits']}")
        if chunk['index'] % 4 == 3:
            output.append("")
    
    # Double word view
    output.append("\nDouble word view (32-bit chunks):")
    for chunk in analysis['views']['dword']:
        output.append(f"[{chunk['index']:2d}] {chunk['range']:>7} : {chunk['bits']}")
        if chunk['index'] % 4 == 3:
            output.append("")
    
    # Quad word view
    output.append("\nQuad word view (64-bit chunks):")
    for chunk in analysis['views']['qword']:
        output.append(f"[{chunk['index']:2d}] {chunk['range']:>7} : {chunk['bits']}")
        if chunk['index'] % 2 == 1:
            output.append("")
    
    return "\n".join(output) 