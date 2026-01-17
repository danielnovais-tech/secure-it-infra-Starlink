#!/usr/bin/env python3
"""
Wrapper script to run the Starlink monitor.
This makes it easier to execute without module syntax.
"""
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main monitor
from src.starlink_monitor import main

if __name__ == "__main__":
    main()
