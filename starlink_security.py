"""
Starlink Security Infrastructure Management
Main application module with structured logging configuration
"""

import logging
from pathlib import Path

# Constants
CONFIG_DIR = Path("/etc/starlink-security")
DATA_DIR = Path("/var/lib/starlink-security")
LOG_DIR = Path("/var/log/starlink-security")

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler('starlink_security.log'),
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
