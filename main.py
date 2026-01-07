#!/usr/bin/env python3
"""Main entry point for Starlink Security Foundation."""

import asyncio
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from starlink_security import StarlinkSecurityFoundation


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Starlink Security Foundation - Enterprise security for Starlink infrastructure"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
        default=None
    )
    
    args = parser.parse_args()
    
    foundation = StarlinkSecurityFoundation(config_path=args.config)
    await foundation.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete")
        sys.exit(0)
