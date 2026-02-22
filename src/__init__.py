"""
LLM Backdoor Scanner

This package provides tools for detecting backdoors in Large Language Models
using attention matrix analysis based on "The Trigger in the Haystack" paper.

Main modules:
- attention_monitor: Core attention monitoring and hijacking detection
- scanner: High-level scanner interface
- visualization: Plotting and visualization utilities
"""

from .attention_monitor import AttentionMonitor
from .scanner import BackdoorScanner, ScanResult
from .visualization import AttentionVisualizer

__version__ = "0.1.0"
__author__ = "LLM Security Research"

__all__ = [
    "AttentionMonitor",
    "BackdoorScanner", 
    "ScanResult",
    "AttentionVisualizer",
]