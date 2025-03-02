#!/usr/bin/env python3
"""
Entry point script to run the Solana GPT analysis.
"""

import os
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analysis.solana_gpt_analysis import run_analysis

if __name__ == "__main__":
    run_analysis() 