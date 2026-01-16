"""
Starlink Security Infrastructure Management
Main application module with structured logging configuration
"""

import json
import logging
import logging.handlers
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

# Configurable log level from environment variable (default: INFO)
LOG_LEVEL = os.getenv('STARLINK_LOG_LEVEL', 'INFO').upper()
LOG_FORMAT = os.getenv('STARLINK_LOG_FORMAT', 'standard').lower()

# Maximum log file size (10 MB) and backup count (7 days worth)
MAX_LOG_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 7


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        """Format log record as JSON."""
        log_data = {
            'timestamp': self.formatTime(record, self.datefmt),
            'logger': record.name,
            'level': record.levelname,
            'module': record.module,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


# Configure handlers
file_handler = logging.handlers.RotatingFileHandler(
    LOG_DIR / 'starlink_security.log',
    maxBytes=MAX_LOG_BYTES,
    backupCount=BACKUP_COUNT
)

console_handler = logging.StreamHandler()

# Set formatters based on configuration
if LOG_FORMAT == 'json':
    file_handler.setFormatter(JSONFormatter())
    console_handler.setFormatter(JSONFormatter())
else:
    standard_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(standard_formatter)
    console_handler.setFormatter(standard_formatter)

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger('starlink-security')

# Security note: Ensure sensitive data is never logged
# Filter or sanitize passwords, tokens, API keys, and PII before logging


def main():
    """Main entry point for the Starlink Security application."""
    logger.info("Starlink Security Infrastructure starting...")
    logger.info(f"Config directory: {CONFIG_DIR}")
    logger.info(f"Data directory: {DATA_DIR}")
    logger.info(f"Log directory: {LOG_DIR}")
    logger.info(f"Log level: {LOG_LEVEL}")
    logger.info(f"Log format: {LOG_FORMAT}")
    logger.info(f"Log rotation: {MAX_LOG_BYTES} bytes, {BACKUP_COUNT} backups")
    
    # Example of logging with correlation ID
    # In production, request_id would come from request context
    extra = {'request_id': 'req-12345', 'user_id': 'user-67890'}
    logger.info("Example log with correlation metadata", extra=extra)
    
    # Example of different log levels
    logger.debug("This is a debug message (only visible with DEBUG log level)")
    logger.warning("This is a warning message")


if __name__ == "__main__":
    main()
