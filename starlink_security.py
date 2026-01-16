"""
Starlink Security Infrastructure Management
Main application module with structured logging configuration
"""

import json
import logging
import logging.handlers
import os
import sys
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
VALID_LOG_LEVELS = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
LOG_LEVEL_RAW = os.getenv('STARLINK_LOG_LEVEL', 'INFO').upper()
LOG_LEVEL = LOG_LEVEL_RAW if LOG_LEVEL_RAW in VALID_LOG_LEVELS else 'INFO'

if LOG_LEVEL_RAW != LOG_LEVEL:
    print(f"Warning: Invalid log level '{LOG_LEVEL_RAW}', falling back to INFO", file=sys.stderr)
    
LOG_FORMAT = os.getenv('STARLINK_LOG_FORMAT', 'standard').lower()

# Maximum log file size (10 MB) and backup count (7 days worth)
MAX_LOG_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 7


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Produces JSON output with the following structure:
    {
        "timestamp": "2026-01-16 19:29:07,668",
        "logger": "logger-name",
        "level": "INFO",
        "module": "module_name",
        "line": 42,
        "message": "Log message text"
    }
    
    Additional fields can be included via the 'extra' parameter in logging calls:
    - request_id: Request/transaction identifier
    - user_id: User identifier
    - Any other custom fields passed via extra dict
    
    Exception information is automatically included when present.
    """
    
    def format(self, record):
        """
        Format log record as JSON.
        
        Args:
            record: LogRecord instance
            
        Returns:
            JSON string representation of the log record
        """
        # Standard logging attributes to exclude from extra fields
        standard_attrs = {
            'name', 'msg', 'args', 'created', 'filename', 'funcName', 'levelname',
            'levelno', 'lineno', 'module', 'msecs', 'message', 'pathname', 'process',
            'processName', 'relativeCreated', 'thread', 'threadName', 'exc_info',
            'exc_text', 'stack_info', 'getMessage', 'taskName'
        }
        
        log_data = {
            'timestamp': self.formatTime(record, self.datefmt),
            'logger': record.name,
            'level': record.levelname,
            'module': record.module,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        # Dynamically add extra fields from record
        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith('_'):
                log_data[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        try:
            return json.dumps(log_data, default=str)
        except (TypeError, ValueError) as e:
            # Fallback to string representation if JSON serialization fails
            return json.dumps({
                'timestamp': self.formatTime(record, self.datefmt),
                'logger': record.name,
                'level': 'ERROR',
                'message': f'Failed to serialize log record: {str(e)}'
            })


# Configure handlers
try:
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / 'starlink_security.log',
        maxBytes=MAX_LOG_BYTES,
        backupCount=BACKUP_COUNT
    )
except (OSError, IOError) as e:
    # Fallback to console-only logging if file handler fails
    print(f"Warning: Could not create log file handler: {e}", file=sys.stderr)
    file_handler = None

console_handler = logging.StreamHandler()

# Set formatters based on configuration
if LOG_FORMAT == 'json':
    json_formatter = JSONFormatter()
    if file_handler:
        file_handler.setFormatter(json_formatter)
    console_handler.setFormatter(json_formatter)
else:
    standard_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
    )
    if file_handler:
        file_handler.setFormatter(standard_formatter)
    console_handler.setFormatter(standard_formatter)

# Configure structured logging
handlers = [console_handler]
if file_handler:
    handlers.insert(0, file_handler)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    handlers=handlers
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
