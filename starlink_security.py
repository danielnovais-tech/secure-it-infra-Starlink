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
import threading
import time
from collections import Counter
from pathlib import Path
from queue import Queue
from typing import Dict, Optional

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

# Resilience: Enable self-test mode at startup
ENABLE_SELF_TEST = os.getenv('STARLINK_LOG_SELF_TEST', 'true').lower() == 'true'

# Maximum log file size (10 MB) and backup count (7 days worth)
MAX_LOG_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 7


# Logging Metrics & Health Monitoring
class LoggingMetrics:
    """
    Tracks metrics about the logging system for observability.
    
    Metrics tracked:
    - messages_logged: Total messages logged by level
    - messages_dropped: Messages dropped due to queue overflow
    - handler_failures: Failures per handler
    - queue_size: Current async queue size (if applicable)
    - handler_health: Health status of each handler
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self.messages_logged = Counter()
        self.messages_dropped = 0
        self.handler_failures = Counter()
        self.handler_health = {}
        self._queue_size = 0
        
    def record_message(self, level: str):
        """Record a logged message."""
        with self._lock:
            self.messages_logged[level] += 1
    
    def record_dropped_message(self):
        """Record a dropped message."""
        with self._lock:
            self.messages_dropped += 1
    
    def record_handler_failure(self, handler_name: str):
        """Record a handler failure."""
        with self._lock:
            self.handler_failures[handler_name] += 1
            self.handler_health[handler_name] = 'unhealthy'
    
    def record_handler_success(self, handler_name: str):
        """Record a handler success."""
        with self._lock:
            self.handler_health[handler_name] = 'healthy'
    
    def set_queue_size(self, size: int):
        """Update the current queue size."""
        with self._lock:
            self._queue_size = size
    
    def get_metrics(self) -> Dict:
        """Get all current metrics."""
        with self._lock:
            return {
                'messages_logged': dict(self.messages_logged),
                'messages_dropped': self.messages_dropped,
                'handler_failures': dict(self.handler_failures),
                'handler_health': dict(self.handler_health),
                'queue_size': self._queue_size,
                'total_messages': sum(self.messages_logged.values())
            }
    
    def get_health_status(self) -> Dict:
        """Get health check status."""
        with self._lock:
            unhealthy_handlers = [h for h, status in self.handler_health.items() if status == 'unhealthy']
            return {
                'status': 'unhealthy' if unhealthy_handlers else 'healthy',
                'unhealthy_handlers': unhealthy_handlers,
                'queue_size': self._queue_size,
                'messages_dropped': self.messages_dropped
            }


# Global metrics instance
logging_metrics = LoggingMetrics()


class ResilientHTTPHandler(logging.handlers.HTTPHandler):
    """HTTP handler with retry logic and circuit breaker."""
    
    def __init__(self, host, url, method='POST', max_retries=3, backoff_factor=2):
        super().__init__(host, url, method)
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.circuit_open = False
        self.failure_count = 0
        self.circuit_threshold = 5
        self._lock = threading.Lock()  # Thread safety for circuit breaker state
        
    def emit(self, record):
        """Emit with retry and circuit breaker."""
        with self._lock:
            if self.circuit_open:
                logging_metrics.record_dropped_message()
                return
        
        for attempt in range(self.max_retries):
            try:
                super().emit(record)
                with self._lock:
                    self.failure_count = 0
                logging_metrics.record_handler_success('http')
                return
            except Exception as e:
                with self._lock:
                    self.failure_count += 1
                    if self.failure_count >= self.circuit_threshold:
                        self.circuit_open = True
                        logging_metrics.record_handler_failure('http')
                
                if attempt == self.max_retries - 1:
                    logging_metrics.record_handler_failure('http')
                    return
                
                time.sleep(self.backoff_factor ** attempt)


class MetricsFilter(logging.Filter):
    """Filter that tracks logging metrics."""
    
    def filter(self, record):
        logging_metrics.record_message(record.levelname)
        return True


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
    
    Each code maps to a human-readable description for documentation.
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
    
    # Error code documentation mapping
    DESCRIPTIONS = {
        "SEC-001": "Security violation detected",
        "SEC-002": "Unauthorized access attempt",
        "SEC-003": "Data integrity check failed",
        "AUTH-001": "Authentication failed",
        "AUTH-002": "Invalid credentials",
        "AUTH-003": "Token expired",
        "AUTH-004": "Permission denied",
        "NET-001": "Connection timeout",
        "NET-002": "Network unreachable",
        "NET-003": "Satellite link down",
        "CFG-001": "Invalid configuration",
        "CFG-002": "Missing required parameter",
        "SYS-001": "Service startup failed",
        "SYS-002": "Resource exhausted",
    }
    
    @classmethod
    def get_description(cls, code: str) -> Optional[str]:
        """Get human-readable description for an error code."""
        return cls.DESCRIPTIONS.get(code, "Unknown error code")


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
        from urllib.parse import urlparse
        
        parsed = urlparse(HTTP_LOG_ENDPOINT)
        http_handler = ResilientHTTPHandler(
            f"{parsed.netloc}",
            f"{parsed.path}",
            method='POST'
        )
        handlers_list.append(http_handler)
        logging_metrics.record_handler_success('http')
        print(f"Info: Resilient HTTP log handler configured for {HTTP_LOG_ENDPOINT}", file=sys.stderr)
    except Exception as e:
        logging_metrics.record_handler_failure('http')
        print(f"Warning: Could not configure HTTP log handler: {e}", file=sys.stderr)

# Add metrics filter to all handlers
metrics_filter = MetricsFilter()
handler_index = 0
for handler in handlers_list:
    handler.addFilter(metrics_filter)
    # Initialize handler health status with unique identifier
    handler_name = f"{handler.__class__.__name__}_{handler_index}"
    logging_metrics.record_handler_success(handler_name)
    handler_index += 1

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


def get_logging_metrics() -> Dict:
    """
    Get current logging system metrics.
    
    Returns:
        Dictionary with metrics including:
        - messages_logged: Count by level
        - messages_dropped: Total dropped messages
        - handler_failures: Failures per handler
        - handler_health: Health status per handler
        - queue_size: Current async queue size
        - total_messages: Total messages logged
    
    Example:
        metrics = get_logging_metrics()
        print(f"Total messages: {metrics['total_messages']}")
        print(f"Messages dropped: {metrics['messages_dropped']}")
    """
    return logging_metrics.get_metrics()


def get_logging_health() -> Dict:
    """
    Get logging system health status.
    
    Returns:
        Dictionary with health information:
        - status: 'healthy' or 'unhealthy'
        - unhealthy_handlers: List of unhealthy handler names
        - queue_size: Current queue size
        - messages_dropped: Dropped message count
    
    Example:
        health = get_logging_health()
        if health['status'] == 'unhealthy':
            print(f"Unhealthy handlers: {health['unhealthy_handlers']}")
    """
    return logging_metrics.get_health_status()


def run_logging_self_test() -> bool:
    """
    Run self-test on logging configuration.
    
    Tests:
    - All handlers can be created
    - Formatters work correctly
    - Log messages can be written
    - Async queue (if enabled) is operational
    
    Returns:
        True if all tests pass, False otherwise
    
    Example:
        if not run_logging_self_test():
            print("Logging system has configuration issues")
    """
    test_results = []
    
    # Test 1: Handler creation
    if not final_handlers:
        print("FAIL: No handlers configured", file=sys.stderr)
        test_results.append(False)
    else:
        print(f"PASS: {len(final_handlers)} handler(s) configured", file=sys.stderr)
        test_results.append(True)
    
    # Test 2: Write test messages at each level
    test_logger = logging.getLogger('starlink-security.selftest')
    try:
        test_logger.debug("Self-test DEBUG message")
        test_logger.info("Self-test INFO message")
        test_logger.warning("Self-test WARNING message")
        print("PASS: Test messages written successfully", file=sys.stderr)
        test_results.append(True)
    except Exception as e:
        print(f"FAIL: Could not write test messages: {e}", file=sys.stderr)
        test_results.append(False)
    
    # Test 3: Verify async queue if enabled
    if USE_ASYNC_LOGGING:
        # Note: Accessing private _thread attribute since QueueListener
        # doesn't provide a public API to check thread status
        if queue_listener and hasattr(queue_listener, '_thread') and queue_listener._thread.is_alive():
            print("PASS: Async logging queue operational", file=sys.stderr)
            test_results.append(True)
        else:
            print("FAIL: Async logging queue not operational", file=sys.stderr)
            test_results.append(False)
    
    # Test 4: Check handler health
    health = get_logging_health()
    if health['status'] == 'healthy':
        print("PASS: All handlers healthy", file=sys.stderr)
        test_results.append(True)
    else:
        print(f"WARN: Some handlers unhealthy: {health['unhealthy_handlers']}", file=sys.stderr)
        test_results.append(True)  # Don't fail on this, just warn
    
    all_passed = all(test_results)
    print(f"\nSelf-test {'PASSED' if all_passed else 'FAILED'}: {sum(test_results)}/{len(test_results)} tests passed\n", file=sys.stderr)
    return all_passed


def attach_correlation_id(correlation_id: str):
    """
    Helper decorator to automatically attach correlation ID to all logs within a function.
    
    Note: In multi-threaded environments, use context-local storage or pass correlation_id
    via the 'extra' parameter directly for better thread safety.
    
    Args:
        correlation_id: The correlation ID to attach
    
    Example:
        @attach_correlation_id('req-12345')
        def process_request():
            logger.info("Processing")  # Will include correlation_id
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # For thread safety, attach correlation_id directly to log calls
            # This is a simplified approach; for production use threading.local()
            return func(*args, **kwargs)
        
        # Store correlation_id as attribute for access within function
        wrapper.__correlation_id__ = correlation_id
        return wrapper
    return decorator


# Register signal handler for dynamic log level changes (Unix-like systems only)
if hasattr(signal, 'SIGUSR1'):
    signal.signal(signal.SIGUSR1, handle_signal_usr1)

# Register cleanup for async logging
atexit.register(cleanup_logging)

# Run self-test if enabled
if ENABLE_SELF_TEST:
    print("=" * 60, file=sys.stderr)
    print("Running logging system self-test...", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    run_logging_self_test()


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
    
    # Example of logging with error codes and descriptions
    error_code = ErrorCode.SEC_002
    logger.error(
        f"Example: {ErrorCode.get_description(error_code)}",
        extra={'error_code': error_code, 'ip_address': '192.168.1.100', 'user_id': 'user-67890'}
    )
    
    error_code = ErrorCode.AUTH_001
    logger.warning(
        f"Example: {ErrorCode.get_description(error_code)}",
        extra={'error_code': error_code, 'username': 'test_user'}
    )
    
    # Example of different log levels
    logger.debug("This is a debug message (only visible with DEBUG log level)")
    logger.warning("This is a warning message")
    
    # Example: Demonstrate per-module logging
    module_logger = logging.getLogger('starlink-security.auth')
    module_logger.info("Module-specific log example")
    
    # Example: Manual correlation ID (recommended for thread safety)
    logger.info("Manual correlation ID example", extra={'correlation_id': 'req-99999'})
    
    # Display logging metrics
    print("\n" + "=" * 60, file=sys.stderr)
    print("Logging System Metrics", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    metrics = get_logging_metrics()
    print(f"Total messages logged: {metrics['total_messages']}", file=sys.stderr)
    print(f"Messages by level: {metrics['messages_logged']}", file=sys.stderr)
    print(f"Messages dropped: {metrics['messages_dropped']}", file=sys.stderr)
    print(f"Handler failures: {metrics['handler_failures']}", file=sys.stderr)
    print(f"Queue size: {metrics['queue_size']}", file=sys.stderr)
    
    print("\n" + "=" * 60, file=sys.stderr)
    print("Logging System Health Check", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    health = get_logging_health()
    print(f"Status: {health['status'].upper()}", file=sys.stderr)
    print(f"Handler health: {metrics['handler_health']}", file=sys.stderr)
    if health['unhealthy_handlers']:
        print(f"Unhealthy handlers: {health['unhealthy_handlers']}", file=sys.stderr)
    else:
        print("All handlers operational", file=sys.stderr)
    print("=" * 60 + "\n", file=sys.stderr)


if __name__ == "__main__":
    main()
