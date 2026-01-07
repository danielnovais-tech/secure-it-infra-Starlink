#!/usr/bin/env python3
"""Main entry point for Starlink Security Foundation."""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from starlink_security import StarlinkSecurityFoundation


def configure_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


async def async_main():
    """Main async entry point."""
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


def main():
    """Main synchronous entry point."""
    configure_logging()
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\nShutdown complete")
        sys.exit(0)


if __name__ == "__main__":
    main()
