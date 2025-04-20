#!/bin/bash
# Test Bitcoin components
pytest src/bitcoin/tests/

# Test audio processing
pytest src/audio_processing/tests/

# Validate data integrity
python scripts/validation/verify_data_sanity.py 