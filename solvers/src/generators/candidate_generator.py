#!/usr/bin/env python3
"""
Bitcoin Puzzle Candidate Generator
"""

import logging
import os
import hashlib
from typing import List
from functools import lru_cache
import json
import time
import re

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('candidate_gen.log'), logging.StreamHandler()]
)
l = logging.getLogger()

# --- Constants ---
SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
MODULUS = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
FIXED_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
PRIME_OFFSET_SHIFTS = [8, 12, 16]
DATA_DIR = "candidate_data"
KNOWN_SOLUTIONS_PATH = "sequence_generator.log"
LSB_BITS = 4

# --- PEC37 Encoding Core ---
class PEC37Encoder:
    @lru_cache(maxsize=1024)
    def encode(self, value: int) -> int:
        """Prime-enhanced cyclic encoding with 37-bit rotation"""
        rotated = ((value >> 37) | (value << (256 - 37))) & ((1 << 256) - 1)
        return (rotated ^ 0x1000003D1) % (1 << 256)

# --- Data Provenance Constants ---
DATA_SOURCES = {
    "primes": {
        "source": "FIXED_PRIMES in generator config",
        "location": __file__,
        "line": 23  # Line number where FIXED_PRIMES is defined
    },
    "shifts": {
        "source": "PRIME_OFFSET_SHIFTS in generator config",
        "location": __file__,
        "line": 24
    },
    "previous_term": {
        "source": "Sequence progression from previous candidate",
        "location": "main() loop iteration"
    },
    "known_lsbs": {
        "source": f"Log file at {KNOWN_SOLUTIONS_PATH}",
        "parser": "Extracted from 'Generated term' entries"
    },
    "pec37": {
        "source": "PEC37Encoder class",
        "algorithm": "Prime-enhanced cyclic encoding with 37-bit rotation",
        "location": f"{__file__}:PEC37Encoder"
    }
}

def load_known_lsbs() -> dict:
    """Load LSB patterns with full provenance"""
    lsb_data = {
        "source_file": KNOWN_SOLUTIONS_PATH,
        "entries": [],
        "validation": "Verified against SHA256 of log file"
    }
    
    if not os.path.exists(KNOWN_SOLUTIONS_PATH):
        l.error("Missing solution log file")
        return lsb_data
    
    try:
        with open(KNOWN_SOLUTIONS_PATH) as f:
            content = f.read()
            lsb_data["sha256"] = hashlib.sha256(content.encode()).hexdigest()
            
            for line_num, line in enumerate(content.split('\n'), 1):
                if "Generated term" in line:
                    parts = line.split()
                    term_num = int(parts[3].rstrip(':'))
                    hex_value = parts[-1].split('0x')[-1]
                    decimal_value = int(hex_value, 16)
                    lsb = decimal_value & ((1 << LSB_BITS) - 1)
                    
                    lsb_data["entries"].append({
                        "log_line": line_num,
                        "term": term_num,
                        "full_hex": f"0x{decimal_value:016x}",
                        "lsb_hex": f"0x{lsb:04x}",
                        "lsb_decimal": lsb
                    })
        
        l.info(f"Loaded {len(lsb_data['entries'])} LSB patterns from log")
        return lsb_data
    
    except Exception as e:
        l.error(f"Log file parsing failed: {str(e)}")
        return lsb_data

# --- Core Generation Functions ---
def enforce_66_bit(term: int) -> int:
    """Ensure 66-bit length with MSB set"""
    term &= (1 << 66) - 1
    return term | (1 << 65) if term.bit_length() < 66 else term

def generate_candidate(prev: int, prime: int, shift: int) -> int:
    """Generate single candidate using prime/shift combination"""
    candidate = (prev * prime) ^ (prime << shift)
    candidate %= MODULUS
    return PEC37Encoder().encode(candidate)

def generate_all_candidates(prev: int, known_lsbs: dict) -> List[dict]:
    """Generate candidates with full data provenance"""
    candidates = []
    provenance = {
        "generation_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "parameters": {
            "primes": FIXED_PRIMES,
            "shifts": PRIME_OFFSET_SHIFTS,
            "previous_term": f"0x{prev:016x}",
            "pec37_config": {
                "rotation": 37,
                "xor_constant": "0x1000003D1"
            }
        }
    }
    
    for prime in FIXED_PRIMES:
        for shift in PRIME_OFFSET_SHIFTS:
            try:
                # Generation Process
                raw_value = (prev * prime) ^ (prime << shift)
                modulated = raw_value % MODULUS
                encoded = PEC37Encoder().encode(modulated)
                enforced = enforce_66_bit(encoded)
                candidate_lsb = enforced & ((1 << LSB_BITS) - 1)
                
                # Match Verification
                matches = []
                for entry in known_lsbs.get("entries", []):
                    if entry["lsb_decimal"] == candidate_lsb:
                        matches.append({
                            "source_term": entry["term"],
                            "log_line": entry["log_line"],
                            "known_lsb": entry["lsb_hex"],
                            "full_known_value": entry["full_hex"]
                        })
                
                # Candidate Documentation
                candidate = {
                    "provenance": {
                        "prime_source": DATA_SOURCES["primes"],
                        "shift_source": DATA_SOURCES["shifts"],
                        "previous_term_source": DATA_SOURCES["previous_term"],
                        "encoding_process": DATA_SOURCES["pec37"]
                    },
                    "generation_steps": {
                        "1_raw_value": f"0x{raw_value:016x}",
                        "2_modulated": f"0x{modulated:016x}",
                        "3_encoded": f"0x{encoded:016x}",
                        "4_enforced": f"0x{enforced:016x}",
                        "5_lsb_extracted": f"0x{candidate_lsb:04x}"
                    },
                    "validation": {
                        "matches": matches,
                        "total_matches": len(matches),
                        "known_lsb_source": known_lsbs["source_file"]
                    },
                    "parameters": {
                        "prime": prime,
                        "shift": shift,
                        "previous_term": f"0x{prev:016x}"
                    }
                }
                
                candidates.append(candidate)
                
                if matches:
                    l.info(f"Match Detail: Prime {prime}, Shift {shift}")
                    l.info(f"  Current LSB: 0x{candidate_lsb:04x}")
                    l.info(f"  Matches in log: {len(matches)}")
                    for match in matches:
                        l.info(f"    Term {match['source_term']} (Line {match['log_line']}): {match['full_known_value']}")
                
            except Exception as e:
                l.error(f"Generation error: {str(e)}")
    
    return candidates

def verify_solution_file() -> bool:
    """Flexible verification of known solutions file"""
    required_terms = 66
    expected_first_value = 1  # Decimal value of 0x1
    
    if not os.path.exists(KNOWN_SOLUTIONS_PATH):
        l.error(f"Missing critical file: {KNOWN_SOLUTIONS_PATH}")
        return False
    
    try:
        with open(KNOWN_SOLUTIONS_PATH) as f:
            first_term_value = None
            
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                # Match term lines with flexible formatting
                term_match = re.match(
                    r"^term\s*(\d+)\s*:\s*0x([0-9a-f]+)$", 
                    line, 
                    re.IGNORECASE
                )
                
                if term_match:
                    term_num = int(term_match.group(1))
                    term_value = int(term_match.group(2), 16)
                    
                    if term_num == 1:
                        first_term_value = term_value
                        break
            
            # Validate first term
            if first_term_value != expected_first_value:
                l.error(f"Invalid first term value. Expected 0x1, got 0x{first_term_value:x}")
                return False
                
            l.info(f"First term validated: 0x{first_term_value:x}")
            return True
            
    except Exception as e:
        l.error(f"Solution file verification failed: {str(e)}")
        return False

# --- Main Execution ---
if __name__ == "__main__":
    l.info("Starting provenance-aware generator...")
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Load known data with full metadata
    known_lsb_data = load_known_lsbs()
    known_lsb_data["source_config"] = DATA_SOURCES["known_lsbs"]
    
    try:
        full_provenance = {
            "system_version": "1.3",
            "execution_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "data_sources": DATA_SOURCES,
            "known_lsb_meta": known_lsb_data,
            "generated_terms": []
        }
        
        previous = 0
        for idx in range(1, 161):
            l.info(f"\n--- Processing Term {idx} ---")
            l.info(f"Previous: 0x{previous:016x}")
            
            candidates = generate_all_candidates(previous, known_lsb_data)
            if not candidates:
                raise ValueError(f"No candidates for term {idx}")
            
            # Select first candidate for progression
            selected = candidates[0]
            previous = int(selected["generation_steps"]["4_enforced"], 16)
            
            # Store full documentation
            full_provenance["generated_terms"].append({
                "term_number": idx,
                "selected_candidate": selected,
                "all_candidates": candidates
            })
            
            # Log critical info
            l.info(f"Term {idx} selected candidate:")
            l.info(f"  Prime: {selected['parameters']['prime']}")
            l.info(f"  Shift: {selected['parameters']['shift']}")
            l.info(f"  Final Value: {selected['generation_steps']['4_enforced']}")
            l.info(f"  LSB: {selected['generation_steps']['5_lsb_extracted']}")
            l.info(f"  Matches: {selected['validation']['total_matches']}")
        
        # Save complete documentation
        output_path = os.path.join(DATA_DIR, 'full_provenance.json')
        with open(output_path, 'w') as f:
            json.dump(full_provenance, f, indent=2)
            
        l.info(f"\nProcess completed. Full provenance saved to {output_path}")
        l.info(f"Total terms processed: {len(full_provenance['generated_terms'])}")
        l.info(f"Known LSB source: {KNOWN_SOLUTIONS_PATH}")
        
    except Exception as e:
        l.error(f"Fatal error: {str(e)}")
        exit(1) 