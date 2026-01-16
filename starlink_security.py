"""
Starlink Security Infrastructure Management
Main application module with structured logging configuration
"""

import atexit
import json
import logging
import logging.handlers
import os
import signal
import sys
from pathlib import Path
from queue import Queue

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

# Performance: Enable async logging for high-throughput scenarios
USE_ASYNC_LOGGING = os.getenv('STARLINK_ASYNC_LOGGING', 'false').lower() == 'true'

# Centralized logging: Support for remote handlers
SYSLOG_ADDRESS = os.getenv('STARLINK_SYSLOG_ADDRESS', None)  # e.g., 'localhost:514'
HTTP_LOG_ENDPOINT = os.getenv('STARLINK_HTTP_LOG_ENDPOINT', None)  # e.g., 'http://logs.example.com/ingest'

# Maximum log file size (10 MB) and backup count (7 days worth)
MAX_LOG_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 7


# Structured Error Codes for filtering and alerting
class ErrorCode:
    """
    Standardized error codes for the Starlink Security system.
    
    Format: {CATEGORY}-{NUMBER}
    - SEC: Security-related errors
    - AUTH: Authentication/Authorization errors
    - NET: Network-related errors
    - CFG: Configuration errors
    - SYS: System-level errors
    """
    # Security errors
    SEC_001 = "SEC-001"  # Security violation detected
    SEC_002 = "SEC-002"  # Unauthorized access attempt
    SEC_003 = "SEC-003"  # Data integrity check failed
    
    # Authentication errors
    AUTH_001 = "AUTH-001"  # Authentication failed
    AUTH_002 = "AUTH-002"  # Invalid credentials
    AUTH_003 = "AUTH-003"  # Token expired
    AUTH_004 = "AUTH-004"  # Permission denied
    
    # Network errors
    NET_001 = "NET-001"  # Connection timeout
    NET_002 = "NET-002"  # Network unreachable
    NET_003 = "NET-003"  # Satellite link down
    
    # Configuration errors
    CFG_001 = "CFG-001"  # Invalid configuration
    CFG_002 = "CFG-002"  # Missing required parameter
    
    # System errors
    SYS_001 = "SYS-001"  # Service startup failed
    SYS_002 = "SYS-002"  # Resource exhausted


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
        "message": "Log message text",
        "error_code": "SEC-001"  # Optional, if provided
    }
    
    Additional fields can be included via the 'extra' parameter in logging calls:
    - request_id: Request/transaction identifier
    - user_id: User identifier
    - error_code: Standardized error code (e.g., SEC-001, AUTH-005)
    - Any other custom fields passed via extra dict
    
    Exception information is automatically included when present.
    
    Example JSON outputs:
    
    Standard log:
    {"timestamp": "2026-01-16 19:29:07,668", "logger": "starlink-security", 
     "level": "INFO", "module": "auth", "line": 42, 
     "message": "User login successful", "request_id": "req-12345"}
    
    Error with code:
    {"timestamp": "2026-01-16 19:29:08,123", "logger": "starlink-security",
     "level": "ERROR", "module": "security", "line": 156,
     "message": "Unauthorized access attempt", "error_code": "SEC-002",
     "user_id": "user-67890", "ip_address": "192.168.1.100"}
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
handlers_list = []

try:
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / 'starlink_security.log',
        maxBytes=MAX_LOG_BYTES,
        backupCount=BACKUP_COUNT
    )
    handlers_list.append(file_handler)
except (OSError, IOError) as e:
    # Fallback to console-only logging if file handler fails
    print(f"Warning: Could not create log file handler: {e}", file=sys.stderr)

console_handler = logging.StreamHandler()
handlers_list.append(console_handler)

# Centralized logging: Add SysLogHandler if configured
if SYSLOG_ADDRESS:
    try:
        if ':' in SYSLOG_ADDRESS:
            host, port_str = SYSLOG_ADDRESS.rsplit(':', 1)
            try:
                port = int(port_str)
                syslog_handler = logging.handlers.SysLogHandler(address=(host, port))
            except ValueError:
                raise ValueError(f"Invalid port number: {port_str}")
        else:
            syslog_handler = logging.handlers.SysLogHandler(address=SYSLOG_ADDRESS)
        handlers_list.append(syslog_handler)
        print(f"Info: SysLog handler configured for {SYSLOG_ADDRESS}", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Could not configure SysLog handler: {e}", file=sys.stderr)

# Centralized logging: Add HTTP handler if configured
if HTTP_LOG_ENDPOINT:
    try:
        from logging.handlers import HTTPHandler
        from urllib.parse import urlparse
        
        parsed = urlparse(HTTP_LOG_ENDPOINT)
        http_handler = HTTPHandler(
            f"{parsed.netloc}",
            f"{parsed.path}",
            method='POST'
        )
        handlers_list.append(http_handler)
        print(f"Info: HTTP log handler configured for {HTTP_LOG_ENDPOINT}", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Could not configure HTTP log handler: {e}", file=sys.stderr)

# Set formatters based on configuration
if LOG_FORMAT == 'json':
    json_formatter = JSONFormatter()
    for handler in handlers_list:
        handler.setFormatter(json_formatter)
else:
    standard_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
    )
    for handler in handlers_list:
        handler.setFormatter(standard_formatter)

# Performance: Wrap handlers in async queue if enabled
# Use bounded queue to prevent unbounded memory growth
MAX_QUEUE_SIZE = 10000  # Maximum pending log records

queue_listener = None
if USE_ASYNC_LOGGING and handlers_list:
    log_queue = Queue(maxsize=MAX_QUEUE_SIZE)
    queue_handler = logging.handlers.QueueHandler(log_queue)
    queue_listener = logging.handlers.QueueListener(log_queue, *handlers_list, respect_handler_level=True)
    queue_listener.start()
    
    # Use only the queue handler for async logging
    final_handlers = [queue_handler]
    print(f"Info: Async logging enabled via QueueHandler (max queue: {MAX_QUEUE_SIZE})", file=sys.stderr)
else:
    final_handlers = handlers_list

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    handlers=final_handlers
)

logger = logging.getLogger('starlink-security')

# Security note: Ensure sensitive data is never logged
# Filter or sanitize passwords, tokens, API keys, and PII before logging


# Dynamic runtime reconfiguration support
def set_log_level(level_name):
    """
    Change log level at runtime.
    
    Args:
        level_name: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Example:
        set_log_level('DEBUG')  # Enable debug logging temporarily
    """
    level_name = level_name.upper()
    if level_name in VALID_LOG_LEVELS:
        logging.getLogger().setLevel(getattr(logging, level_name))
        logger.info(f"Log level changed to {level_name}")
        return True
    else:
        logger.warning(f"Invalid log level: {level_name}")
        return False


def handle_signal_usr1(signum, frame):
    """
    Signal handler for SIGUSR1 - toggles between INFO and DEBUG levels.
    Useful for debugging production issues without redeployment.
    
    Send signal with: kill -USR1 <pid>
    """
    current_level = logging.getLogger().level
    if current_level == logging.DEBUG:
        set_log_level('INFO')
    else:
        set_log_level('DEBUG')


def cleanup_logging():
    """Clean up async logging resources."""
    global queue_listener
    if queue_listener:
        queue_listener.stop()


# Register signal handler for dynamic log level changes (Unix-like systems only)
if hasattr(signal, 'SIGUSR1'):
    signal.signal(signal.SIGUSR1, handle_signal_usr1)

# Register cleanup for async logging
atexit.register(cleanup_logging)


def main():
    """Main entry point for the Starlink Security application."""
    logger.info("Starlink Security Infrastructure starting...")
    logger.info(f"Config directory: {CONFIG_DIR}")
    logger.info(f"Data directory: {DATA_DIR}")
    logger.info(f"Log directory: {LOG_DIR}")
    logger.info(f"Log level: {LOG_LEVEL}")
    logger.info(f"Log format: {LOG_FORMAT}")
    logger.info(f"Log rotation: {MAX_LOG_BYTES} bytes, {BACKUP_COUNT} backups")
    logger.info(f"Async logging: {USE_ASYNC_LOGGING}")
    
    # Example of logging with correlation ID
    # In production, request_id would come from request context
    extra = {'request_id': 'req-12345', 'user_id': 'user-67890'}
    logger.info("Example log with correlation metadata", extra=extra)
    
    # Example of logging with error codes
    logger.error(
        "Example: Unauthorized access attempt detected",
        extra={'error_code': ErrorCode.SEC_002, 'ip_address': '192.168.1.100', 'user_id': 'user-67890'}
    )
    
    logger.warning(
        "Example: Authentication failed",
        extra={'error_code': ErrorCode.AUTH_001, 'username': 'test_user'}
    )
    
    # Example of different log levels
    logger.debug("This is a debug message (only visible with DEBUG log level)")
    logger.warning("This is a warning message")
    
    # Example: Demonstrate per-module logging
    module_logger = logging.getLogger('starlink-security.auth')
    module_logger.info("Module-specific log example")


if __name__ == "__main__":
    main()
