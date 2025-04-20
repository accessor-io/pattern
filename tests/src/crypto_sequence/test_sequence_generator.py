from crypto_sequence import SequenceGenerator 
from bn import BN 

def test_term_66_specific():
    # Using EC library's verification methodology
    gen = SequenceGenerator(0x1a838b13505b26867)
    term66 = gen._next_transformation()
    
    # EC-style modular verification
    n = BN(2**66)
    r = BN(term66).umod(n)
    s = BN(term66).ushrn(66)
    
    assert r.cmp(BN(0x2832ed74f2b5e35ee)) == 0
    assert s.cmp(BN(0)) == 0  # Ensure no overflow 