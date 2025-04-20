"""
Audio Processing System
A comprehensive audio processing and synthesis system with real-time capabilities.
"""

from .core.integration import IntegrationInterface
from .core.engine import AudioProcessingApplication

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    'AudioProcessingApplication',
    'IntegrationInterface'
] 