import pytest
from crypto_sequence import SequenceGenerator
import logging
from logging_config import configure_logging

def test_logging_output(caplog):
    configure_logging()
    caplog.set_level(logging.DEBUG)
    
    gen = SequenceGenerator(0x01)
    gen.validate([0x03, 0x07])
    
    # Verify critical logs
    assert "Initializing generator with value: 0x1" in caplog.text
    assert "Grid position updated from (0, 0) to (1, 0)" in caplog.text
    assert "Validation succeeded" in caplog.text 