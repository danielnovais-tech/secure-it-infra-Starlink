#!/usr/bin/env python3
"""
Main entry point for the Network Security Monitor
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from network_security_monitor import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
