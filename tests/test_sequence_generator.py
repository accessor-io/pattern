import pytest
from sequence_generator import SequenceGenerator

# Updated test data from section 13 of analysis
VALIDATED_SEQUENCE = [
    0x1a838b13505b26867,  # Initial value (matches doc)
    0x8a6a29ed38b664511436128ebace8d6ec1180000000000000000000000000000,
    0x14600000000000000000000000000000000000000000000000000000000000000
]

def test_known_sequence_validation():
    """Test sequence from cryptographic_analysis.md section 13"""
    gen = SequenceGenerator(VALIDATED_SEQUENCE[0])
    assert gen.validate(VALIDATED_SEQUENCE[1:]), "Documented sequence validation failed"

def test_grid_movement_pattern():
    """Verify 4-5 directional pattern from section 4"""
    gen = SequenceGenerator(0x01)
    
    # First 8 moves should follow → ↓ → → ↓ → ↓ → → pattern
    positions = []
    for _ in range(8):
        gen._next_transformation()
        positions.append(gen.grid_position)
    
    assert positions == [
        (1,0), (1,1), (2,1), (3,1), (3,2), (4,2), (4,3), (5,3)
    ], "Grid movement pattern mismatch"

def test_sequence_validation():
    """Test sequence validation against documented values"""
    generator = SequenceGenerator(VALIDATED_SEQUENCE[0])
    assert generator.validate(VALIDATED_SEQUENCE[1:]), "Sequence validation failed"

def test_grid_position_tracking():
    """Test grid position tracking during generation"""
    generator = SequenceGenerator(VALIDATED_SEQUENCE[0])
    generator._next_transformation()
    assert generator.grid_position == (1, 0), "First move should be right"
    
    generator._next_transformation()
    assert generator.grid_position == (1, 1), "Second move should be down"

def test_bit_requirement_enforcement():
    """Test 66-bit requirement from section 14"""
    generator = SequenceGenerator(VALIDATED_SEQUENCE[0])
    value = generator._next_transformation()
    assert bin(value).count('1') == 66, "Must have exactly 66 bits set"

def test_initial_terms():
    """Verify first 4 terms match cryptographic requirements"""
    initial_sequence = [
        0x01,  # Term 1
        0x03,  # Term 2 (0x01 ^ 2)
        0x07,  # Term 3 (0x03 ^ 4)
        0x08   # Term 4 (0x07 ^ 15)
    ]
    
    gen = SequenceGenerator(initial_sequence[0])
    assert gen.validate(initial_sequence[1:]), "Initial sequence validation failed"

def test_puzzle_1_solution():
    """Direct test for puzzle 1 solution"""
    gen = SequenceGenerator(0x01)
    # Verify initial state remains unchanged
    assert gen.current == 0x01, "Puzzle 1 solution mismatch"
    assert gen.position == 0, "Position should not advance without transformation"
    
    # First transformation should produce term 2
    term2 = gen._next_transformation()
    assert term2 == 0x03, "Term 2 mismatch"

def test_term_66_specific():
    """Special test for term 66 requirements"""
    gen = SequenceGenerator(0x1a838b13505b26867)  # Term 65
    term66 = gen._next_transformation()
    
    # Verify cryptographic properties
    assert term66 == 0x2832ed74f2b5e35ee, "Value mismatch"
    assert bin(term66).count('1') == 66, "Bit count mismatch"
    assert term66.bit_length() == 66, "Bit length mismatch"
    
    # Verify transformation steps
    prev = int(KNOWN_SOLUTIONS[65], 16)
    calculated = ((prev + 2)**4 % 256) ^ 247  # 247 is key_numbers[2]
    assert (term66 >> 56) == calculated, "Core transformation mismatch" 