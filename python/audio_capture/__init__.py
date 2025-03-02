"""
Audio Capture - A cross-platform audio capture library for Python
"""

from .capture import AudioCapture, AudioFormat
from .utils import WavWriter

__version__ = "0.1.0"
__all__ = ['AudioCapture', 'AudioFormat', 'WavWriter'] 