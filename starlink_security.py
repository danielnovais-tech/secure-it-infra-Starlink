"""
Starlink Security Infrastructure Management
Main application module with structured logging configuration
"""

import logging
import os
from pathlib import Path

# Constants - use local directories if system directories are not writable
if os.access("/etc", os.W_OK):
    CONFIG_DIR = Path("/etc/starlink-security")
    DATA_DIR = Path("/var/lib/starlink-security")
    LOG_DIR = Path("/var/log/starlink-security")
else:
    # Fallback to local directories for development/testing
    CONFIG_DIR = Path("./config")
    DATA_DIR = Path("./data")
    LOG_DIR = Path("./logs")

# Create directories if they don't exist
LOG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'starlink_security.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('starlink-security')


def main():
    """Main entry point for the Starlink Security application."""
    logger.info("Starlink Security Infrastructure starting...")
    logger.info(f"Config directory: {CONFIG_DIR}")
    logger.info(f"Data directory: {DATA_DIR}")
    logger.info(f"Log directory: {LOG_DIR}")


if __name__ == "__main__":
    main()
