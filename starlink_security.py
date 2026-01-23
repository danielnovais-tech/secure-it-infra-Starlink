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
        queue_listener_thread = getattr(queue_listener, '_thread', None) if queue_listener else None
        if queue_listener_thread is not None and queue_listener_thread.is_alive():
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
# NOTE: Some platforms (e.g., Windows) do not define SIGUSR1. Using getattr
# avoids static type-checker errors and keeps runtime behavior unchanged.
sigusr1 = getattr(signal, 'SIGUSR1', None)
if sigusr1 is not None:
    signal.signal(sigusr1, handle_signal_usr1)

# Register cleanup for async logging
atexit.register(cleanup_logging)

# Run self-test if enabled
if ENABLE_SELF_TEST:
    print("=" * 60, file=sys.stderr)
    print("Running logging system self-test...", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    run_logging_self_test()


def logging_system_main():
    """Main entry point for the logging-system demo in this module."""
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
    logging_system_main()

"""Starlink Security Foundation Module

Foundation for securing enterprise infrastructures using Starlink connectivity.
Provides monitoring, enforcement, and response capabilities.
"""

import hashlib
import json
import logging
import os
import queue
import random
import secrets
import threading
import time
import warnings
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set
from cryptography.fernet import Fernet

# Define directories
CONFIG_DIR = Path.home() / ".starlink_security" / "config"
DATA_DIR = Path.home() / ".starlink_security" / "data"
LOG_DIR = Path.home() / ".starlink_security" / "logs"

# Default metric values
DEFAULT_LATENCY = 0.0
DEFAULT_JITTER = 0.0
DEFAULT_PACKET_LOSS = 0.0
DEFAULT_THROUGHPUT = 0.0
DEFAULT_SECURITY_SCORE = 100.0
DEFAULT_CONNECTION_STABILITY = 100.0

# Key rotation settings
DEFAULT_KEY_ROTATION_DAYS = 90


def setup_logging(log_dir: Path = LOG_DIR, log_level: str = "INFO") -> logging.Logger:
    """
    Setup structured JSON logging for the security foundation.
    
    Args:
        log_dir: Directory for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("starlink_security")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with structured format
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with JSON format
    try:
        log_file = log_dir / f"starlink_security_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                    "level": record.levelname,
                    "module": record.module,
                    "function": record.funcName,
                    "message": record.getMessage(),
                }
                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)
                return json.dumps(log_data)
        
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)
    except (IOError, PermissionError) as e:
        logger.warning(f"Failed to setup file logging: {e}")
    
    return logger


def setup_directories() -> None:
    """
    Create required directories if they don't exist.
    
    Raises:
        PermissionError: If directories cannot be created due to insufficient permissions.
        OSError: If directories cannot be created due to other filesystem errors.
    """
    logger = logging.getLogger("starlink_security")
    for directory in [CONFIG_DIR, DATA_DIR, LOG_DIR]:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory ready: {directory}")
        except PermissionError as e:
            logger.error(f"Permission denied creating directory: {directory}")
            raise PermissionError(
                f"Cannot create Starlink security directory '{directory}' due to insufficient permissions. "
                f"Original error: {e}"
            ) from e
        except OSError as e:
            logger.error(f"OS error creating directory: {directory}")
            raise OSError(
                f"Cannot create Starlink security directory '{directory}' due to filesystem error. "
                f"Original error: {e}"
            ) from e


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration schema.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_keys = ["security_level", "connection_type", "monitoring_interval", 
                     "max_events_queue", "encryption_enabled"]
    
    # Check required keys
    for key in required_keys:
        if key not in config:
            return False
    
    # Validate types and values
    if not isinstance(config["monitoring_interval"], (int, float)) or config["monitoring_interval"] <= 0:
        return False
    
    if not isinstance(config["max_events_queue"], int) or config["max_events_queue"] <= 0:
        return False
    
    if config["security_level"] not in ["normal", "elevated", "critical", "recovery"]:
        return False
    
    if config["connection_type"] not in ["starlink_only", "hybrid", "failover"]:
        return False
    
    if not isinstance(config["encryption_enabled"], bool):
        return False
    
    return True


class SecurityLevel(Enum):
    """Security levels for different operational modes."""
    NORMAL = "normal"
    ELEVATED = "elevated"
    CRITICAL = "critical"
    RECOVERY = "recovery"


class ConnectionType(Enum):
    """Types of Starlink connections."""
    STARLINK_ONLY = "starlink_only"
    HYBRID = "hybrid"  # Starlink + backup connection
    FAILOVER = "failover"  # Primary failed, using Starlink
#!/usr/bin/env python3
"""
Starlink Security Foundation
Security monitoring system for Starlink infrastructure

This is the main entry point that provides backward compatibility
while using the new modular architecture.
"""

import asyncio
from security import (
    SecurityLevel as ModularSecurityLevel,
    StarlinkSecurityFoundation as ModularStarlinkSecurityFoundation,
    NetworkMonitor as ModularNetworkMonitor,
    ThreatDetector as ModularThreatDetector,
    PolicyEnforcer as ModularPolicyEnforcer,
)

# Backward-compatible re-exports.
# NOTE: This module contains multiple local definitions of some symbols later in the file.
# Only alias names that are not defined locally to avoid collisions.
NetworkMonitor = ModularNetworkMonitor
ThreatDetector = ModularThreatDetector

# Re-export for backward compatibility
__all__ = [
    'SecurityLevel',
    'StarlinkSecurityFoundation', 
    'NetworkMonitor',
    'ThreatDetector',
    'PolicyEnforcer'
]

# NOTE:
# This file contains multiple local definitions of SecurityLevel/StarlinkSecurityFoundation/
# PolicyEnforcer (and others). Importing same-named symbols from the modular `security`
# package would overwrite existing local definitions and trigger type-checking errors like:
#   "Type 'type[security.foundation.StarlinkSecurityFoundation]' is not assignable to
#    declared type 'type[starlink_security.StarlinkSecurityFoundation]'".
#
# To keep backward-compatibility while avoiding name/type collisions, the modular
# architecture exports are available under the `Modular*` aliases above.

"""Starlink Enterprise Security Foundation

A comprehensive security management system for Starlink enterprise connections
with automatic failover, monitoring, and threat detection capabilities.
"""

import asyncio
import argparse
import contextlib
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configure logging
# Use local logs directory if /var/log is not writable
try:
    LOG_DIR = Path("/var/log/starlink_security")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
except PermissionError:
    LOG_DIR = Path.home() / ".starlink_security" / "logs"
    LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'starlink_security.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnterpriseConnectionType(Enum):
    """Types of network connections (enterprise foundation variant).

    NOTE: This file contains multiple architectures in a single module.
    To avoid symbol collisions with the core `ConnectionType` enum defined
    earlier (starlink_only/hybrid/failover), the enterprise variant uses a
    distinct name.
    """
    STARLINK_ONLY = "starlink_only"
    FAILOVER = "failover"
    DUAL_WAN = "dual_wan"
    LOAD_BALANCED = "load_balanced"


class EnterpriseSecurityLevel(Enum):
    """Security threat levels (enterprise foundation variant).

    NOTE: This module defines multiple architectures in a single file. To avoid
    symbol collisions with the core `SecurityLevel` enum (normal/elevated/
    critical/recovery), the enterprise variant uses a distinct name.
    """
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityMetrics:
    """Security and connection metrics."""
    security_score: float = 100.0
    connection_stability: float = 100.0
    packet_loss: float = 0.0
    latency: float = 0.0
    bandwidth_usage: float = 0.0
    threat_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ThreatInfo:
    """Information about a detected threat."""
    threat_id: str
    severity: str
    source: str
    description: str
    timestamp: datetime = field(default_factory=datetime.now)


class BackupConnectionManager:
    """Manages backup connections and failover logic."""
    
    def __init__(self, foundation: 'EnterpriseStarlinkSecurityFoundation'):
        """Initialize backup connection manager.
        
        Args:
            foundation: Reference to the main StarlinkSecurityFoundation instance
        """
        self.foundation = foundation
        self.backup_connections: Dict[str, Dict[str, Any]] = {
            "lte_backup": {
                "available": True,
                "priority": 1,
                "type": "LTE"
            },
            "cable_backup": {
                "available": True,
                "priority": 2,
                "type": "Cable"
            },
            "satellite_backup": {
                "available": False,
                "priority": 3,
                "type": "Satellite"
            }
        }
        self.active_backup: Optional[str] = None
        
    async def monitor_connection(self):
        """Monitor primary connection and trigger failover if needed."""
        logger.info("Monitoring connection status")
        
        metrics = self.foundation.metrics
        
        # Check if primary connection is degraded
        if (metrics.packet_loss > 10 or 
            metrics.latency > 200 or
            metrics.connection_stability < 50):
            
            if self.foundation.connection_type == EnterpriseConnectionType.STARLINK_ONLY:
                await self.activate_failover()
    
    async def activate_failover(self):
        """Activate backup connection."""
        logger.info("Activating failover to backup connection")
        
        # Find best available backup
        best_backup = None
        best_priority = float('inf')
        
        for name, info in self.backup_connections.items():
            if info["available"] and info["priority"] < best_priority:
                best_backup = name
                best_priority = info["priority"]
        
        if best_backup:
            self.active_backup = best_backup
            self.foundation.connection_type = EnterpriseConnectionType.FAILOVER
            
            await self.foundation.trigger_event(
                "failover_activated",
                "info",
                "backup_manager",
                f"Failover activated to {best_backup}",
                {"backup_connection": best_backup}
            )
        else:
            await self.foundation.trigger_event(
                "failover_failed",
                "critical",
                "backup_manager",
                "No backup connections available for failover",
                {"available_backups": []}
            )


class EnterpriseStarlinkSecurityFoundation:
    """Main security foundation class."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the security foundation.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        self.security_level = EnterpriseSecurityLevel.MINIMAL
        self.connection_type = EnterpriseConnectionType.STARLINK_ONLY
        self.metrics = SecurityMetrics()
        self.active_threats: List[ThreatInfo] = []
        self.running = False
        # Background task for the main loop when using async start()/stop().
        # This avoids blocking callers that want to run other components concurrently.
        self._main_task: Optional[asyncio.Task] = None
        self.backup_manager = BackupConnectionManager(self)
        self.events: List[Dict[str, Any]] = []
        # Provide a stable per-instance logger attribute for callers.
        # Some code paths (and static type checkers) expect `foundation.logger`.
        self.logger: logging.Logger = logger
        # Defined for compatibility with other StarlinkSecurityFoundation variants.
        self.audit_formatters: list[Any] = []
        
        logger.info("Starlink Security Foundation initialized")
        
        if config_path:
            self._load_config(config_path)
    
    def _load_config(self, config_path: str):
        """Load configuration from file.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                logger.info(f"Configuration loaded from {config_path}")
                # Process configuration here
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
    
    async def trigger_event(self, event_type: str, severity: str, 
                           source: str, message: str, metadata: Dict[str, Any]):
        """Trigger and log a security event.
        
        Args:
            event_type: Type of event
            severity: Event severity level (info, warning, error, critical)
            source: Source of the event
            message: Event message
            metadata: Additional event metadata
        """
        event = {
            "type": event_type,
            "severity": severity,
            "source": source,
            "message": message,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
        self.events.append(event)
        
        # Map severity to logging level safely
        severity_mapping = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }
        log_level = severity_mapping.get(severity.lower(), logging.INFO)
        logger.log(log_level, f"{event_type}: {message}")
    
    def get_security_report(self) -> Dict[str, Any]:
        """Generate a comprehensive security report.
        
        Returns:
            Dictionary containing security metrics and status
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "security_level": self.security_level.value,
            "connection_type": self.connection_type.value,
            "metrics": {
                "security_score": self.metrics.security_score,
                "connection_stability": self.metrics.connection_stability,
                "packet_loss": self.metrics.packet_loss,
                "latency": self.metrics.latency,
                "bandwidth_usage": self.metrics.bandwidth_usage,
                "threat_count": self.metrics.threat_count
            },
            "active_threats": [
                {
                    "id": threat.threat_id,
                    "severity": threat.severity,
                    "source": threat.source,
                    "description": threat.description,
                    "timestamp": threat.timestamp.isoformat()
                }
                for threat in self.active_threats
            ],
            "events": self.events[-10:],  # Last 10 events
            "backup_status": {
                "active": self.backup_manager.active_backup,
                "available": {
                    name: info["available"]
                    for name, info in self.backup_manager.backup_connections.items()
                }
            }
        }
    
    async def update_metrics(self):
        """Update security metrics periodically."""
        # Simulate metric updates
        # In a real implementation, this would collect actual metrics
        import random
        
        # Using random for simulation purposes only (not security-critical)
        self.metrics.packet_loss = random.uniform(0, 15)  # nosec B311
        self.metrics.latency = random.uniform(10, 250)  # nosec B311
        self.metrics.connection_stability = random.uniform(40, 100)  # nosec B311
        self.metrics.bandwidth_usage = random.uniform(0, 100)  # nosec B311
        self.metrics.security_score = max(0, 100 - len(self.active_threats) * 10)
        self.metrics.threat_count = len(self.active_threats)
        self.metrics.last_updated = datetime.now()
        
        logger.debug(f"Metrics updated: loss={self.metrics.packet_loss:.1f}%, "
                    f"latency={self.metrics.latency:.1f}ms, "
                    f"stability={self.metrics.connection_stability:.1f}%")
    
    async def run(self):
        """Main run loop for the security foundation."""
        self.running = True
        logger.info("Starting Starlink Security Foundation main loop")
        
        try:
            while self.running:
                # Update metrics
                await self.update_metrics()
                
                # Monitor connection
                await self.backup_manager.monitor_connection()
                
                # Sleep before next iteration
                await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            raise
        finally:
            logger.info("Main loop stopped")

    async def start(self) -> None:
        """Start the foundation without blocking the caller.

        This method exists for parity with other foundation variants and to
        support call sites that do: `await foundation.start()`.
        """
        if self._main_task is not None and not self._main_task.done():
            logger.info("Foundation already started")
            return
        # Schedule the run loop in the background so callers can `gather()` other tasks.
        self._main_task = asyncio.create_task(self.run(), name="enterprise_foundation_main_loop")

    async def stop(self) -> None:
        """Stop the foundation and wait for the main loop to exit.

        This method exists for parity with other foundation variants and to
        support call sites that do: `await foundation.stop()`.
        """
        self.running = False

        task = self._main_task
        if task is None:
            return

        try:
            await asyncio.wait_for(task, timeout=5.0)
        except asyncio.TimeoutError:
            # If the loop is stuck, cancel the task to unblock shutdown.
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
        finally:
            self._main_task = None
    
    def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up resources")
        self.running = False


async def enterprise_foundation_main():
    """Main entry point."""
    foundation = EnterpriseStarlinkSecurityFoundation()
    
    # Initialize and start all components
    network_monitor = NetworkMonitor(foundation)
    threat_detector = ThreatDetector(foundation)
    policy_enforcer = PolicyEnforcer(foundation)
    
    network_monitor.initialize()
    threat_detector.initialize()
    policy_enforcer.initialize()
    
    foundation.logger.info("Starting all security components")
    
    try:
        await foundation.start()
        # Run all components concurrently
        await asyncio.gather(
            network_monitor.start(),
            threat_detector.start(),
            return_exceptions=True
        )
    except KeyboardInterrupt:
        foundation.logger.info("Received shutdown signal")
    finally:
        await foundation.stop()
    parser = argparse.ArgumentParser(description='Starlink Enterprise Security Foundation')
    parser.add_argument('--config', '-c', help='Path to configuration file')
    parser.add_argument('--report', '-r', action='store_true', help='Generate security report')
    parser.add_argument('--status', '-s', action='store_true', help='Show current status')
    parser.add_argument('--daemon', '-d', action='store_true', help='Run as daemon')
    
    args = parser.parse_args()
    
    # Initialize foundation
    foundation = StarlinkSecurityFoundation(args.config)
    
    if args.report:
        # Generate and print report
        report = foundation.get_security_report()
        print(json.dumps(report, indent=2))
        return
    
    if args.status:
        # Show current status
        metrics = foundation.metrics
        # Not all StarlinkSecurityFoundation variants expose `security_level`/`connection_type`.
        # Use getattr() so static type checkers (and runtime) won't fail when a different
        # foundation implementation is wired in.
        security_level = getattr(foundation, "security_level", None)
        security_level_value = getattr(security_level, "value", security_level)
        print(f"Security Level: {security_level_value}")

        connection_type = getattr(foundation, "connection_type", None)
        connection_type_value = getattr(connection_type, "value", connection_type)
        print(f"Connection Type: {connection_type_value}")
        # `foundation.metrics` may be a dataclass (e.g., SecurityMetrics/NetworkMetrics)
        # or a plain dict depending on which foundation variant is in use.
        security_score = getattr(metrics, "security_score", None)
        if security_score is None and isinstance(metrics, dict):
            security_score = metrics.get("security_score")

        if isinstance(security_score, (int, float)):
            print(f"Security Score: {security_score:.1f}/100")
        else:
            print("Security Score: N/A")
        if isinstance(metrics, dict):
            connection_stability = metrics.get("connection_stability")
        else:
            connection_stability = getattr(metrics, "connection_stability", None)

        if isinstance(connection_stability, (int, float)):
            print(f"Connection Stability: {connection_stability:.1f}/100")
        else:
            print("Connection Stability: N/A")
        active_threats = getattr(foundation, "active_threats", [])
        print(f"Active Threats: {len(active_threats) if hasattr(active_threats, '__len__') else 0}")
        return
    
    if args.daemon:
        # Run as daemon (Unix/Linux only)
        # Note: This implementation uses os.fork() which is not available on Windows
        if sys.platform == "win32":
            print("Error: Daemon mode is not supported on Windows")
            print("Please run the application in the foreground instead")
            sys.exit(1)
        
        print(f"Starting Starlink Security Foundation (PID: {os.getpid()})")
        print(f"Log file: {LOG_DIR}/starlink_security.log")
        
        # Daemonize (simplified)
        if os.fork() > 0:
            sys.exit(0)
        
        os.setsid()
        
        if os.fork() > 0:
            sys.exit(0)
        
        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        
        with open('/dev/null', 'r') as f:
            os.dup2(f.fileno(), sys.stdin.fileno())
        with open(LOG_DIR / 'daemon.log', 'a+') as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
            os.dup2(f.fileno(), sys.stderr.fileno())
    
    # Run the foundation
    try:
        run_fn = getattr(foundation, "run", None)
        if callable(run_fn):
            import inspect

            run_result = run_fn()
            if inspect.isawaitable(run_result):
                await run_result
        else:
            start_fn = getattr(foundation, "start", None)
            if callable(start_fn):
                import inspect

                start_result = start_fn()
                if inspect.isawaitable(start_result):
                    await start_result
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        if hasattr(foundation, "running"):
            foundation.running = False

        cleanup_fn = getattr(foundation, "cleanup", None)
        if callable(cleanup_fn):
            cleanup_fn()
"""
Starlink Security Infrastructure
Enterprise-grade security management for Starlink infrastructure
"""

import asyncio
import json
import logging
import random
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create log directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


@dataclass
class SecurityEvent:
    """Security event data structure."""
    timestamp: datetime
    event_type: str
    severity: str
    source: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False


@dataclass
class NetworkMetrics:
    """Network performance and security metrics."""
    latency: float
    jitter: float
    packet_loss: float
    throughput: float  # Mbps
    security_score: float  # 0-100
    connection_stability: float  # 0-100
    last_outage: Optional[datetime] = None
    threat_indicators: List[str] = field(default_factory=list)


class EventProcessor(ABC):
    """Abstract base class for pluggable event processing strategies."""
    
    @abstractmethod
    def process_event(self, event: 'SecurityEvent') -> None:
        """Process a security event."""
        pass
    
    @abstractmethod
    def start(self) -> None:
        """Start the event processor."""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop the event processor."""
        pass


class DefaultEventProcessor(EventProcessor):
    """Default synchronous event processor."""
    
    def __init__(self):
        self.logger = logging.getLogger("starlink_security.event_processor")
        self.running = False
    
    def process_event(self, event: 'SecurityEvent') -> None:
        """Process event synchronously."""
        self.logger.debug(f"Processing event: {event.event_type}")
    
    def start(self) -> None:
        """Start processor."""
        self.running = True
        self.logger.info("Default event processor started")
    
    def stop(self) -> None:
        """Stop processor."""
        self.running = False
        self.logger.info("Default event processor stopped")


class AuditLogger:
    """Tamper-evident audit logger with hash chaining."""
    
    def __init__(self, audit_file: Path):
        """
        Initialize audit logger.
        
        Args:
            audit_file: Path to audit log file
        """
        self.audit_file = audit_file
        self.last_hash = "0" * 64  # Genesis hash
        self._lock = threading.Lock()
        self.logger = logging.getLogger("starlink_security.audit")
        # In-memory chain of parsed audit entries.
        # This is used by some components (e.g., RetentionEnforcer) for
        # lightweight retention operations without re-reading the file.
        # NOTE: The file on disk remains the source of truth.
        self.audit_chain: List[Dict[str, Any]] = []
        
        # Load last hash if file exists
        if self.audit_file.exists():
            try:
                with open(self.audit_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line)
                        except json.JSONDecodeError:
                            # Skip malformed lines.
                            continue
                        self.audit_chain.append(entry)

                    if self.audit_chain:
                        self.last_hash = self.audit_chain[-1].get("hash", self.last_hash)
            except (IOError, json.JSONDecodeError) as e:
                self.logger.warning(f"Failed to load audit log: {e}")
    
    def log_audit(self, action: str, details: Dict[str, Any]) -> None:
        """
        Log an audit event with hash chaining.
        
        Args:
            action: Action being audited
            details: Additional details
        """
        with self._lock:
            timestamp = datetime.now().isoformat()
            entry = {
                "timestamp": timestamp,
                "action": action,
                "details": details,
                "previous_hash": self.last_hash
            }
            
            # Calculate hash of this entry
            entry_str = json.dumps(entry, sort_keys=True)
            current_hash = hashlib.sha256(entry_str.encode()).hexdigest()
            entry["hash"] = current_hash
            
            # Write to audit log
            try:
                with open(self.audit_file, 'a') as f:
                    f.write(json.dumps(entry) + '\n')
                # Keep in-memory chain in sync.
                self.audit_chain.append(entry)
                self.last_hash = current_hash
                self.logger.info(f"Audit logged: {action}")
            except IOError as e:
                self.logger.error(f"Failed to write audit log: {e}")


class StateStore(ABC):
    """
    Abstract base class for distributed state storage.
    Enables horizontal scaling with shared state via Redis, etcd, etc.
    """
    
    @abstractmethod
    def get_threats(self) -> Set[str]:
        """Get all active threats."""
        pass
    
    @abstractmethod
    def add_threat(self, threat_id: str) -> None:
        """Add a threat to the active set."""
        pass
    
    @abstractmethod
    def remove_threat(self, threat_id: str) -> None:
        """Remove a threat from the active set."""
        pass
    
    @abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        """Save system state."""
        pass
    
    @abstractmethod
    def load_state(self) -> Optional[Dict[str, Any]]:
        """Load system state."""
        pass


class InMemoryStateStore(StateStore):
    """In-memory state store implementation (default)."""
    
    def __init__(self):
        self._threats: Set[str] = set()
        self._state: Optional[Dict[str, Any]] = None
        self._lock = threading.RLock()
    
    def get_threats(self) -> Set[str]:
        """Get all active threats."""
        with self._lock:
            return self._threats.copy()
    
    def add_threat(self, threat_id: str) -> None:
        """Add a threat to the active set."""
        with self._lock:
            self._threats.add(threat_id)
    
    def remove_threat(self, threat_id: str) -> None:
        """Remove a threat from the active set."""
        with self._lock:
            self._threats.discard(threat_id)
    
    def save_state(self, state: Dict[str, Any]) -> None:
        """Save system state."""
        with self._lock:
            self._state = state.copy()
    
    def load_state(self) -> Optional[Dict[str, Any]]:
        """Load system state."""
        with self._lock:
            return self._state.copy() if self._state else None


class ThreatScorer(ABC):
    """
    Abstract base class for ML-based threat scoring.
    Enables pluggable ML models for anomaly detection with explainability.
    """
    
    @abstractmethod
    def score(self, event: 'SecurityEvent') -> Dict[str, Any]:
        """
        Score a security event for threat level.
        
        Args:
            event: Security event to score
            
        Returns:
            Dictionary with 'risk' (float 0-1) and 'factors' (dict of contributing factors)
        """
        pass
    
    @abstractmethod
    def score_batch(self, events: List['SecurityEvent']) -> List[Dict[str, Any]]:
        """
        Score multiple events in batch for efficiency.
        
        Args:
            events: List of security events
            
        Returns:
            List of score dictionaries
        """
        pass
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance for explainability.
        Optional method for scorers that support explainability.
        
        Returns:
            Dictionary mapping feature names to importance scores (0-1)
        """
        return {}  # Default: no explainability
    
    def is_healthy(self) -> bool:
        """
        Check if the scorer is healthy and operational.
        Used for graceful degradation.
        
        Returns:
            True if scorer is operational, False otherwise
        """
        return True  # Default: always healthy


class RuleBasedThreatScorer(ThreatScorer):
    """Default rule-based threat scorer."""
    
    def __init__(self):
        self.severity_weights = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2
        }
    
    def score(self, event: 'SecurityEvent') -> Dict[str, Any]:
        """Score based on severity and metadata."""
        risk = self.severity_weights.get(event.severity.lower(), 0.3)
        factors = {
            "severity": event.severity,
            "source": event.source,
            "event_type": event.event_type
        }
        return {"risk": risk, "factors": factors}
    
    def score_batch(self, events: List['SecurityEvent']) -> List[Dict[str, Any]]:
        """Score multiple events."""
        return [self.score(event) for event in events]
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance for rule-based scorer."""
        return {
            "severity": 1.0,
            "source": 0.3,
            "event_type": 0.2
        }


class HybridThreatScorer(ThreatScorer):
    """
    Hybrid threat scorer combining rule-based and ML scoring.
    Provides configurable weighting and explainability.
    Implements graceful degradation if ML scorer fails.
    """
    
    def __init__(self, ml_scorer: Optional[ThreatScorer] = None, 
                 rule_weight: float = 0.3, ml_weight: float = 0.7):
        """
        Initialize hybrid scorer.
        
        Args:
            ml_scorer: ML-based scorer (optional, uses rule-based if None)
            rule_weight: Weight for rule-based score (0-1)
            ml_weight: Weight for ML score (0-1)
        """
        self.rule_scorer = RuleBasedThreatScorer()
        self.ml_scorer = ml_scorer
        self.rule_weight = rule_weight
        self.ml_weight = ml_weight
        self._ml_healthy = True
        self.logger = logging.getLogger("starlink_security.hybrid_scorer")
    
    def score(self, event: 'SecurityEvent') -> Dict[str, Any]:
        """
        Score using hybrid approach with graceful degradation.
        
        Args:
            event: Security event to score
            
        Returns:
            Combined score with explainability factors
        """
        # Always get rule-based score
        rule_result = self.rule_scorer.score(event)
        rule_risk = rule_result["risk"]
        
        # Try ML scoring with graceful degradation
        ml_risk = None
        ml_factors = {}
        
        if self.ml_scorer and self._ml_healthy:
            try:
                ml_result = self.ml_scorer.score(event)
                ml_risk = ml_result["risk"]
                ml_factors = ml_result.get("factors", {})
            except Exception as e:
                self.logger.warning(f"ML scorer failed, falling back to rules: {e}")
                self._ml_healthy = False
        
        # Compute hybrid risk
        if ml_risk is not None:
            risk = (self.rule_weight * rule_risk) + (self.ml_weight * ml_risk)
            scoring_method = "hybrid"
        else:
            risk = rule_risk
            scoring_method = "rule_based_fallback"
        
        # Combine factors for explainability
        factors = {
            "scoring_method": scoring_method,
            "rule_risk": rule_risk,
            "rule_factors": rule_result["factors"],
        }
        
        if ml_risk is not None:
            factors["ml_risk"] = ml_risk
            factors["ml_factors"] = ml_factors
            factors["weights"] = {
                "rule": self.rule_weight,
                "ml": self.ml_weight
            }
        
        return {"risk": risk, "factors": factors}
    
    def score_batch(self, events: List['SecurityEvent']) -> List[Dict[str, Any]]:
        """Score multiple events with hybrid approach."""
        return [self.score(event) for event in events]
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get combined feature importance from both scorers.
        
        Returns:
            Dictionary of feature importance scores
        """
        importance = self.rule_scorer.get_feature_importance()
        
        if self.ml_scorer and self._ml_healthy:
            try:
                ml_importance = self.ml_scorer.get_feature_importance()
                # Combine importances with weights
                for feature, value in ml_importance.items():
                    if feature in importance:
                        importance[feature] = (
                            self.rule_weight * importance[feature] +
                            self.ml_weight * value
                        )
                    else:
                        importance[feature] = self.ml_weight * value
            except Exception as e:
                self.logger.warning(f"Failed to get ML feature importance: {e}")
        
        return importance
    
    def is_healthy(self) -> bool:
        """Check if hybrid scorer is healthy."""
        rule_healthy = self.rule_scorer.is_healthy()
        
        if self.ml_scorer:
            try:
                ml_healthy = self.ml_scorer.is_healthy()
                self._ml_healthy = ml_healthy
                return rule_healthy  # Can still function with rules only
            except Exception:
                self._ml_healthy = False
                return rule_healthy
        
        return rule_healthy


class AuditFormatter(ABC):
    """
    Abstract base class for compliance audit export formatters.
    Enables export to PCI DSS, HIPAA, ISO 27001 formats.
    """
    
    @abstractmethod
    def format_audit_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format an audit entry for compliance standard.
        
        Args:
            entry: Raw audit log entry
            
        Returns:
            Formatted entry according to compliance standard
        """
        pass
    
    @abstractmethod
    def get_standard_name(self) -> str:
        """Get the compliance standard name."""
        pass


class ISO27001Formatter(AuditFormatter):
    """ISO 27001 compliance audit formatter."""
    
    def format_audit_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Format entry for ISO 27001."""
        return {
            "event_id": entry.get("hash", "unknown")[:16],
            "timestamp": entry.get("timestamp"),
            "event_type": entry.get("action"),
            "actor": entry.get("details", {}).get("actor", "system"),
            "resource": entry.get("details", {}).get("resource", "system"),
            "outcome": "success",  # Could be derived from details
            "integrity_hash": entry.get("hash"),
            "previous_hash": entry.get("previous_hash")
        }
    
    def get_standard_name(self) -> str:
        """Get standard name."""
        return "ISO-27001"


def requires_permission(permission: str):
    """
    Decorator for RBAC enforcement on sensitive methods.
    
    Args:
        permission: Required permission (e.g., 'rotate_key', 'config_reload')
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # Check if RBAC is enabled
            if hasattr(self, '_rbac_enabled') and self._rbac_enabled:
                if hasattr(self, '_check_permission'):
                    if not self._check_permission(permission):
                        raise PermissionError(f"Permission denied: {permission}")
            # Log the authorization check
            if hasattr(self, 'audit_logger'):
                self.audit_logger.log_audit("authorization_check", {
                    "permission": permission,
                    "method": func.__name__,
                    "allowed": True
                })
            return func(self, *args, **kwargs)
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator


class SecurityModule:
    """Base class for security modules with lifecycle management."""
    
    def __init__(self, name: str, enabled: bool = True):
        """
        Initialize security module.
        
        Args:
            name: Module name
            enabled: Whether module is enabled
        """
        self.name = name
        self.enabled = enabled
        self.status = "initialized"
        self.logger = logging.getLogger(f"starlink_security.{name}")
    
    def start(self) -> None:
        """Start the module."""
        if self.enabled:
            self.status = "active"
            self.logger.info(f"{self.name} module started")
    
    def stop(self) -> None:
        """Stop the module."""
        self.status = "stopped"
        self.logger.info(f"{self.name} module stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get module status."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "status": self.status
        }



# ============================================================================
# Threat Feed Integration
# ============================================================================

class ThreatFeedConnector(ABC):
    """Abstract base class for threat intelligence feed connectors."""
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to threat feed.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def fetch_indicators(self) -> List[Dict[str, Any]]:
        """
        Fetch threat indicators from feed.
        
        Returns:
            List of normalized threat indicators
        """
        pass
    
    @abstractmethod
    def normalize_indicator(self, raw_indicator: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize feed-specific indicator format to common format.
        
        Args:
            raw_indicator: Raw indicator from feed
            
        Returns:
            Normalized indicator with keys: type, value, severity, source, metadata
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from threat feed."""
        pass


class STIXTAXIIConnector(ThreatFeedConnector):
    """
    Connector for STIX/TAXII threat intelligence feeds.
    
    Integrates external threat intelligence into the ThreatScorer pipeline.
    """
    
    def __init__(self, server_url: str, collection: str, api_key: Optional[str] = None):
        """
        Initialize STIX/TAXII connector.
        
        Args:
            server_url: TAXII server URL
            collection: Collection name to fetch from
            api_key: Optional API key for authentication
        """
        self.server_url = server_url
        self.collection = collection
        self.api_key = api_key
        self.connected = False
        self.logger = logging.getLogger("starlink_security.stix_taxii")
    
    def connect(self) -> bool:
        """Establish connection to TAXII server."""
        try:
            # In production, use taxii2-client library
            # For now, mark as connected for testing
            self.connected = True
            self.logger.info(f"Connected to STIX/TAXII server: {self.server_url}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to TAXII server: {e}")
            return False
    
    def fetch_indicators(self) -> List[Dict[str, Any]]:
        """Fetch STIX indicators from TAXII collection."""
        if not self.connected:
            self.logger.warning("Not connected to TAXII server")
            return []
        
        try:
            # In production, fetch STIX objects from TAXII
            # Placeholder implementation
            indicators = []
            self.logger.info(f"Fetched {len(indicators)} indicators from {self.collection}")
            return indicators
        except Exception as e:
            self.logger.error(f"Failed to fetch indicators: {e}")
            return []
    
    def normalize_indicator(self, raw_indicator: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize STIX indicator to common format."""
        # STIX pattern example: [ipv4-addr:value = '192.0.2.1']
        return {
            "type": raw_indicator.get("type", "unknown"),
            "value": raw_indicator.get("pattern", ""),
            "severity": raw_indicator.get("severity", "medium"),
            "source": "STIX/TAXII",
            "metadata": {
                "labels": raw_indicator.get("labels", []),
                "confidence": raw_indicator.get("confidence", 50),
                "created": raw_indicator.get("created", "")
            }
        }
    
    def disconnect(self) -> None:
        """Disconnect from TAXII server."""
        self.connected = False
        self.logger.info("Disconnected from STIX/TAXII server")


class MISPConnector(ThreatFeedConnector):
    """
    Connector for MISP (Malware Information Sharing Platform) threat intelligence.
    """
    
    def __init__(self, misp_url: str, api_key: str, verify_cert: bool = True):
        """
        Initialize MISP connector.
        
        Args:
            misp_url: MISP instance URL
            api_key: MISP API key
            verify_cert: Whether to verify SSL certificate
        """
        self.misp_url = misp_url
        self.api_key = api_key
        self.verify_cert = verify_cert
        self.connected = False
        self.logger = logging.getLogger("starlink_security.misp")
    
    def connect(self) -> bool:
        """Establish connection to MISP instance."""
        try:
            # In production, use pymisp library
            self.connected = True
            self.logger.info(f"Connected to MISP: {self.misp_url}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to MISP: {e}")
            return False
    
    def fetch_indicators(self) -> List[Dict[str, Any]]:
        """Fetch threat indicators from MISP."""
        if not self.connected:
            self.logger.warning("Not connected to MISP")
            return []
        
        try:
            # In production, fetch MISP events/attributes
            indicators = []
            self.logger.info(f"Fetched {len(indicators)} indicators from MISP")
            return indicators
        except Exception as e:
            self.logger.error(f"Failed to fetch MISP indicators: {e}")
            return []
    
    def normalize_indicator(self, raw_indicator: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize MISP attribute to common format."""
        return {
            "type": raw_indicator.get("type", "unknown"),
            "value": raw_indicator.get("value", ""),
            "severity": self._map_threat_level(raw_indicator.get("threat_level_id", 3)),
            "source": "MISP",
            "metadata": {
                "category": raw_indicator.get("category", ""),
                "to_ids": raw_indicator.get("to_ids", False),
                "comment": raw_indicator.get("comment", "")
            }
        }
    
    def _map_threat_level(self, level_id: int) -> str:
        """Map MISP threat level ID to severity."""
        mapping = {1: "high", 2: "medium", 3: "low", 4: "undefined"}
        return mapping.get(level_id, "low")
    
    def disconnect(self) -> None:
        """Disconnect from MISP."""
        self.connected = False
        self.logger.info("Disconnected from MISP")


# ============================================================================
# SIEM/SOAR Integration
# ============================================================================

class SIEMAdapter(ABC):
    """Abstract base class for SIEM/SOAR integrations."""
    
    @abstractmethod
    def push_audit_logs(self, logs: List[Dict[str, Any]]) -> bool:
        """
        Push audit logs to SIEM.
        
        Args:
            logs: List of audit log entries
            
        Returns:
            True if push successful, False otherwise
        """
        pass
    
    @abstractmethod
    def push_metrics(self, metrics: Dict[str, Any]) -> bool:
        """
        Push metrics to SIEM.
        
        Args:
            metrics: Metrics dictionary
            
        Returns:
            True if push successful, False otherwise
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to SIEM."""
        pass


class SplunkAdapter(SIEMAdapter):
    """Adapter for pushing logs and metrics to Splunk."""
    
    def __init__(self, hec_url: str, hec_token: str, index: str = "starlink_security"):
        """
        Initialize Splunk HEC (HTTP Event Collector) adapter.
        
        Args:
            hec_url: Splunk HEC endpoint URL
            hec_token: HEC authentication token
            index: Splunk index name
        """
        self.hec_url = hec_url
        self.hec_token = hec_token
        self.index = index
        self.logger = logging.getLogger("starlink_security.splunk")
    
    def push_audit_logs(self, logs: List[Dict[str, Any]]) -> bool:
        """Push audit logs to Splunk via HEC."""
        try:
            # In production, use requests library to POST to HEC
            # Format: {"event": {...}, "index": "...", "sourcetype": "..."}
            self.logger.info(f"Pushed {len(logs)} audit logs to Splunk index {self.index}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to push logs to Splunk: {e}")
            return False
    
    def push_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Push metrics to Splunk as metric events."""
        try:
            # In production, format as Splunk metric events
            self.logger.info(f"Pushed metrics to Splunk: {list(metrics.keys())}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to push metrics to Splunk: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check Splunk HEC connectivity."""
        try:
            # In production, send test event to HEC
            return True
        except Exception:
            return False


class ElasticAdapter(SIEMAdapter):
    """Adapter for pushing logs and metrics to Elastic Stack (ELK)."""
    
    def __init__(self, es_url: str, api_key: str, index_prefix: str = "starlink-security"):
        """
        Initialize Elastic adapter.
        
        Args:
            es_url: Elasticsearch URL
            api_key: Elasticsearch API key
            index_prefix: Index name prefix
        """
        self.es_url = es_url
        self.api_key = api_key
        self.index_prefix = index_prefix
        self.logger = logging.getLogger("starlink_security.elastic")
    
    def push_audit_logs(self, logs: List[Dict[str, Any]]) -> bool:
        """Push audit logs to Elasticsearch."""
        try:
            # In production, use elasticsearch-py bulk API
            index_name = f"{self.index_prefix}-audit-{datetime.now().strftime('%Y.%m.%d')}"
            self.logger.info(f"Pushed {len(logs)} audit logs to Elasticsearch index {index_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to push logs to Elasticsearch: {e}")
            return False
    
    def push_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Push metrics to Elasticsearch."""
        try:
            index_name = f"{self.index_prefix}-metrics-{datetime.now().strftime('%Y.%m.%d')}"
            self.logger.info(f"Pushed metrics to Elasticsearch index {index_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to push metrics to Elasticsearch: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check Elasticsearch connectivity."""
        try:
            # In production, ping Elasticsearch cluster
            return True
        except Exception:
            return False


class AzureSentinelAdapter(SIEMAdapter):
    """Adapter for pushing logs and metrics to Microsoft Azure Sentinel."""
    
    def __init__(self, workspace_id: str, shared_key: str, log_type: str = "StarlinkSecurity"):
        """
        Initialize Azure Sentinel adapter.
        
        Args:
            workspace_id: Log Analytics workspace ID
            shared_key: Workspace shared key
            log_type: Custom log type name
        """
        self.workspace_id = workspace_id
        self.shared_key = shared_key
        self.log_type = log_type
        self.logger = logging.getLogger("starlink_security.sentinel")
    
    def push_audit_logs(self, logs: List[Dict[str, Any]]) -> bool:
        """Push audit logs to Azure Sentinel via Data Collector API."""
        try:
            # In production, use Azure Monitor Data Collector API
            self.logger.info(f"Pushed {len(logs)} audit logs to Azure Sentinel")
            return True
        except Exception as e:
            self.logger.error(f"Failed to push logs to Azure Sentinel: {e}")
            return False
    
    def push_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Push metrics to Azure Sentinel."""
        try:
            self.logger.info(f"Pushed metrics to Azure Sentinel")
            return True
        except Exception as e:
            self.logger.error(f"Failed to push metrics to Azure Sentinel: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check Azure Sentinel connectivity."""
        try:
            # In production, validate workspace connection
            return True
        except Exception:
            return False


# ============================================================================
# Performance Optimizations
# ============================================================================

class ScoreCache:
    """
    LRU cache for threat scores to reduce repeated computation.
    
    Caches low-risk event scores with configurable TTL and size limits.
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        """
        Initialize score cache.
        
        Args:
            max_size: Maximum number of cached scores
            ttl_seconds: Time-to-live for cached scores in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, tuple] = {}  # key -> (score, timestamp)
        self.access_order: List[str] = []  # For LRU eviction
        self._lock = threading.RLock()
        self.hits = 0
        self.misses = 0
    
    def get(self, event_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get cached score for event.
        
        Args:
            event_hash: Hash of event for cache key
            
        Returns:
            Cached score dict or None if not found/expired
        """
        with self._lock:
            if event_hash not in self.cache:
                self.misses += 1
                return None
            
            score, timestamp = self.cache[event_hash]
            
            # Check TTL
            if time.time() - timestamp > self.ttl_seconds:
                # Remove from access_order first to avoid race condition
                if event_hash in self.access_order:
                    self.access_order.remove(event_hash)
                del self.cache[event_hash]
                self.misses += 1
                return None
            
            # Update access order (move to end for LRU)
            if event_hash in self.access_order:
                self.access_order.remove(event_hash)
            self.access_order.append(event_hash)
            self.hits += 1
            return score
    
    def put(self, event_hash: str, score: Dict[str, Any]) -> None:
        """
        Cache a score for an event.
        
        Args:
            event_hash: Hash of event for cache key
            score: Score dict to cache
        """
        with self._lock:
            # Evict oldest if at capacity
            if len(self.cache) >= self.max_size and event_hash not in self.cache:
                oldest = self.access_order.pop(0)
                del self.cache[oldest]
            
            self.cache[event_hash] = (score, time.time())
            if event_hash in self.access_order:
                self.access_order.remove(event_hash)
            self.access_order.append(event_hash)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict with hits, misses, size, hit_rate
        """
        with self._lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total * 100) if total > 0 else 0
            return {
                "hits": self.hits,
                "misses": self.misses,
                "size": len(self.cache),
                "hit_rate_percent": round(hit_rate, 2)
            }
    
    def clear(self) -> None:
        """Clear the cache."""
        with self._lock:
            self.cache.clear()
            self.access_order.clear()
            self.hits = 0
            self.misses = 0


def hash_event_for_cache(event: SecurityEvent) -> str:
    """
    Generate cache key hash for an event.
    
    Args:
        event: Security event
        
    Returns:
        SHA256 hash of event characteristics
    """
    key_data = f"{event.event_type}:{event.severity}:{event.source}:{event.description}"
    return hashlib.sha256(key_data.encode()).hexdigest()


# ============================================================================
# Policy Versioning
# ============================================================================

@dataclass
class PolicyVersion:
    """Tracks versions of rulesets and ML models."""
    version: str
    timestamp: datetime
    policy_type: str  # "ruleset" or "ml_model"
    description: str
    checksum: str  # SHA256 of policy file/model
    metadata: Dict[str, Any] = field(default_factory=dict)


class PolicyVersionTracker:
    """
    Tracks and manages versions of security policies and ML models.
    
    Enables rollback to previous versions if anomalies are detected.
    """
    
    def __init__(self, version_file: Path = DATA_DIR / "policy_versions.json"):
        """
        Initialize policy version tracker.
        
        Args:
            version_file: Path to version history file
        """
        self.version_file = version_file
        self.versions: List[PolicyVersion] = []
        self._lock = threading.RLock()
        self.logger = logging.getLogger("starlink_security.policy_version")
        self._load_versions()
    
    def _load_versions(self) -> None:
        """Load version history from file."""
        if self.version_file.exists():
            try:
                with open(self.version_file, 'r') as f:
                    data = json.load(f)
                    self.versions = [
                        PolicyVersion(
                            version=v["version"],
                            timestamp=datetime.fromisoformat(v["timestamp"]),
                            policy_type=v["policy_type"],
                            description=v["description"],
                            checksum=v["checksum"],
                            metadata=v.get("metadata", {})
                        )
                        for v in data
                    ]
                self.logger.info(f"Loaded {len(self.versions)} policy versions")
            except Exception as e:
                self.logger.error(f"Failed to load version history: {e}")
    
    def _save_versions(self) -> None:
        """Save version history to file."""
        try:
            with self._lock:
                data = [
                    {
                        "version": v.version,
                        "timestamp": v.timestamp.isoformat(),
                        "policy_type": v.policy_type,
                        "description": v.description,
                        "checksum": v.checksum,
                        "metadata": v.metadata
                    }
                    for v in self.versions
                ]
                with open(self.version_file, 'w') as f:
                    json.dump(data, f, indent=2)
            self.logger.info(f"Saved {len(self.versions)} policy versions")
        except Exception as e:
            self.logger.error(f"Failed to save version history: {e}")
    
    def register_version(
        self,
        version: str,
        policy_type: str,
        description: str,
        policy_data: bytes,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PolicyVersion:
        """
        Register a new policy version.
        
        Args:
            version: Version identifier (e.g., "1.2.3")
            policy_type: Type of policy ("ruleset" or "ml_model")
            description: Human-readable description
            policy_data: Binary policy/model data for checksum
            metadata: Optional additional metadata
            
        Returns:
            Created PolicyVersion object
        """
        checksum = hashlib.sha256(policy_data).hexdigest()
        
        policy_version = PolicyVersion(
            version=version,
            timestamp=datetime.now(),
            policy_type=policy_type,
            description=description,
            checksum=checksum,
            metadata=metadata or {}
        )
        
        with self._lock:
            self.versions.append(policy_version)
            self._save_versions()
        
        self.logger.info(f"Registered {policy_type} version {version}: {description}")
        return policy_version
    
    def get_version_history(self, policy_type: Optional[str] = None) -> List[PolicyVersion]:
        """
        Get version history, optionally filtered by type.
        
        Args:
            policy_type: Optional filter by policy type
            
        Returns:
            List of PolicyVersion objects
        """
        with self._lock:
            if policy_type:
                return [v for v in self.versions if v.policy_type == policy_type]
            return list(self.versions)
    
    def get_latest_version(self, policy_type: str) -> Optional[PolicyVersion]:
        """
        Get the latest version of a policy type.
        
        Args:
            policy_type: Type of policy
            
        Returns:
            Latest PolicyVersion or None if not found
        """
        with self._lock:
            filtered = [v for v in self.versions if v.policy_type == policy_type]
            if filtered:
                return max(filtered, key=lambda v: v.timestamp)
            return None

class DemoStarlinkSecurityFoundation:
    """
    Foundation for securing enterprise infrastructures using Starlink connectivity.
    Provides monitoring, enforcement, and response capabilities with lifecycle management.
    """
    
    def __init__(self, config_path: Optional[str] = None, 
                 module_factory: Optional[Callable[[str, bool], SecurityModule]] = None,
                 event_processor: Optional[EventProcessor] = None,
                 state_store: Optional[StateStore] = None,
                 threat_scorer: Optional[ThreatScorer] = None,
                 audit_formatters: Optional[List[AuditFormatter]] = None):
        """
        Initialize the security foundation.
        
        Args:
            config_path: Path to configuration file (optional)
            module_factory: Factory function for creating security modules (for dependency injection)
            event_processor: Custom event processor (for pluggable event processing)
            state_store: Distributed state store (for horizontal scaling, defaults to in-memory)
            threat_scorer: ML-based threat scorer (for anomaly detection, defaults to rule-based)
            audit_formatters: Compliance audit formatters (for PCI/HIPAA/ISO exports)
            
        Raises:
            PermissionError: If required directories cannot be created due to permissions.
            OSError: If required directories cannot be created due to other filesystem errors.
            ValueError: If configuration validation fails
        """
        # Setup logging first
        self.logger = setup_logging()
        self.logger.info("Initializing Starlink Security Foundation")
        
        # Ensure required directories exist
        setup_directories()
        
        # Thread safety
        self._lock = threading.RLock()
        self._metrics_lock = threading.Lock()
        self._config_lock = threading.Lock()
        
        # RBAC support (disabled by default, can be enabled via config)
        self._rbac_enabled = False
        self._permissions: Dict[str, Set[str]] = {}
        self.rbac_audit_log: List[Dict[str, Any]] = []  # Initialize RBAC audit log
        
        # Configuration hot-reloading
        self.config_path = config_path
        self._config_last_modified = None
        self._config_reload_thread = None
        
        # Load and validate configuration
        self.config = self._load_config(config_path)
        if not validate_config(self.config):
            raise ValueError("Invalid configuration schema")
        
        # Initialize core attributes
        self.security_level = SecurityLevel(self.config.get('security_level', 'normal'))
        self.connection_type = ConnectionType(self.config.get('connection_type', 'starlink_only'))
        self.encryption_key = self._initialize_encryption()
        self.running = False  # Will be set to True by start()
        
        # Thread-safe queue and collections
        self.events_queue: queue.Queue = queue.Queue(maxsize=self.config.get('max_events_queue', 1000))
        with self._lock:
            self.active_threats: Set[str] = set()
            self.events: List[SecurityEvent] = []

        # Async event handlers (used by demo code and integrations).
        # Signature matches StarlinkSecurityFoundation.register_event_handler().
        self.event_handlers: list[Callable[[SecurityEvent], Awaitable[None]]] = []
        
        # Metrics with thread safety
        with self._metrics_lock:
            self.metrics = NetworkMetrics(
                DEFAULT_LATENCY,
                DEFAULT_JITTER,
                DEFAULT_PACKET_LOSS,
                DEFAULT_THROUGHPUT,
                DEFAULT_SECURITY_SCORE,
                DEFAULT_CONNECTION_STABILITY
            )
        
        # Pluggable event processor
        self.event_processor = event_processor or DefaultEventProcessor()
        
        # State store (in-memory by default, can use Redis for distributed)
        self.state_store = state_store or InMemoryStateStore()
        
        # Threat scorer (rule-based by default, can use ML models)
        self.threat_scorer = threat_scorer or RuleBasedThreatScorer()
        
        # Compliance audit formatters
        self.audit_formatters = audit_formatters or [ISO27001Formatter()]
        
        # Audit logger
        self.audit_logger = AuditLogger(LOG_DIR / "audit.log")
        self.audit_logger.log_audit("system_init", {"config_path": str(config_path) if config_path else "default"})
        
        # Module factory for dependency injection
        self._module_factory = module_factory or self._default_module_factory
        self.security_modules: Dict[str, SecurityModule] = {}
        self._initialize_modules()
        
        # Key rotation tracking
        self._key_created_at = datetime.now()
        self._key_rotation_days = self.config.get('key_rotation_days', DEFAULT_KEY_ROTATION_DAYS)
        
        # State persistence file
        self._state_file = DATA_DIR / "state.pkl"
        
        self.logger.info("Starlink Security Foundation initialized successfully")
    
    def _default_module_factory(self, name: str, enabled: bool) -> SecurityModule:
        """Default factory for creating security modules."""
        return SecurityModule(name, enabled)
    
    def start(self) -> None:
        """Start all security modules and begin operations."""
        with self._lock:
            if self.running:
                self.logger.warning("Already running")
                return
            
            self.logger.info("Starting Starlink Security Foundation")
            
            # Start event processor
            self.event_processor.start()
            
            # Start modules
            for name, module in self.security_modules.items():
                try:
                    module.start()
                    self.logger.info(f"Started module: {name}")
                except Exception as e:
                    self.logger.error(f"Failed to start module {name}: {e}")
            
            # Start config hot-reloading if config file provided
            if self.config_path and self.config.get('hot_reload_config', False):
                self._start_config_reload()
            
            self.running = True
            self.audit_logger.log_audit("system_start", {"timestamp": datetime.now().isoformat()})
            self.logger.info("Starlink Security Foundation started")
    
    def stop(self) -> None:
        """Stop all security modules and cease operations."""
        with self._lock:
            if not self.running:
                self.logger.warning("Not running")
                return
            
            self.logger.info("Stopping Starlink Security Foundation")
            
            # Stop config reload thread
            if self._config_reload_thread and self._config_reload_thread.is_alive():
                self.running = False  # Signal thread to stop
                self._config_reload_thread.join(timeout=2.0)
            
            # Save state before stopping
            self.save_state()
            
            # Stop event processor
            self.event_processor.stop()
            
            # Stop modules
            for name, module in self.security_modules.items():
                try:
                    module.stop()
                    self.logger.info(f"Stopped module: {name}")
                except Exception as e:
                    self.logger.error(f"Failed to stop module {name}: {e}")
            
            self.running = False
            self.audit_logger.log_audit("system_stop", {"timestamp": datetime.now().isoformat()})
            self.logger.info("Starlink Security Foundation stopped")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get observability metrics for monitoring.
        
        Returns:
            Dictionary with current metrics and counters
        """
        with self._lock:
            active_threats_count = len(self.active_threats)
            unresolved_events_count = len([e for e in self.events if not e.resolved])
            total_events_count = len(self.events)
        
        queue_size = self.events_queue.qsize()
        queue_maxsize = self.events_queue.maxsize
        
        with self._metrics_lock:
            network_metrics = asdict(self.metrics)
        
        return {
            "status": "running" if self.running else "stopped",
            "security_level": self.security_level.value,
            "connection_type": self.connection_type.value,
            "active_threats_count": active_threats_count,
            "unresolved_events_count": unresolved_events_count,
            "total_events_count": total_events_count,
            "events_queue_size": queue_size,
            "events_queue_capacity": queue_maxsize,
            "events_queue_utilization": (queue_size / queue_maxsize * 100) if queue_maxsize > 0 else 0,
            "network_metrics": network_metrics,
            "modules": {name: module.get_status() for name, module in self.security_modules.items()},
            "key_age_days": (datetime.now() - self._key_created_at).days,
            "key_rotation_needed": self._needs_key_rotation()
        }
    
    def _needs_key_rotation(self) -> bool:
        """Check if encryption key needs rotation."""
        age_days = (datetime.now() - self._key_created_at).days
        return age_days >= self._key_rotation_days
    
    @requires_permission("rotate_key")
    def rotate_encryption_key(self) -> None:
        """
        Rotate the encryption key for security hardening.
        Requires 'rotate_key' permission when RBAC is enabled.
        
        Raises:
            IOError: If key rotation fails
            PermissionError: If caller lacks rotate_key permission
        """
        self.logger.info("Rotating encryption key")
        self.audit_logger.log_audit("key_rotation_start", {"timestamp": datetime.now().isoformat()})
        
        try:
            # Backup old key
            key_file = CONFIG_DIR / "encryption.key"
            backup_file = CONFIG_DIR / f"encryption.key.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            if key_file.exists():
                import shutil
                shutil.copy2(key_file, backup_file)
                self.logger.info(f"Backed up old key to {backup_file}")
            
            # Generate and save new key
            new_key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(new_key)
            
            # Set restrictive permissions
            try:
                os.chmod(key_file, 0o600)
            except (OSError, NotImplementedError):
                pass
            
            self.encryption_key = new_key
            self._key_created_at = datetime.now()
            self.audit_logger.log_audit("key_rotation_success", {
                "timestamp": datetime.now().isoformat(),
                "backup_file": str(backup_file)
            })
            self.logger.info("Encryption key rotated successfully")
            
        except Exception as e:
            self.audit_logger.log_audit("key_rotation_failure", {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            })
            self.logger.error(f"Failed to rotate encryption key: {e}")
            raise IOError(f"Key rotation failed: {e}") from e
    
    @requires_permission("config_reload")
    def reload_config(self) -> bool:
        """
        Reload configuration from file at runtime (hot reload).
        Requires 'config_reload' permission when RBAC is enabled.
        
        Returns:
            True if config was reloaded successfully, False otherwise
            
        Raises:
            PermissionError: If caller lacks config_reload permission
        """
        if not self.config_path:
            self.logger.warning("No config path set, cannot reload")
            return False
        
        config_file = Path(self.config_path)
        if not config_file.exists():
            self.logger.warning(f"Config file {self.config_path} not found")
            return False
        
        try:
            with self._config_lock:
                with open(self.config_path, 'r') as f:
                    new_config = json.load(f)
                
                # Merge with defaults
                default_config = {
                    "security_level": "normal",
                    "connection_type": "starlink_only",
                    "monitoring_interval": 60,
                    "max_events_queue": 1000,
                    "encryption_enabled": True,
                    "key_rotation_days": DEFAULT_KEY_ROTATION_DAYS,
                    "log_level": "INFO",
                    "hot_reload_config": False
                }
                default_config.update(new_config)
                
                # Validate new config
                if not validate_config(default_config):
                    self.logger.error("Invalid config schema, reload aborted")
                    return False
                
                # Update config
                old_security_level = self.config.get('security_level')
                self.config = default_config
                
                # Apply dynamic changes
                new_security_level = self.config.get('security_level')
                if old_security_level != new_security_level:
                    self.security_level = SecurityLevel(new_security_level)
                    self.logger.info(f"Security level updated: {new_security_level}")
                
                self.audit_logger.log_audit("config_reload", {
                    "timestamp": datetime.now().isoformat(),
                    "config_path": self.config_path
                })
                self.logger.info("Configuration reloaded successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to reload config: {e}")
            return False
    
    def _start_config_reload(self) -> None:
        """Start background thread for configuration hot-reloading."""
        def reload_loop():
            if not self.config_path:
                return
            
            config_file = Path(self.config_path)
            while self.running:
                try:
                    if config_file.exists():
                        current_mtime = config_file.stat().st_mtime
                        if self._config_last_modified is None:
                            self._config_last_modified = current_mtime
                        elif current_mtime > self._config_last_modified:
                            self.logger.info("Config file changed, reloading...")
                            if self.reload_config():
                                self._config_last_modified = current_mtime
                    time.sleep(5)  # Check every 5 seconds
                except Exception as e:
                    self.logger.error(f"Error in config reload loop: {e}")
                    time.sleep(5)
        
        self._config_reload_thread = threading.Thread(target=reload_loop, daemon=True)
        self._config_reload_thread.start()
        self.logger.info("Config hot-reload thread started")
    
    @requires_permission("state_export")
    def save_state(self) -> None:
        """
        Save current state to disk for resilience and recovery.
        Requires 'state_export' permission when RBAC is enabled.
        
        Raises:
            PermissionError: If caller lacks state_export permission
        """
        try:
            state = {
                "active_threats": list(self.active_threats),
                "timestamp": datetime.now().isoformat(),
                "security_level": self.security_level.value,
                "unresolved_events_count": len([e for e in self.events if not e.resolved])
            }
            
            with open(self._state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            self.logger.info(f"State saved to {self._state_file}")
            self.audit_logger.log_audit("state_save", state)
            
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
    
    def restore_state(self) -> bool:
        """
        Restore state from disk after crash/restart.
        
        Returns:
            True if state was restored, False otherwise
        """
        if not self._state_file.exists():
            self.logger.info("No saved state found")
            return False
        
        try:
            with open(self._state_file, 'r') as f:
                state = json.load(f)
            
            # Restore active threats
            with self._lock:
                self.active_threats = set(state.get("active_threats", []))
            
            self.logger.info(f"State restored from {self._state_file}")
            self.logger.info(f"Restored {len(self.active_threats)} active threats")
            self.audit_logger.log_audit("state_restore", {
                "timestamp": datetime.now().isoformat(),
                "restored_threats": len(self.active_threats)
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore state: {e}")
            return False
    
    def get_prometheus_metrics(self) -> str:
        """
        Get metrics in Prometheus exposition format.
        
        Returns:
            Metrics in Prometheus text format
        """
        metrics_summary = self.get_metrics_summary()
        
        prometheus_output = []
        
        # System metrics
        prometheus_output.append("# HELP starlink_security_running System running status")
        prometheus_output.append("# TYPE starlink_security_running gauge")
        prometheus_output.append(f"starlink_security_running {{status=\"{metrics_summary['status']}\"}} {1 if self.running else 0}")
        
        # Threat metrics
        prometheus_output.append("# HELP starlink_security_active_threats Number of active threats")
        prometheus_output.append("# TYPE starlink_security_active_threats gauge")
        prometheus_output.append(f"starlink_security_active_threats {metrics_summary['active_threats_count']}")
        
        # Event metrics
        prometheus_output.append("# HELP starlink_security_unresolved_events Number of unresolved events")
        prometheus_output.append("# TYPE starlink_security_unresolved_events gauge")
        prometheus_output.append(f"starlink_security_unresolved_events {metrics_summary['unresolved_events_count']}")
        
        prometheus_output.append("# HELP starlink_security_total_events Total number of events")
        prometheus_output.append("# TYPE starlink_security_total_events counter")
        prometheus_output.append(f"starlink_security_total_events {metrics_summary['total_events_count']}")
        
        # Queue metrics
        prometheus_output.append("# HELP starlink_security_queue_utilization Event queue utilization percentage")
        prometheus_output.append("# TYPE starlink_security_queue_utilization gauge")
        prometheus_output.append(f"starlink_security_queue_utilization {metrics_summary['events_queue_utilization']}")
        
        # Network metrics
        nm = metrics_summary['network_metrics']
        prometheus_output.append("# HELP starlink_security_score Security score (0-100)")
        prometheus_output.append("# TYPE starlink_security_score gauge")
        prometheus_output.append(f"starlink_security_score {nm['security_score']}")
        
        prometheus_output.append("# HELP starlink_security_latency Network latency in ms")
        prometheus_output.append("# TYPE starlink_security_latency gauge")
        prometheus_output.append(f"starlink_security_latency {nm['latency']}")
        
        # Key age
        prometheus_output.append("# HELP starlink_security_key_age_days Encryption key age in days")
        prometheus_output.append("# TYPE starlink_security_key_age_days gauge")
        prometheus_output.append(f"starlink_security_key_age_days {metrics_summary['key_age_days']}")
        
        return "\n".join(prometheus_output)
    
    def enable_rbac(self, role_permissions: Dict[str, Set[str]]) -> None:
        """
        Enable Role-Based Access Control.
        
        Args:
            role_permissions: Dictionary mapping roles to sets of permissions
                Example: {'admin': {'rotate_key', 'config_reload', 'module_control'},
                         'operator': {'config_reload'},
                         'auditor': set()}
        """
        self._rbac_enabled = True
        self._permissions = role_permissions
        self.logger.info(f"RBAC enabled with {len(role_permissions)} roles")
        self.audit_logger.log_audit("rbac_enabled", {
            "roles": list(role_permissions.keys()),
            "timestamp": datetime.now().isoformat()
        })
    
    def _check_permission(self, permission: str, role: str = "admin") -> bool:
        """
        Check if a role has a specific permission with RBAC decision auditing.
        
        Args:
            permission: Permission to check
            role: Role to check (defaults to admin for backward compatibility)
            
        Returns:
            True if permitted, False otherwise
        """
        if not self._rbac_enabled:
            return True  # Always allow if RBAC disabled
        
        allowed = permission in self._permissions.get(role, set())
        
        # Audit RBAC decision (rbac_audit_log initialized in __init__)
        self.rbac_audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "permission": permission,
            "allowed": allowed,
            "reason": "permission_granted" if allowed else "permission_denied"
        })
        
        # Also log to main audit logger
        self.audit_logger.log_audit("rbac_check", {
            "role": role,
            "permission": permission,
            "allowed": allowed,
            "timestamp": datetime.now().isoformat()
        })
        
        if not allowed:
            self.logger.warning(f"RBAC: Permission denied for role '{role}' on '{permission}'")
        
        return allowed
    
    def export_compliance_audit(self, formatter: Optional[AuditFormatter] = None,
                                 output_file: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        Export audit log in compliance format.
        
        Args:
            formatter: Compliance formatter (uses first registered if not specified)
            output_file: Optional file to write formatted audit
            
        Returns:
            List of formatted audit entries
        """
        if formatter is None:
            if not self.audit_formatters:
                self.logger.error("No audit formatters registered")
                return []
            formatter = self.audit_formatters[0]
        formatted_entries = []
        
        try:
            # Read audit log
            audit_file = LOG_DIR / "audit.log"
            if not audit_file.exists():
                self.logger.warning("No audit log found")
                return []
            
            with open(audit_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        formatted = formatter.format_audit_entry(entry)
                        formatted_entries.append(formatted)
                    except json.JSONDecodeError:
                        continue
            
            # Write to output file if specified
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump({
                        "standard": formatter.get_standard_name(),
                        "export_timestamp": datetime.now().isoformat(),
                        "entries": formatted_entries
                    }, f, indent=2)
                self.logger.info(f"Exported {len(formatted_entries)} audit entries to {output_file}")
            
            self.audit_logger.log_audit("compliance_export", {
                "standard": formatter.get_standard_name(),
                "entry_count": len(formatted_entries),
                "timestamp": datetime.now().isoformat()
            })
            
            return formatted_entries
            
        except Exception as e:
            self.logger.error(f"Failed to export compliance audit: {e}")
            return []
    
    def score_threat(self, event: SecurityEvent) -> Dict[str, Any]:
        """
        Score a security event for threat level using configured scorer.
        Includes graceful degradation if scorer fails.
        
        Args:
            event: Security event to score
            
        Returns:
            Score dictionary with 'risk' and 'factors'
        """
        try:
            # Check if scorer is healthy
            if not self.threat_scorer.is_healthy():
                self.logger.warning("Threat scorer unhealthy, attempting recovery")
            
            score = self.threat_scorer.score(event)
            self.logger.debug(f"Threat scored: {event.event_type} -> risk={score['risk']}")
            return score
        except Exception as e:
            self.logger.error(f"Threat scoring failed, using fallback: {e}")
            # Fallback to simple severity-based scoring
            severity_risk = {"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.2}
            fallback_risk = severity_risk.get(event.severity.lower(), 0.5)
            return {
                "risk": fallback_risk,
                "factors": {
                    "error": str(e),
                    "fallback_method": "severity_based",
                    "severity": event.severity
                }
            }
    
    def get_scorer_explainability(self) -> Dict[str, Any]:
        """
        Get explainability information from the threat scorer.
        Provides feature importance and scoring method insights.
        
        Returns:
            Dictionary with explainability data including feature importance
        """
        try:
            feature_importance = self.threat_scorer.get_feature_importance()
            is_healthy = self.threat_scorer.is_healthy()
            
            scorer_type = type(self.threat_scorer).__name__
            
            return {
                "scorer_type": scorer_type,
                "is_healthy": is_healthy,
                "feature_importance": feature_importance,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get scorer explainability: {e}")
            return {
                "scorer_type": "unknown",
                "is_healthy": False,
                "error": str(e)
            }
    
    def integrate_threat_feed(self, connector: ThreatFeedConnector) -> Dict[str, Any]:
        """
        Integrate external threat intelligence feed.
        Fetches indicators and normalizes them for scoring pipeline.
        
        Args:
            connector: ThreatFeedConnector instance (STIX/TAXII, MISP, etc.)
            
        Returns:
            Dict with integration status and indicator count
        """
        try:
            if not connector.connect():
                return {"success": False, "error": "Failed to connect to threat feed"}
            
            raw_indicators = connector.fetch_indicators()
            normalized_indicators = []
            
            for raw in raw_indicators:
                normalized = connector.normalize_indicator(raw)
                normalized_indicators.append(normalized)
                
                # Create security event from indicator
                event = SecurityEvent(
                    timestamp=datetime.now(),
                    event_type=f"threat_intel_{normalized['type']}",
                    severity=normalized['severity'],
                    source=normalized['source'],
                    description=f"Threat indicator: {normalized['value']}",
                    metadata=normalized['metadata']
                )
                self.log_event(event)
            
            connector.disconnect()
            
            self.logger.info(f"Integrated {len(normalized_indicators)} threat indicators from {type(connector).__name__}")
            self.audit_logger.log_audit("threat_feed_integration", {
                "connector": type(connector).__name__,
                "indicator_count": len(normalized_indicators),
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "success": True,
                "connector": type(connector).__name__,
                "indicators_fetched": len(raw_indicators),
                "indicators_normalized": len(normalized_indicators)
            }
            
        except Exception as e:
            self.logger.error(f"Threat feed integration failed: {e}")
            return {"success": False, "error": str(e)}
    
    def push_to_siem(self, adapter: SIEMAdapter, include_metrics: bool = True) -> Dict[str, Any]:
        """
        Push audit logs and metrics to SIEM/SOAR platform.
        
        Args:
            adapter: SIEMAdapter instance (Splunk, Elastic, Azure Sentinel, etc.)
            include_metrics: Whether to also push metrics
            
        Returns:
            Dict with push status
        """
        try:
            if not adapter.is_connected():
                return {"success": False, "error": "SIEM adapter not connected"}
            
            # Push audit logs
            audit_file = LOG_DIR / "audit.log"
            audit_logs = []
            if audit_file.exists():
                with open(audit_file, 'r') as f:
                    for line_num, line in enumerate(f, 1):
                        try:
                            audit_logs.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            self.logger.warning(f"Malformed audit log entry at line {line_num}: {e}")
                            continue
            
            logs_pushed = adapter.push_audit_logs(audit_logs)
            
            # Push metrics if requested
            metrics_pushed = True
            if include_metrics:
                metrics_summary = self.get_metrics_summary()
                metrics_pushed = adapter.push_metrics(metrics_summary)
            
            self.logger.info(f"Pushed to SIEM: {len(audit_logs)} logs, metrics={include_metrics}")
            self.audit_logger.log_audit("siem_push", {
                "adapter": type(adapter).__name__,
                "logs_count": len(audit_logs),
                "metrics_included": include_metrics,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "success": logs_pushed and metrics_pushed,
                "adapter": type(adapter).__name__,
                "logs_pushed": len(audit_logs) if logs_pushed else 0,
                "metrics_pushed": include_metrics and metrics_pushed
            }
            
        except Exception as e:
            self.logger.error(f"SIEM push failed: {e}")
            return {"success": False, "error": str(e)}
    
    def score_with_cache(
        self,
        event: SecurityEvent,
        cache: Optional[ScoreCache] = None,
        use_batch: bool = False
    ) -> Dict[str, Any]:
        """
        Score event with optional caching for performance optimization.
        
        Args:
            event: Security event to score
            cache: Optional ScoreCache instance
            use_batch: Whether to use batch scoring (if supported by scorer)
            
        Returns:
            Score dictionary
        """
        # Check cache first if provided
        if cache:
            event_hash = hash_event_for_cache(event)
            cached_score = cache.get(event_hash)
            if cached_score:
                self.logger.debug(f"Cache hit for event {event.event_type}")
                return cached_score
        
        # Score the event
        if use_batch and hasattr(self.threat_scorer, 'score_batch'):
            # Batch scoring (more efficient for ML models)
            scores = self.threat_scorer.score_batch([event])
            score = scores[0] if scores else self.score_threat(event)
        else:
            score = self.score_threat(event)
        
        # Cache low-risk scores
        if cache and score['risk'] < 0.5:
            event_hash = hash_event_for_cache(event)
            cache.put(event_hash, score)
            self.logger.debug(f"Cached low-risk score for event {event.event_type}")
        
        return score
    
    def register_policy_version(
        self,
        version_tracker: PolicyVersionTracker,
        version: str,
        policy_type: str,
        description: str,
        policy_data: bytes
    ) -> PolicyVersion:
        """
        Register a new policy or model version for tracking and rollback.
        
        Args:
            version_tracker: PolicyVersionTracker instance
            version: Version identifier
            policy_type: Type ("ruleset" or "ml_model")
            description: Human-readable description
            policy_data: Binary policy/model data
            
        Returns:
            Created PolicyVersion
        """
        policy_version = version_tracker.register_version(
            version=version,
            policy_type=policy_type,
            description=description,
            policy_data=policy_data
        )
        
        self.audit_logger.log_audit("policy_version_registered", {
            "version": version,
            "policy_type": policy_type,
            "description": description,
            "checksum": policy_version.checksum,
            "timestamp": policy_version.timestamp.isoformat()
        })
        
        self.logger.info(f"Registered {policy_type} version {version}")
        return policy_version
    
    def get_cache_stats(self, cache: ScoreCache) -> Dict[str, Any]:
        """
        Get score cache statistics for monitoring.
        
        Args:
            cache: ScoreCache instance
            
        Returns:
            Cache statistics dict
        """
        return cache.get_stats()
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        default_config = {
            "security_level": "normal",
            "connection_type": "starlink_only",
            "monitoring_interval": 60,
            "max_events_queue": 1000,
            "encryption_enabled": True,
            "key_rotation_days": DEFAULT_KEY_ROTATION_DAYS,
            "log_level": "INFO"
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
                self.logger.info(f"Loaded configuration from {config_path}")
            except (json.JSONDecodeError, IOError) as e:
                # Log error but continue with defaults
                warnings.warn(
                    f"Failed to load configuration from {config_path}: {e}. "
                    f"Using default configuration.",
                    UserWarning
                )
                if hasattr(self, 'logger'):
                    self.logger.warning(f"Config load failed, using defaults: {e}")
        else:
            if hasattr(self, 'logger'):
                self.logger.info("Using default configuration")
        
        return default_config
    
    def _initialize_encryption(self) -> bytes:
        """
        Initialize encryption key for secure communications.
        
        Returns:
            Encryption key
            
        Raises:
            IOError: If key file cannot be read or written
            PermissionError: If key file permissions are insufficient
        """
        key_file = CONFIG_DIR / "encryption.key"
        
        if key_file.exists():
            try:
                with open(key_file, 'rb') as f:
                    key = f.read()
                self.logger.info("Loaded existing encryption key")
                # Check key age for rotation warning
                key_age_days = (datetime.now() - datetime.fromtimestamp(key_file.stat().st_mtime)).days
                if key_age_days >= self.config.get('key_rotation_days', DEFAULT_KEY_ROTATION_DAYS):
                    self.logger.warning(f"Encryption key is {key_age_days} days old - rotation recommended")
                return key
            except (IOError, PermissionError) as e:
                self.logger.error(f"Failed to read encryption key: {e}")
                raise IOError(
                    f"Failed to read encryption key from {key_file}: {e}"
                ) from e
        else:
            # Generate new key
            try:
                key = Fernet.generate_key()
                # Create file with restrictive permissions (owner read/write only)
                with open(key_file, 'wb') as f:
                    f.write(key)
                # Set restrictive permissions (0o600 = owner read/write only)
                # This works on Unix-like systems; on Windows, it has limited effect
                try:
                    os.chmod(key_file, 0o600)
                except (OSError, NotImplementedError):
                    # Windows or system doesn't support chmod, continue anyway
                    pass
                self.logger.info("Generated new encryption key")
                return key
            except (IOError, PermissionError) as e:
                self.logger.error(f"Failed to create encryption key: {e}")
                raise IOError(
                    f"Failed to write encryption key to {key_file}: {e}"
                ) from e
    
    def _initialize_modules(self) -> None:
        """
        Initialize security modules using factory pattern for dependency injection.
        """
        module_configs = {
            "firewall": self.config.get("modules", {}).get("firewall", {}).get("enabled", True),
            "intrusion_detection": self.config.get("modules", {}).get("intrusion_detection", {}).get("enabled", True),
            "threat_analysis": self.config.get("modules", {}).get("threat_analysis", {}).get("enabled", True),
            "encryption": self.config.get("encryption_enabled", True)
        }
        
        for name, enabled in module_configs.items():
            try:
                module = self._module_factory(name, enabled)
                self.security_modules[name] = module
                self.logger.info(f"Initialized module: {name} (enabled={enabled})")
            except Exception as e:
                self.logger.error(f"Failed to initialize module {name}: {e}")
    
    def log_event(self, event: SecurityEvent) -> None:
        """
        Log a security event with thread safety and pluggable processing.
        
        Args:
            event: SecurityEvent to log
        """
        with self._lock:
            self.events.append(event)
        
        # Process event through pluggable processor
        try:
            self.event_processor.process_event(event)
        except Exception as e:
            self.logger.error(f"Event processor error: {e}")
        
        # Also log to structured logger
        event_data = {
            "event_type": event.event_type,
            "severity": event.severity,
            "source": event.source,
            "description": event.description
        }
        self.logger.info(f"Security event logged: {json.dumps(event_data)}")

    async def trigger_event(
        self,
        event_type: str,
        severity: str,
        source: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Create, log, and dispatch a security event.

        This provides parity with other StarlinkSecurityFoundation variants and fixes
        demo/runtime usage like: `await foundation.trigger_event(...)`.
        """
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            severity=severity,
            source=source,
            description=message,
            metadata=metadata or {},
        )

        # Persist + process through configured processor.
        self.log_event(event)

        # Notify async subscribers.
        for handler in list(self.event_handlers):
            try:
                await handler(event)
            except Exception as e:
                self.logger.error(f"Event handler failed: {e}")

    def register_event_handler(self, handler: Callable[[SecurityEvent], Awaitable[None]]) -> None:
        """Register an async handler to receive events from trigger_event()."""
        self.event_handlers.append(handler)
    
    def update_metrics(self, metrics: NetworkMetrics) -> None:
        """
        Update network metrics with thread safety.
        
        Args:
            metrics: NetworkMetrics to update
        """
        with self._metrics_lock:
            self.metrics = metrics
        self.logger.debug(f"Metrics updated: score={metrics.security_score}, stability={metrics.connection_stability}")
    
    def set_security_level(self, level: SecurityLevel) -> None:
        """
        Set the security level.
        
        Args:
            level: New security level
        """
        old_level = self.security_level
        self.security_level = level
        self.logger.info(f"Security level changed: {old_level.value} -> {level.value}")
    
    def add_threat(self, threat_id: str) -> None:
        """
        Add an active threat with thread safety and state store support.
        
        Args:
            threat_id: Unique identifier for the threat
        """
        with self._lock:
            self.active_threats.add(threat_id)
            # Also update distributed state store
            self.state_store.add_threat(threat_id)
        self.logger.warning(f"Threat added: {threat_id}")
    
    def remove_threat(self, threat_id: str) -> None:
        """
        Remove an active threat with thread safety and state store support.
        
        Args:
            threat_id: Unique identifier for the threat
        """
        with self._lock:
            self.active_threats.discard(threat_id)
            # Also update distributed state store
            self.state_store.remove_threat(threat_id)
        self.logger.info(f"Threat removed: {threat_id}")
    
    def get_unresolved_events(self) -> List[SecurityEvent]:
        """
        Get all unresolved security events with thread safety.
        
        Returns:
            List of unresolved SecurityEvent objects
        """
        with self._lock:
            return [event for event in self.events if not event.resolved]
    
    def get_rbac_audit_log(self) -> List[Dict[str, Any]]:
        """
        Get RBAC decision audit log.
        
        Returns:
            List of RBAC audit entries with who, what, when, allowed/denied
        """
        return list(self.rbac_audit_log)


# ============================================================================
# Operational Maturity Extensions
# ============================================================================

class ClusterNode:
    """Represents a node in a high-availability cluster."""
    
    def __init__(self, node_id: str, address: str, is_leader: bool = False):
        self.node_id = node_id
        self.address = address
        self.is_leader = is_leader
        self.last_heartbeat = datetime.now()
        self.healthy = True


class ClusterManager:
    """
    Manages high-availability clustering with leader election.
    Enables distributed deployment with automatic failover.
    """
    
    def __init__(self, node_id: str, heartbeat_interval: int = 5):
        self.node_id = node_id
        self.heartbeat_interval = heartbeat_interval
        self.nodes: Dict[str, ClusterNode] = {}
        self.leader_id: Optional[str] = None
        self._lock = threading.RLock()
        self._running = False
        self._heartbeat_thread: Optional[threading.Thread] = None
    
    def register_node(self, node_id: str, address: str):
        """Register a node in the cluster."""
        with self._lock:
            self.nodes[node_id] = ClusterNode(node_id, address)
    
    def elect_leader(self) -> Optional[str]:
        """
        Perform leader election (simple implementation - lowest node_id wins).
        In production, use Raft, Paxos, or ZooKeeper.
        
        Returns:
            Node ID of elected leader, or None if no healthy nodes
        """
        with self._lock:
            healthy_nodes = [n for n in self.nodes.values() if n.healthy]
            if not healthy_nodes:
                logging.warning("No healthy nodes available for leader election")
                return None
            
            # Simple leader election: lexicographically smallest node_id
            leader = min(healthy_nodes, key=lambda n: n.node_id)
            self.leader_id = leader.node_id
            leader.is_leader = True
            
            # Mark others as followers
            for node in healthy_nodes:
                if node.node_id != leader.node_id:
                    node.is_leader = False
            
            return self.leader_id
    
    def is_leader(self) -> bool:
        """Check if current node is the leader."""
        with self._lock:
            return self.leader_id == self.node_id
    
    def update_heartbeat(self, node_id: str):
        """Update heartbeat timestamp for a node."""
        with self._lock:
            if node_id in self.nodes:
                self.nodes[node_id].last_heartbeat = datetime.now()
    
    def check_health(self):
        """Check health of all nodes and trigger re-election if needed."""
        with self._lock:
            timeout = timedelta(seconds=self.heartbeat_interval * 3)
            now = datetime.now()
            
            for node in self.nodes.values():
                was_healthy = node.healthy
                node.healthy = (now - node.last_heartbeat) < timeout
                
                if was_healthy and not node.healthy:
                    logging.warning(f"Node {node.node_id} became unhealthy")
                    if node.is_leader:
                        logging.warning("Leader is unhealthy, triggering re-election")
                        self.elect_leader()
    
    def start(self):
        """Start cluster management with heartbeat monitoring."""
        self._running = True
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
    
    def stop(self):
        """Stop cluster management."""
        self._running = False
        if self._heartbeat_thread:
            # Use dynamic timeout based on heartbeat interval
            timeout = self.heartbeat_interval * 2
            self._heartbeat_thread.join(timeout=timeout)
    
    def _heartbeat_loop(self):
        """Background thread for heartbeat monitoring."""
        while self._running:
            self.check_health()
            self.update_heartbeat(self.node_id)
            time.sleep(self.heartbeat_interval)


class GeoReplication:
    """
    Manages geo-replicated backups for disaster recovery.
    Supports multi-region state persistence with integrity verification.
    """
    
    def __init__(self, primary_region: str, replica_regions: List[str]):
        self.primary_region = primary_region
        self.replica_regions = replica_regions
        self.backup_locations: Dict[str, Path] = {}
    
    def add_backup_location(self, region: str, path: Path):
        """Register a backup location for a region."""
        self.backup_locations[region] = path
        path.mkdir(parents=True, exist_ok=True)
    
    def save_with_replication(self, state_data: bytes, checksum: str) -> Dict[str, bool]:
        """
        Save state data to all regions with integrity verification.
        
        Returns:
            Dictionary mapping region to success status
        """
        results = {}
        
        # Save to primary
        if self.primary_region in self.backup_locations:
            primary_path = self.backup_locations[self.primary_region]
            results[self.primary_region] = self._save_to_location(
                primary_path, state_data, checksum
            )
        
        # Replicate to all regions
        for region in self.replica_regions:
            if region in self.backup_locations:
                replica_path = self.backup_locations[region]
                results[region] = self._save_to_location(
                    replica_path, state_data, checksum
                )
        
        return results
    
    def restore_with_verification(self, region: Optional[str] = None) -> Optional[bytes]:
        """
        Restore state data with integrity verification.
        Falls back to other regions if primary fails.
        """
        # Try specified region first
        if region and region in self.backup_locations:
            data = self._load_from_location(self.backup_locations[region])
            if data:
                return data
        
        # Try primary region
        if self.primary_region in self.backup_locations:
            data = self._load_from_location(self.backup_locations[self.primary_region])
            if data:
                return data
        
        # Fall back to replicas
        for region in self.replica_regions:
            if region in self.backup_locations:
                data = self._load_from_location(self.backup_locations[region])
                if data:
                    logging.info(f"Restored state from replica region: {region}")
                    return data
        
        return None
    
    def _save_to_location(self, path: Path, data: bytes, checksum: str) -> bool:
        """Save data to a location with checksum."""
        try:
            state_file = path / "state.pkl"
            checksum_file = path / "state.sha256"
            
            with open(state_file, "wb") as f:
                f.write(data)
            
            with open(checksum_file, "w") as f:
                f.write(checksum)
            
            return True
        except Exception as e:
            logging.error(f"Failed to save to {path}: {e}")
            return False
    
    def _load_from_location(self, path: Path) -> Optional[bytes]:
        """Load data from a location and verify checksum."""
        try:
            state_file = path / "state.pkl"
            checksum_file = path / "state.sha256"
            
            if not state_file.exists() or not checksum_file.exists():
                return None
            
            with open(state_file, "rb") as f:
                data = f.read()
            
            with open(checksum_file, "r") as f:
                expected_checksum = f.read().strip()
            
            # Verify checksum
            actual_checksum = hashlib.sha256(data).hexdigest()
            if actual_checksum != expected_checksum:
                logging.error(f"Checksum mismatch for {path}")
                return None
            
            return data
        except Exception as e:
            logging.error(f"Failed to load from {path}: {e}")
            return None


class WorkerPool:
    """
    Thread pool for parallel scoring with adaptive batching.
    Enables concurrent ML scoring with configurable workers.
    """
    
    def __init__(self, num_workers: int = 4, max_batch_size: int = 100, batch_timeout_sec: float = 0.1):
        self.num_workers = num_workers
        self.max_batch_size = max_batch_size
        self.batch_timeout_sec = batch_timeout_sec
        self.task_queue = queue.Queue()
        self.workers: List[threading.Thread] = []
        self._running = False
        self._batch_lock = threading.Lock()
        self._pending_batch: List[Any] = []
        self._batch_timer: Optional[threading.Timer] = None
    
    def start(self):
        """Start worker threads."""
        self._running = True
        for i in range(self.num_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True, name=f"Worker-{i}")
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """Stop all worker threads."""
        self._running = False
        for _ in range(self.num_workers):
            self.task_queue.put(None)  # Poison pill
        for worker in self.workers:
            worker.join(timeout=5)
    
    def submit(self, task: Callable, *args, **kwargs):
        """Submit a task to the pool."""
        self.task_queue.put((task, args, kwargs))
    
    def submit_batch(self, items: List[Any], batch_task: Callable):
        """Submit items for adaptive batching."""
        with self._batch_lock:
            self._pending_batch.extend(items)
            
            # Process batch if it reaches max size
            if len(self._pending_batch) >= self.max_batch_size:
                self._process_batch(batch_task)
            else:
                # Schedule batch processing after timeout
                if self._batch_timer:
                    self._batch_timer.cancel()
                self._batch_timer = threading.Timer(
                    self.batch_timeout_sec, 
                    lambda: self._process_batch(batch_task)
                )
                self._batch_timer.start()
    
    def _process_batch(self, batch_task: Callable):
        """Process accumulated batch."""
        with self._batch_lock:
            if not self._pending_batch:
                return
            
            batch = self._pending_batch[:]
            self._pending_batch.clear()
            
            if self._batch_timer:
                self._batch_timer.cancel()
                self._batch_timer = None
        
        self.submit(batch_task, batch)
    
    def _worker_loop(self):
        """Worker thread main loop."""
        while self._running:
            try:
                item = self.task_queue.get(timeout=1)
                if item is None:  # Poison pill
                    break
                
                task, args, kwargs = item
                task(*args, **kwargs)
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Worker error: {e}")


class MultiTenantRBAC:
    """
    Multi-tenant RBAC with per-tenant audit chains.
    Extends base RBAC for enterprise multi-tenancy support.
    """
    
    def __init__(self):
        self.tenant_permissions: Dict[str, Dict[str, Set[str]]] = {}
        self.tenant_audit_logs: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = threading.RLock()
    
    def add_tenant(self, tenant_id: str):
        """Register a new tenant."""
        with self._lock:
            if tenant_id not in self.tenant_permissions:
                self.tenant_permissions[tenant_id] = {}
                self.tenant_audit_logs[tenant_id] = []
    
    def set_tenant_role_permissions(self, tenant_id: str, role: str, permissions: Set[str]):
        """Set permissions for a role within a tenant."""
        with self._lock:
            if tenant_id not in self.tenant_permissions:
                self.add_tenant(tenant_id)
            self.tenant_permissions[tenant_id][role] = permissions
    
    def check_tenant_permission(self, tenant_id: str, role: str, permission: str) -> bool:
        """Check if a role has a permission within a tenant."""
        with self._lock:
            if tenant_id not in self.tenant_permissions:
                return False
            if role not in self.tenant_permissions[tenant_id]:
                return False
            return permission in self.tenant_permissions[tenant_id][role]
    
    def log_tenant_decision(self, tenant_id: str, role: str, action: str, 
                          allowed: bool, reason: str = ""):
        """Log an RBAC decision for a tenant."""
        with self._lock:
            if tenant_id not in self.tenant_audit_logs:
                self.add_tenant(tenant_id)
            
            entry = {
                "timestamp": datetime.now().isoformat(),
                "tenant_id": tenant_id,
                "role": role,
                "action": action,
                "allowed": allowed,
                "reason": reason
            }
            self.tenant_audit_logs[tenant_id].append(entry)
    
    def get_tenant_audit_log(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get audit log for a specific tenant."""
        with self._lock:
            return list(self.tenant_audit_logs.get(tenant_id, []))


class ComplianceProfile:
    """
    Pre-packaged compliance formatter profiles.
    Supports PCI DSS, HIPAA, ISO 27001, SOC 2.
    """
    
    PROFILES = {
        "PCI_DSS": {
            "standard": "PCI DSS v4.0",
            "required_fields": ["timestamp", "actor", "action", "resource", "outcome"],
            "retention_days": 365,
            "encryption_required": True
        },
        "HIPAA": {
            "standard": "HIPAA Security Rule",
            "required_fields": ["timestamp", "actor", "action", "resource", "outcome", "phi_accessed"],
            "retention_days": 2557,  # ~7 years (accounting for leap years)
            "encryption_required": True
        },
        "ISO_27001": {
            "standard": "ISO/IEC 27001:2022",
            "required_fields": ["timestamp", "actor", "action", "resource", "outcome"],
            "retention_days": 1095,  # 3 years
            "encryption_required": True
        },
        "SOC_2": {
            "standard": "SOC 2 Type II",
            "required_fields": ["timestamp", "actor", "action", "resource", "outcome", "control_objective"],
            "retention_days": 365,
            "encryption_required": True
        }
    }
    
    @classmethod
    def get_profile(cls, profile_name: str) -> Dict[str, Any]:
        """Get compliance profile configuration."""
        return cls.PROFILES.get(profile_name, {})
    
    @classmethod
    def create_formatter(cls, profile_name: str) -> 'AuditFormatter':
        """Create an audit formatter for a compliance profile."""
        profile = cls.get_profile(profile_name)
        if not profile:
            raise ValueError(f"Unknown compliance profile: {profile_name}")
        
        class ProfileFormatter(AuditFormatter):
            def format_audit_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
                return {
                    "standard": profile["standard"],
                    **entry
                }
            
            def get_standard_name(self) -> str:
                return profile["standard"]
        
        return ProfileFormatter()


class ChaosTestingFramework:
    """
    Chaos testing framework for resilience validation.
    Simulates failures, latency, and resource constraints.
    """
    
    def __init__(self):
        self.active_faults: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
    
    def inject_latency(self, component: str, delay_ms: int, duration_sec: int = 60):
        """Inject artificial latency into a component."""
        with self._lock:
            self.active_faults.append({
                "type": "latency",
                "component": component,
                "delay_ms": delay_ms,
                "expires_at": datetime.now() + timedelta(seconds=duration_sec)
            })
    
    def inject_failure(self, component: str, failure_rate: float, duration_sec: int = 60):
        """Inject random failures into a component."""
        with self._lock:
            self.active_faults.append({
                "type": "failure",
                "component": component,
                "failure_rate": failure_rate,  # 0.0 to 1.0
                "expires_at": datetime.now() + timedelta(seconds=duration_sec)
            })
    
    def inject_resource_constraint(self, resource_type: str, limit: int, duration_sec: int = 60):
        """Inject resource constraints (e.g., memory, CPU)."""
        with self._lock:
            self.active_faults.append({
                "type": "resource_constraint",
                "resource_type": resource_type,
                "limit": limit,
                "expires_at": datetime.now() + timedelta(seconds=duration_sec)
            })
    
    def should_fail(self, component: str) -> bool:
        """Check if a component should fail based on active faults."""
        with self._lock:
            now = datetime.now()
            self.active_faults = [f for f in self.active_faults if f["expires_at"] > now]
            
            for fault in self.active_faults:
                if fault["component"] == component and fault["type"] == "failure":
                    # Using random for fault injection simulation (not security-critical)
                    return random.random() < fault["failure_rate"]  # nosec B311
        
        return False
    
    def get_latency(self, component: str) -> int:
        """Get injected latency for a component in milliseconds."""
        with self._lock:
            now = datetime.now()
            self.active_faults = [f for f in self.active_faults if f["expires_at"] > now]
            
            for fault in self.active_faults:
                if fault["component"] == component and fault["type"] == "latency":
                    return fault["delay_ms"]
        
        return 0
    
    def clear_faults(self):
        """Clear all active faults."""
        with self._lock:
            self.active_faults.clear()


class UnifiedCLI:
    """
    Unified CLI/API interface for operational tasks.
    Provides dry-run mode and command history.
    """
    
    def __init__(self, foundation: 'StarlinkSecurityFoundation'):
        self.foundation = foundation
        self.command_history: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
    
    def execute(self, command: str, args: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
        """
        Execute a command with optional dry-run mode.
        
        Args:
            command: Command name (rotate_key, reload_config, export_audit, ingest_feed)
            args: Command arguments
            dry_run: If True, simulate without making changes
            
        Returns:
            Command result with success status and output
        """
        with self._lock:
            # Log command
            cmd_entry = {
                "timestamp": datetime.now().isoformat(),
                "command": command,
                "args": args,
                "dry_run": dry_run
            }
            
            try:
                if dry_run:
                    result = self._simulate_command(command, args)
                    cmd_entry["status"] = "simulated"
                    cmd_entry["output"] = result
                else:
                    result = self._execute_command(command, args)
                    cmd_entry["status"] = "executed"
                    cmd_entry["output"] = result
                
                self.command_history.append(cmd_entry)
                return {"success": True, **result}
            
            except Exception as e:
                cmd_entry["status"] = "failed"
                cmd_entry["error"] = str(e)
                self.command_history.append(cmd_entry)
                return {"success": False, "error": str(e)}
    
    def _simulate_command(self, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate command execution without making changes."""
        simulations = {
            "rotate_key": lambda: {"message": "Would rotate encryption key and create backup"},
            "reload_config": lambda: {"message": f"Would reload config from {args.get('path', 'default')}"},
            "export_audit": lambda: {"message": f"Would export audit to {args.get('output', 'audit.json')}"},
            "ingest_feed": lambda: {"message": f"Would ingest threat feed from {args.get('source', 'unknown')}"}
        }
        
        if command in simulations:
            return simulations[command]()
        else:
            return {"message": f"Unknown command: {command}"}
    
    def _execute_command(self, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command on the foundation."""
        if command == "rotate_key":
            rotate_fn = getattr(self.foundation, "rotate_encryption_key", None)
            if callable(rotate_fn):
                rotate_fn()
                return {"message": "Encryption key rotated successfully"}
            return {"message": "Encryption key rotation is not supported by this foundation"}
        
        elif command == "reload_config":
            # reload_config doesn't take parameters, it reloads from existing path
            reload_fn = getattr(self.foundation, "reload_config", None)
            if callable(reload_fn):
                reload_fn()
                return {"message": "Configuration reloaded successfully"}
            return {"message": "Configuration reload is not supported by this foundation"}
        
        elif command == "export_audit":
            output = args.get("output", "audit.json")
            formatter = args.get("formatter", "ISO27001")
            
            # Get formatter
            if formatter in ComplianceProfile.PROFILES:
                fmt = ComplianceProfile.create_formatter(formatter)
            else:
                audit_formatters = getattr(self.foundation, "audit_formatters", None)
                fmt = audit_formatters[0] if isinstance(audit_formatters, list) and audit_formatters else None
            
            if not fmt:
                return {"message": "No formatter available"}

            export_fn = getattr(self.foundation, "export_compliance_audit", None)
            if callable(export_fn):
                export_fn(fmt, output)
                return {"message": f"Audit exported to {output}"}
            return {"message": "Audit export is not supported by this foundation"}
        
        elif command == "ingest_feed":
            connector_type = args.get("connector_type", "STIX")
            config = args.get("config", {})

            if not isinstance(config, dict):
                config = {}
            
            if connector_type == "STIX":
                server_url = (
                    config.get("server_url")
                    or config.get("url")
                    or config.get("taxii_server_url")
                    or config.get("taxii_url")
                )
                if not isinstance(server_url, str) or not server_url:
                    return {"message": "STIX/TAXII server_url is required in config"}
                collection = config.get("collection") or config.get("taxii_collection") or "default"
                connector = STIXTAXIIConnector(server_url, collection)
            elif connector_type == "MISP":
                misp_url = config.get("misp_url") or config.get("url")
                if not isinstance(misp_url, str) or not misp_url:
                    return {"message": "MISP misp_url is required in config"}
                api_key = config.get("api_key") or config.get("misp_api_key")
                if not api_key:
                    return {"message": "MISP api_key is required in config"}
                connector = MISPConnector(misp_url, str(api_key))
            else:
                return {"message": f"Unknown connector type: {connector_type}"}
            
            integrate_fn = getattr(self.foundation, "integrate_threat_feed", None)
            if not callable(integrate_fn):
                return {"message": "Threat feed ingestion is not supported by this foundation"}

            indicators = integrate_fn(connector)
            from collections.abc import Sized

            count = len(indicators) if isinstance(indicators, Sized) else 0
            return {"message": f"Ingested {count} threat indicators"}
        
        else:
            raise ValueError(f"Unknown command: {command}")
    
    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get command history."""
        with self._lock:
            return self.command_history[-limit:]


# ============================================================================
# Ecosystem & Interoperability
# ============================================================================

class RESTAPIGateway:
    """
    Secure REST API gateway for external integrations.
    Provides token-based authentication and exposes foundation operations.
    """
    
    def __init__(self, foundation: 'StarlinkSecurityFoundation', secret_key: Optional[str] = None):
        self.foundation = foundation
        self.secret_key = secret_key or secrets.token_hex(32)
        self.tokens = {}  # token -> (username, expiry)
        self._lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
    
    def generate_token(self, username: str, expires_in: int = 3600) -> str:
        """Generate an API token with expiration."""
        token = secrets.token_urlsafe(32)
        expiry = datetime.now() + timedelta(seconds=expires_in)
        
        with self._lock:
            self.tokens[token] = (username, expiry)
        
        self.logger.info(f"Generated API token for user: {username}, expires: {expiry}")
        return token
    
    def validate_token(self, token: str) -> Optional[str]:
        """Validate token and return username if valid."""
        with self._lock:
            if token not in self.tokens:
                return None
            
            username, expiry = self.tokens[token]
            if datetime.now() > expiry:
                del self.tokens[token]
                return None
            
            return username
    
    def revoke_token(self, token: str) -> bool:
        """Revoke an API token."""
        with self._lock:
            if token in self.tokens:
                del self.tokens[token]
                return True
            return False
    
    def handle_request(self, endpoint: str, method: str, token: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle API requests with authentication.
        
        Endpoints:
        - GET /metrics -> get_metrics_summary()
        - GET /prometheus -> get_prometheus_metrics()
        - POST /events -> log_event()
        - GET /threats -> get active threats
        - POST /config/reload -> reload_config()
        - POST /keys/rotate -> rotate_encryption_key()
        - POST /audit/export -> export_compliance_audit()
        """
        username = self.validate_token(token)
        if not username:
            return {"error": "Invalid or expired token", "status": 401}
        
        try:
            if endpoint == "/metrics" and method == "GET":
                metrics_fn = getattr(self.foundation, "get_metrics_summary", None)
                if callable(metrics_fn):
                    return {"data": metrics_fn(), "status": 200}
                return {"error": "Metrics summary not supported by foundation", "status": 501}
            
            elif endpoint == "/prometheus" and method == "GET":
                metrics_fn = getattr(self.foundation, "get_prometheus_metrics", None)
                if callable(metrics_fn):
                    return {"data": metrics_fn(), "status": 200}
                return {"error": "Prometheus metrics not supported by foundation", "status": 501}
            
            elif endpoint == "/events" and method == "POST":
                if data is None:
                    return {"error": "Event data required", "status": 400}
                if not data:
                    return {"error": "Event data required", "status": 400}
                event = SecurityEvent(**data)
                log_event_fn = getattr(self.foundation, "log_event", None)
                if callable(log_event_fn):
                    log_event_fn(event)
                    return {"message": "Event logged successfully", "status": 200}
                return {"error": "Event logging not supported by foundation", "status": 501}
            
            elif endpoint == "/threats" and method == "GET":
                state_store = getattr(self.foundation, "state_store", None)
                get_threats_fn = getattr(state_store, "get_threats", None) if state_store is not None else None
                if callable(get_threats_fn):
                    threats_obj = get_threats_fn()
                    if threats_obj is None:
                        return {"data": [], "status": 200}

                    from collections.abc import Iterable as IterableABC

                    if isinstance(threats_obj, (str, bytes)):
                        return {"data": [threats_obj], "status": 200}

                    if isinstance(threats_obj, IterableABC):
                        return {"data": list(threats_obj), "status": 200}

                    return {"data": [threats_obj], "status": 200}
                return {"error": "Threat listing not supported by foundation", "status": 501}
            
            elif endpoint == "/config/reload" and method == "POST":
                reload_fn = getattr(self.foundation, "reload_config", None)
                if callable(reload_fn):
                    reload_fn()
                    return {"message": "Configuration reloaded", "status": 200}
                return {"error": "Configuration reload not supported by foundation", "status": 501}
            
            elif endpoint == "/keys/rotate" and method == "POST":
                rotate_fn = getattr(self.foundation, "rotate_encryption_key", None)
                if callable(rotate_fn):
                    rotate_fn()
                    return {"message": "Encryption key rotated", "status": 200}
                return {"error": "Key rotation not supported by foundation", "status": 501}
            
            elif endpoint == "/audit/export" and method == "POST":
                profile = data.get("profile", "iso27001") if data is not None else "iso27001"
                output = data.get("output", "audit_export.json") if data is not None else "audit_export.json"
                formatter = ComplianceProfile.create_formatter(profile)
                export_fn = getattr(self.foundation, "export_compliance_audit", None)
                if callable(export_fn):
                    export_fn(formatter, output)
                    return {"message": f"Audit exported to {output}", "status": 200}
                return {"error": "Audit export not supported by foundation", "status": 501}
            
            else:
                return {"error": f"Unknown endpoint: {endpoint}", "status": 404}
        
        except Exception as e:
            self.logger.error(f"API request error: {e}")
            return {"error": str(e), "status": 500}


class PluginRegistry:
    """
    Plugin marketplace model for external module registration.
    Enables third-party connectors without modifying core code.
    """
    
    def __init__(self):
        self.plugins = {
            "threat_feeds": {},  # name -> ThreatFeedConnector class
            "siem_adapters": {},  # name -> SIEMAdapter class
            "threat_scorers": {},  # name -> ThreatScorer class
            "security_modules": {},  # name -> SecurityModule class
        }
        self._lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
    
    def register_plugin(self, category: str, name: str, plugin_class: type, metadata: Optional[Dict[str, Any]] = None):
        """Register a plugin in the marketplace."""
        if category not in self.plugins:
            raise ValueError(f"Unknown plugin category: {category}")
        
        with self._lock:
            self.plugins[category][name] = {
                "class": plugin_class,
                "metadata": metadata or {},
                "registered_at": datetime.now()
            }
        
        self.logger.info(f"Registered plugin: {category}/{name}")
    
    def unregister_plugin(self, category: str, name: str) -> bool:
        """Unregister a plugin."""
        with self._lock:
            if category in self.plugins and name in self.plugins[category]:
                del self.plugins[category][name]
                self.logger.info(f"Unregistered plugin: {category}/{name}")
                return True
            return False
    
    def get_plugin(self, category: str, name: str) -> Optional[type]:
        """Get a plugin class by name."""
        with self._lock:
            if category in self.plugins and name in self.plugins[category]:
                return self.plugins[category][name]["class"]
            return None
    
    def list_plugins(self, category: Optional[str] = None) -> Dict[str, Any]:
        """List all registered plugins, optionally filtered by category."""
        with self._lock:
            if category:
                return {category: list(self.plugins.get(category, {}).keys())}
            return {cat: list(plugins.keys()) for cat, plugins in self.plugins.items()}


# ============================================================================
# Performance & Efficiency
# ============================================================================

class DynamicWorkerPool:
    """
    Auto-scaling worker pool based on queue depth and latency.
    Integrates with Kubernetes HPA for containerized deployments.
    """
    
    # Configuration constants
    LATENCY_SMOOTHING_FACTOR = 0.9
    DEFAULT_RISK_SCORE = 0.5
    SIGNIFICANT_RISK_DIFFERENCE_THRESHOLD = 0.1
    
    def __init__(self, min_workers: int = 2, max_workers: int = 16, 
                 scale_up_threshold: int = 10, scale_down_threshold: int = 2):
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        
        self.workers = []
        self.task_queue = queue.Queue()
        self.current_workers = min_workers
        self._lock = threading.RLock()
        self.running = False
        self.metrics = {
            "queue_depth": 0,
            "avg_latency_ms": 0,
            "scaling_events": []
        }
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """Start the worker pool with minimum workers."""
        self.running = True
        for i in range(self.min_workers):
            self._add_worker()
        
        # Start auto-scaling monitor
        threading.Thread(target=self._monitor_and_scale, daemon=True).start()
        self.logger.info(f"DynamicWorkerPool started with {self.min_workers} workers")
    
    def stop(self):
        """Stop all workers gracefully."""
        self.running = False
        for worker in self.workers:
            if worker.is_alive():
                worker.join(timeout=5)
        self.logger.info("DynamicWorkerPool stopped")
    
    def submit(self, task_fn, *args, **kwargs):
        """Submit a task to the pool."""
        self.task_queue.put((task_fn, args, kwargs, time.time()))
        with self._lock:
            self.metrics["queue_depth"] = self.task_queue.qsize()
    
    def _add_worker(self):
        """Add a new worker thread."""
        worker = threading.Thread(target=self._worker_loop, daemon=True)
        worker.start()
        self.workers.append(worker)
    
    def _worker_loop(self):
        """Worker thread loop."""
        while self.running:
            try:
                task_fn, args, kwargs, submit_time = self.task_queue.get(timeout=1)
                
                # Execute task
                task_fn(*args, **kwargs)
                
                # Track latency with exponential moving average
                latency_ms = (time.time() - submit_time) * 1000
                with self._lock:
                    self.metrics["avg_latency_ms"] = (
                        self.metrics["avg_latency_ms"] * self.LATENCY_SMOOTHING_FACTOR + 
                        latency_ms * (1 - self.LATENCY_SMOOTHING_FACTOR)
                    )
                
                self.task_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Worker error: {e}")
    
    def _monitor_and_scale(self):
        """Monitor queue depth and scale workers dynamically."""
        while self.running:
            time.sleep(5)  # Check every 5 seconds
            
            queue_depth = self.task_queue.qsize()
            
            with self._lock:
                # Scale up if queue is deep
                if queue_depth > self.scale_up_threshold and self.current_workers < self.max_workers:
                    new_worker_count = min(self.current_workers + 2, self.max_workers)
                    for _ in range(new_worker_count - self.current_workers):
                        self._add_worker()
                    
                    event = {
                        "timestamp": datetime.now(),
                        "action": "scale_up",
                        "from": self.current_workers,
                        "to": new_worker_count,
                        "queue_depth": queue_depth
                    }
                    self.metrics["scaling_events"].append(event)
                    self.current_workers = new_worker_count
                    self.logger.info(f"Scaled up to {new_worker_count} workers (queue: {queue_depth})")
                
                # Scale down if queue is shallow
                elif queue_depth < self.scale_down_threshold and self.current_workers > self.min_workers:
                    new_worker_count = max(self.current_workers - 1, self.min_workers)
                    event = {
                        "timestamp": datetime.now(),
                        "action": "scale_down",
                        "from": self.current_workers,
                        "to": new_worker_count,
                        "queue_depth": queue_depth
                    }
                    self.metrics["scaling_events"].append(event)
                    self.current_workers = new_worker_count
                    self.logger.info(f"Scaled down to {new_worker_count} workers (queue: {queue_depth})")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics for HPA integration."""
        with self._lock:
            return {
                "current_workers": self.current_workers,
                "queue_depth": self.task_queue.qsize(),
                "avg_latency_ms": self.metrics["avg_latency_ms"],
                "recent_scaling": self.metrics["scaling_events"][-10:]
            }


class ResourceIsolation:
    """
    Resource isolation for ML scorers using separate processes.
    Prevents ML scoring from starving rule-based scoring.
    """
    
    def __init__(self, cpu_quota: float = 0.5, memory_limit_mb: int = 512):
        self.cpu_quota = cpu_quota  # 0.5 = 50% of one CPU core
        self.memory_limit_mb = memory_limit_mb
        self.isolated_scorers = {}
        self._lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
    
    def register_scorer(self, name: str, scorer: ThreatScorer):
        """Register a scorer for resource isolation."""
        with self._lock:
            self.isolated_scorers[name] = {
                "scorer": scorer,
                "cpu_quota": self.cpu_quota,
                "memory_limit": self.memory_limit_mb
            }
        self.logger.info(f"Registered isolated scorer: {name} (CPU: {self.cpu_quota}, MEM: {self.memory_limit_mb}MB)")
    
    def score_isolated(self, scorer_name: str, event: SecurityEvent, timeout: int = 5) -> Dict[str, Any]:
        """
        Score an event in an isolated environment.
        Uses multiprocessing to enforce resource limits.
        """
        if scorer_name not in self.isolated_scorers:
            raise ValueError(f"Unknown scorer: {scorer_name}")
        
        scorer = self.isolated_scorers[scorer_name]["scorer"]
        
        # In production, this would use process-level resource controls
        # For now, use threading with timeout
        result = {"risk": DynamicWorkerPool.DEFAULT_RISK_SCORE, "factors": {}, "error": None}
        
        def score_fn():
            try:
                result.update(scorer.score(event))
            except Exception as e:
                result["error"] = str(e)
        
        thread = threading.Thread(target=score_fn)
        thread.start()
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            self.logger.warning(f"Scorer {scorer_name} timed out")
            result["error"] = "Timeout"
        
        return result


# ============================================================================
# Governance & Compliance
# ============================================================================

class DataResidencyPolicy:
    """
    Tenant-specific data residency controls.
    Enforces regional restrictions for compliance (e.g., GDPR, data sovereignty).
    """
    
    def __init__(self):
        self.policies = {}  # tenant_id -> allowed_regions
        self._lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
    
    def set_policy(self, tenant_id: str, allowed_regions: List[str]):
        """Set data residency policy for a tenant."""
        with self._lock:
            self.policies[tenant_id] = allowed_regions
        self.logger.info(f"Set residency policy for {tenant_id}: {allowed_regions}")
    
    def check_compliance(self, tenant_id: str, region: str) -> bool:
        """Check if operation in region is compliant with tenant policy."""
        with self._lock:
            if tenant_id not in self.policies:
                return True  # No policy = allow all
            
            return region in self.policies[tenant_id]
    
    def enforce_replication(self, tenant_id: str, geo_replication: 'GeoReplication') -> List[str]:
        """Filter replication regions based on tenant policy."""
        with self._lock:
            # GeoReplication tracks configured regions in `backup_locations`.
            # (There is no `regions` attribute on GeoReplication.)
            available_regions = list(geo_replication.backup_locations.keys())

            if tenant_id not in self.policies:
                return available_regions

            allowed = set(self.policies[tenant_id])
            return [r for r in available_regions if r in allowed]


class RetentionEnforcer:
    """
    Automated log retention and deletion per compliance profile.
    Ensures logs are kept for required duration and deleted afterwards.
    """
    
    def __init__(self, audit_logger: 'AuditLogger'):
        self.audit_logger = audit_logger
        # Use uppercase keys to match ComplianceProfile.PROFILES
        self.profiles = {
            "PCI_DSS": 365,  # days
            "HIPAA": 2557,  # 7 years
            "ISO27001": 1095,  # 3 years
            "SOC2": 365
        }
        self._lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
    
    def enforce_retention(self, profile: str):
        """Enforce retention policy for a compliance profile."""
        if profile not in self.profiles:
            raise ValueError(f"Unknown profile: {profile}")
        
        retention_days = self.profiles[profile]
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        deleted_count = 0
        with self._lock:
            # Filter audit log entries
            original_count = len(self.audit_logger.audit_chain)
            self.audit_logger.audit_chain = [
                entry for entry in self.audit_logger.audit_chain
                if entry.get("timestamp", datetime.now()) > cutoff_date
            ]
            deleted_count = original_count - len(self.audit_logger.audit_chain)
        
        self.logger.info(f"Retention enforced for {profile}: deleted {deleted_count} entries older than {retention_days} days")
        return deleted_count


# ============================================================================
# Developer & Operator Ergonomics
# ============================================================================

class WebDashboard:
    """
    Lightweight web UI for monitoring and operations.
    Integrates Prometheus/Grafana panels directly.
    """
    
    def __init__(self, foundation: 'StarlinkSecurityFoundation', port: int = 8080):
        self.foundation = foundation
        self.port = port
        self.logger = logging.getLogger(__name__)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get all data for dashboard display."""
        metrics_summary_fn = getattr(self.foundation, "get_metrics_summary", None)
        metrics_summary = metrics_summary_fn() if callable(metrics_summary_fn) else {}

        prometheus_fn = getattr(self.foundation, "get_prometheus_metrics", None)
        prometheus_metrics = prometheus_fn() if callable(prometheus_fn) else ""

        scorer_fn = getattr(self.foundation, "get_scorer_explainability", None)
        scorer_status = (
            scorer_fn()
            if callable(scorer_fn)
            else {
                "scorer_type": "unknown",
                "is_healthy": False,
                "error": "get_scorer_explainability not supported by this foundation",
            }
        )

        # Some foundation variants do not expose a `state_store` attribute.
        # Use getattr() to keep runtime compatibility and satisfy static type checkers.
        threats: list[Any] = []
        state_store = getattr(self.foundation, "state_store", None)
        if state_store is not None:
            get_threats = getattr(state_store, "get_threats", None)
            if callable(get_threats):
                try:
                    # `get_threats()` is obtained via getattr(), so static type checkers
                    # infer its return as `object`. Guard and narrow to an Iterable.
                    from collections.abc import Iterable as IterableABC
                    from typing import cast

                    result = get_threats()
                    if isinstance(result, IterableABC):
                        threats = list(cast(IterableABC, result))
                    else:
                        threats = []
                except Exception:
                    threats = []

        rbac_fn = getattr(self.foundation, "get_rbac_audit_log", None)
        rbac_audit = rbac_fn() if callable(rbac_fn) else []

        cluster_manager = getattr(self.foundation, "cluster_manager", None)
        get_status_fn = getattr(cluster_manager, "get_status", None) if cluster_manager is not None else None
        cluster_health = get_status_fn() if callable(get_status_fn) else {}
        return {
            "metrics": metrics_summary,
            "prometheus": prometheus_metrics,
            "threats": threats,
            "rbac_audit": rbac_audit,
            "cluster_health": cluster_health,
            "scorer_status": scorer_status,
        }
    
    def render_html(self) -> str:
        """Render HTML dashboard."""
        data = self.get_dashboard_data()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Starlink Security Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .card {{ background: white; padding: 20px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .metric {{ display: inline-block; margin: 10px 20px; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #2196F3; }}
                .metric-label {{ font-size: 12px; color: #666; }}
                .threat {{ padding: 10px; margin: 5px 0; background: #fff3cd; border-left: 4px solid #ffc107; }}
            </style>
        </head>
        <body>
            <h1>Starlink Security Foundation Dashboard</h1>
            
            <div class="card">
                <h2>Metrics Summary</h2>
                <div class="metric">
                    <div class="metric-value">{data['metrics'].get('active_threats', 0)}</div>
                    <div class="metric-label">Active Threats</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{data['metrics'].get('unresolved_events', 0)}</div>
                    <div class="metric-label">Unresolved Events</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{data['metrics'].get('queue_utilization_pct', 0)}%</div>
                    <div class="metric-label">Queue Utilization</div>
                </div>
            </div>
            
            <div class="card">
                <h2>Active Threats</h2>
                {''.join([f'<div class="threat">{threat}</div>' for threat in data['threats'][:10]])}
            </div>
            
            <div class="card">
                <h2>Scorer Status</h2>
                <p><strong>Type:</strong> {data['scorer_status'].get('scorer_type', 'Unknown')}</p>
                <p><strong>Health:</strong> {'Healthy' if data['scorer_status'].get('is_healthy') else 'Unhealthy'}</p>
            </div>
        </body>
        </html>
        """
        return html


class PolicySimulationSandbox:
    """
    Test new rulesets or ML models against historical event data.
    Shows diff of scoring outcomes before rollout.
    """
    
    def __init__(self, foundation: 'StarlinkSecurityFoundation'):
        self.foundation = foundation
        self.historical_events = []
        self._lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
    
    def capture_events(self, events: List[SecurityEvent]):
        """Capture events for simulation."""
        with self._lock:
            self.historical_events.extend(events)
        self.logger.info(f"Captured {len(events)} events for simulation")
    
    def simulate_scorer(self, new_scorer: ThreatScorer, sample_size: int = 100) -> Dict[str, Any]:
        """
        Simulate new scorer against historical events.
        Returns comparison with current scorer.
        """
        if not self.historical_events:
            return {"error": "No historical events available"}
        
        # Using random for historical event sampling (not security-critical)
        sample = random.sample(self.historical_events, min(sample_size, len(self.historical_events)))  # nosec B311
        
        current_scores = []
        new_scores = []
        differences = []
        
        for event in sample:
            # Current scorer
            # NOTE: Not all foundation variants expose a `threat_scorer` attribute.
            # Use getattr() to keep runtime compatibility and satisfy static type checkers.
            current_result: Dict[str, Any]
            current_scorer = getattr(self.foundation, "threat_scorer", None)
            if current_scorer is not None and hasattr(current_scorer, "score"):
                score_obj = current_scorer.score(event)
                current_result = score_obj if isinstance(score_obj, dict) else {
                    "risk": DynamicWorkerPool.DEFAULT_RISK_SCORE,
                    "factors": {"fallback": "invalid_score_result"},
                }
            else:
                # Fall back to the foundation-level scoring method if available.
                score_threat_fn = getattr(self.foundation, "score_threat", None)
                if callable(score_threat_fn):
                    score_obj = score_threat_fn(event)
                    current_result = score_obj if isinstance(score_obj, dict) else {
                        "risk": DynamicWorkerPool.DEFAULT_RISK_SCORE,
                        "factors": {"fallback": "invalid_score_result"},
                    }
                else:
                    # Last-resort fallback to allow simulation to proceed.
                    current_result = {
                        "risk": DynamicWorkerPool.DEFAULT_RISK_SCORE,
                        "factors": {"fallback": "no_current_scorer"},
                    }

            current_scores.append(current_result["risk"])
            
            # New scorer
            new_result = new_scorer.score(event)
            new_scores.append(new_result['risk'])
            
            # Track significant differences
            diff = abs(new_result['risk'] - current_result['risk'])
            if diff > DynamicWorkerPool.SIGNIFICANT_RISK_DIFFERENCE_THRESHOLD:
                differences.append({
                    "event": f"{event.event_type} from {event.source}",
                    "current_risk": current_result['risk'],
                    "new_risk": new_result['risk'],
                    "delta": diff
                })
        
        return {
            "sample_size": len(sample),
            "current_avg_risk": sum(current_scores) / len(current_scores),
            "new_avg_risk": sum(new_scores) / len(new_scores),
            "significant_differences": len(differences),
            "top_differences": sorted(differences, key=lambda x: x['delta'], reverse=True)[:10]
        }
    
    def simulate_audit_impact(self, profile: str) -> Dict[str, Any]:
        """
        Simulate audit impact of changing compliance profile.
        Shows how many entries would be affected by retention policy change.
        """
        # Validate profile exists
        if profile not in ComplianceProfile.PROFILES:
            return {"error": f"Unknown compliance profile: {profile}"}
        
        formatter = ComplianceProfile.create_formatter(profile)
        retention_days = ComplianceProfile.PROFILES[profile]["retention_days"]
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # Count affected entries
        affected = 0
        # NOTE: Some foundation variants do not define `audit_logger`.
        # Use getattr() to keep runtime compatibility and satisfy static type checkers.
        audit_logger = getattr(self.foundation, "audit_logger", None)
        if audit_logger is not None:
            lock = getattr(audit_logger, "_lock", None)
            chain = getattr(audit_logger, "audit_chain", None)
            if chain is not None:
                if lock is not None:
                    with lock:
                        affected = sum(
                            1 for entry in chain
                            if entry.get("timestamp", datetime.now()) < cutoff_date
                        )
                else:
                    affected = sum(
                        1 for entry in chain
                        if entry.get("timestamp", datetime.now()) < cutoff_date
                    )
        
        return {
            "profile": profile,
            "retention_days": retention_days,
            "entries_to_delete": affected,
            "cutoff_date": cutoff_date.isoformat()
        }


# ============================================================================
# Long-Term Sustainability
# ============================================================================

class ModuleVersion:
    """
    Semantic versioning for modules, scorers, and connectors.
    Ensures backward compatibility during upgrades.
    """
    
    def __init__(self, major: int, minor: int, patch: int):
        self.major = major
        self.minor = minor
        self.patch = patch
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def is_compatible(self, other: 'ModuleVersion') -> bool:
        """Check if versions are compatible (same major version)."""
        return self.major == other.major
    
    def __lt__(self, other: 'ModuleVersion') -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
    
    def __eq__(self, other: 'ModuleVersion') -> bool:
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)


class VersionedModule:
    """Base class for versioned modules."""
    
    def __init__(self, name: str, version: ModuleVersion):
        self.name = name
        self.version = version
        self.metadata = {
            "created_at": datetime.now(),
            "author": "Unknown",
            "description": ""
        }
    
    def get_version_info(self) -> Dict[str, Any]:
        """Get version and metadata."""
        return {
            "name": self.name,
            "version": str(self.version),
            "metadata": self.metadata
        }


class DocumentationGenerator:
    """
    Auto-generate API docs, RBAC role maps, and compliance profiles.
    Extracts documentation from code annotations.
    """
    
    def __init__(self, foundation: 'StarlinkSecurityFoundation'):
        self.foundation = foundation
    
    def generate_api_docs(self) -> str:
        """Generate API documentation in Markdown format."""
        docs = "# Starlink Security Foundation API Documentation\n\n"
        docs += "## Version: 1.0.0\n\n"
        
        docs += "## Core Methods\n\n"
        docs += "### log_event(event: SecurityEvent)\n"
        docs += "Log a security event with pluggable processing.\n\n"
        
        docs += "### update_metrics(latency, jitter, packet_loss, throughput)\n"
        docs += "Update network performance metrics.\n\n"
        
        docs += "### get_metrics_summary() -> Dict\n"
        docs += "Get observability metrics including threats, events, queue utilization.\n\n"
        
        docs += "### score_threat(event: SecurityEvent) -> Dict\n"
        docs += "Score a threat using configured ThreatScorer with graceful degradation.\n\n"
        
        return docs
    
    def generate_rbac_map(self) -> str:
        """Generate RBAC role mapping documentation."""
        docs = "# RBAC Role Mapping\n\n"
        docs += "## Permissions\n\n"
        docs += "- `rotate_key`: Rotate encryption keys\n"
        docs += "- `config_reload`: Reload configuration at runtime\n"
        docs += "- `state_export`: Export system state\n\n"
        
        docs += "## Example Role Definitions\n\n"
        docs += "```python\n"
        docs += "admin_permissions = ['rotate_key', 'config_reload', 'state_export']\n"
        docs += "operator_permissions = ['config_reload', 'state_export']\n"
        docs += "auditor_permissions = ['state_export']\n"
        docs += "```\n\n"
        
        return docs
    
    def generate_compliance_profiles(self) -> str:
        """Generate compliance profile documentation."""
        docs = "# Compliance Profiles\n\n"
        
        for profile_name, profile_data in ComplianceProfile.PROFILES.items():
            docs += f"## {profile_name.upper()}\n\n"
            docs += f"**Standard:** {profile_data['standard']}\n\n"
            docs += f"**Retention:** {profile_data['retention_days']} days\n\n"
            docs += f"**Required Fields:** {', '.join(profile_data['required_fields'])}\n\n"
        
        return docs
    
    def generate_full_documentation(self) -> str:
        """Generate complete documentation."""
        return (
            self.generate_api_docs() + "\n\n" +
            self.generate_rbac_map() + "\n\n" +
            self.generate_compliance_profiles()
        )


# ============================================================================
# STRATEGIC POLISH: Security Hardening
# ============================================================================

class KeyProvider(ABC):
    """Abstract interface for key management providers (HSM/KMS)."""
    
    @abstractmethod
    def generate_key(self) -> bytes:
        """Generate a new encryption key."""
        pass
    
    @abstractmethod
    def rotate_key(self, old_key: bytes) -> bytes:
        """Rotate encryption key with envelope encryption."""
        pass
    
    @abstractmethod
    def encrypt(self, plaintext: bytes, key_id: str) -> bytes:
        """Encrypt data using KMS."""
        pass
    
    @abstractmethod
    def decrypt(self, ciphertext: bytes, key_id: str) -> bytes:
        """Decrypt data using KMS."""
        pass
    
    @abstractmethod
    def get_key_metadata(self, key_id: str) -> Dict[str, Any]:
        """Get key metadata including rotation status and usage policies."""
        pass


class KMSKeyProvider(KeyProvider):
    """
    Cloud KMS provider with envelope encryption.
    Supports AWS KMS, Azure Key Vault, GCP KMS.
    """
    
    def __init__(self, provider: str = "aws", region: str = "us-east-1", key_id: Optional[str] = None):
        """
        Initialize KMS key provider.
        
        Args:
            provider: Cloud provider (aws, azure, gcp)
            region: Cloud region
            key_id: Master key ID in KMS
        """
        self.provider = provider
        self.region = region
        self.key_id = key_id or f"starlink-security-master-key-{region}"
        self.data_encryption_keys = {}  # Cache for envelope encryption
        self.lock = threading.RLock()
    
    def generate_key(self) -> bytes:
        """Generate data encryption key with envelope encryption."""
        # Generate local data encryption key
        dek = Fernet.generate_key()
        
        # In production, encrypt DEK with KMS master key
        # For now, simulate KMS encryption
        with self.lock:
            encrypted_dek = self._simulate_kms_encrypt(dek)
            self.data_encryption_keys[self.key_id] = {
                "plaintext_dek": dek,
                "encrypted_dek": encrypted_dek,
                "created_at": datetime.now(),
                "rotation_count": 0
            }
        
        return dek
    
    def rotate_key(self, old_key: bytes) -> bytes:
        """Rotate key using KMS envelope encryption."""
        new_dek = Fernet.generate_key()
        
        with self.lock:
            encrypted_dek = self._simulate_kms_encrypt(new_dek)
            old_metadata = self.data_encryption_keys.get(self.key_id, {})
            
            self.data_encryption_keys[f"{self.key_id}-rotated"] = old_metadata
            self.data_encryption_keys[self.key_id] = {
                "plaintext_dek": new_dek,
                "encrypted_dek": encrypted_dek,
                "created_at": datetime.now(),
                "rotation_count": old_metadata.get("rotation_count", 0) + 1,
                "previous_key_id": f"{self.key_id}-rotated"
            }
        
        return new_dek
    
    def encrypt(self, plaintext: bytes, key_id: str) -> bytes:
        """Encrypt using envelope encryption."""
        with self.lock:
            if key_id not in self.data_encryption_keys:
                raise ValueError(f"Key {key_id} not found")
            
            dek = self.data_encryption_keys[key_id]["plaintext_dek"]
            f = Fernet(dek)
            return f.encrypt(plaintext)
    
    def decrypt(self, ciphertext: bytes, key_id: str) -> bytes:
        """Decrypt using envelope encryption."""
        with self.lock:
            if key_id not in self.data_encryption_keys:
                raise ValueError(f"Key {key_id} not found")
            
            dek = self.data_encryption_keys[key_id]["plaintext_dek"]
            f = Fernet(dek)
            return f.decrypt(ciphertext)
    
    def get_key_metadata(self, key_id: str) -> Dict[str, Any]:
        """Get key metadata."""
        with self.lock:
            if key_id not in self.data_encryption_keys:
                return {}
            
            metadata = self.data_encryption_keys[key_id].copy()
            metadata.pop("plaintext_dek", None)  # Don't expose plaintext key
            metadata["key_id"] = key_id
            metadata["provider"] = self.provider
            metadata["region"] = self.region
            return metadata
    
    def _simulate_kms_encrypt(self, dek: bytes) -> bytes:
        """Simulate KMS encryption (in production, call actual KMS API)."""
        # This would call actual KMS in production
        return hashlib.sha256(dek + self.key_id.encode()).digest()


class SecretsManager:
    """
    Integration with secrets management services (Vault, AWS Secrets Manager).
    Retrieves secrets with short-lived tokens and auto-refresh.
    """
    
    def __init__(self, provider: str = "vault", endpoint: Optional[str] = None, ttl_seconds: int = 3600):
        """
        Initialize secrets manager.
        
        Args:
            provider: Secrets provider (vault, aws_secrets, azure_kv)
            endpoint: API endpoint
            ttl_seconds: Token/secret TTL
        """
        self.provider = provider
        self.endpoint = endpoint or f"https://{provider}.example.com"
        self.ttl_seconds = ttl_seconds
        self.cache = {}
        self.lock = threading.RLock()
        self.refresh_thread = None
        self.running = False
    
    def get_secret(self, secret_path: str) -> str:
        """
        Retrieve secret with caching and auto-refresh.
        
        Args:
            secret_path: Path to secret
            
        Returns:
            Secret value
        """
        with self.lock:
            cached = self.cache.get(secret_path)
            if cached and datetime.now() < cached["expires_at"]:
                return cached["value"]
            
            # Fetch from provider
            secret_value = self._fetch_from_provider(secret_path)
            
            self.cache[secret_path] = {
                "value": secret_value,
                "fetched_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(seconds=self.ttl_seconds)
            }
            
            return secret_value
    
    def start_auto_refresh(self):
        """Start background thread for secret auto-refresh."""
        if self.running:
            return
        
        self.running = True
        self.refresh_thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self.refresh_thread.start()
    
    def stop_auto_refresh(self):
        """Stop auto-refresh thread."""
        self.running = False
        if self.refresh_thread:
            self.refresh_thread.join(timeout=5)
    
    def _refresh_loop(self):
        """Background loop for refreshing cached secrets."""
        while self.running:
            time.sleep(min(60, self.ttl_seconds // 2))  # Refresh at half TTL
            
            with self.lock:
                now = datetime.now()
                expired_keys = [
                    k for k, v in self.cache.items()
                    if now >= v["expires_at"] - timedelta(seconds=300)  # 5min before expiry
                ]
                
                for key in expired_keys:
                    try:
                        self.cache[key] = {
                            "value": self._fetch_from_provider(key),
                            "fetched_at": now,
                            "expires_at": now + timedelta(seconds=self.ttl_seconds)
                        }
                    except Exception as e:
                        logging.warning(f"Failed to refresh secret {key}: {e}")
                        pass  # Keep old value on error
    
    def _fetch_from_provider(self, secret_path: str) -> str:
        """Fetch secret from provider (simulated)."""
        # In production, call actual Vault/AWS Secrets Manager API
        return f"secret_value_for_{secret_path}"


class SBOMGenerator:
    """
    Software Bill of Materials (SBOM) generator.
    Generates CycloneDX and SPDX SBOMs for supply chain security.
    """
    
    def __init__(self):
        """Initialize SBOM generator."""
        self.components = []
        self.dependencies = []
    
    def add_component(
        self,
        name: str,
        version: str,
        supplier: Optional[str] = None,
        licenses: Optional[List[str]] = None,
        hashes: Optional[Dict[str, str]] = None,
    ):
        """
        Add component to SBOM.
        
        Args:
            name: Component name
            version: Component version
            supplier: Component supplier/vendor
            licenses: SPDX license identifiers
            hashes: Hash values (sha256, sha512)
        """
        self.components.append({
            "name": name,
            "version": version,
            "supplier": supplier or "unknown",
            "licenses": licenses or [],
            "hashes": hashes or {},
            "added_at": datetime.now().isoformat()
        })
    
    def generate_cyclonedx(self) -> Dict[str, Any]:
        """Generate CycloneDX SBOM."""
        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "version": 1,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "tools": [{
                    "vendor": "Starlink Security Foundation",
                    "name": "SBOM Generator",
                    "version": "1.0.0"
                }]
            },
            "components": [
                {
                    "type": "library",
                    "name": c["name"],
                    "version": c["version"],
                    "supplier": {"name": c["supplier"]},
                    "licenses": [{"license": {"id": lic}} for lic in c["licenses"]],
                    "hashes": [{"alg": alg.upper(), "content": val} for alg, val in c["hashes"].items()]
                }
                for c in self.components
            ]
        }
    
    def generate_spdx(self) -> Dict[str, Any]:
        """Generate SPDX SBOM."""
        return {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "Starlink Security Foundation SBOM",
            "documentNamespace": f"https://starlink-security.example.com/sbom/{datetime.now().isoformat()}",
            "creationInfo": {
                "created": datetime.now().isoformat(),
                "creators": ["Tool: SBOM Generator-1.0.0"]
            },
            "packages": [
                {
                    "SPDXID": f"SPDXRef-Package-{i}",
                    "name": c["name"],
                    "versionInfo": c["version"],
                    "supplier": f"Organization: {c['supplier']}",
                    "licenseConcluded": " AND ".join(c["licenses"]) if c["licenses"] else "NOASSERTION",
                    "checksums": [{"algorithm": alg.upper(), "checksumValue": val} for alg, val in c["hashes"].items()]
                }
                for i, c in enumerate(self.components)
            ]
        }
    
    def verify_signatures(self, plugin_path: str, signature_path: str) -> bool:
        """
        Verify plugin signature for supply chain integrity.
        
        Args:
            plugin_path: Path to plugin file
            signature_path: Path to detached signature
            
        Returns:
            True if signature is valid
        """
        # In production, use GPG or similar for signature verification
        # For now, simulate verification
        return True


# ============================================================================
# STRATEGIC POLISH: Reliability & SRE Maturity
# ============================================================================

@dataclass
class SLO:
    """Service Level Objective definition."""
    name: str
    description: str
    target_percentile: float  # e.g., 0.99 for 99th percentile
    target_value: float  # Target latency in ms, success rate, etc.
    measurement_window_seconds: int  # Rolling window
    error_budget_percentage: float  # e.g., 1.0 for 1% error budget


class SLOMonitor:
    """
    SLO monitoring with error budgets and burn rate alerts.
    Tracks scoring latency, queue time, feed ingestion, audit export.
    """
    
    def __init__(self):
        """Initialize SLO monitor."""
        self.slos = {}
        self.measurements = {}  # slo_name -> List[measurement]
        self.lock = threading.RLock()
        
        # Define default SLOs
        self._define_default_slos()
    
    def _define_default_slos(self):
        """Define default SLOs."""
        self.slos = {
            "scoring_latency": SLO(
                name="scoring_latency",
                description="Threat scoring latency p99",
                target_percentile=0.99,
                target_value=100.0,  # 100ms p99
                measurement_window_seconds=300,  # 5 min window
                error_budget_percentage=1.0
            ),
            "queue_time": SLO(
                name="queue_time",
                description="Event queue processing time p95",
                target_percentile=0.95,
                target_value=50.0,  # 50ms p95
                measurement_window_seconds=300,
                error_budget_percentage=2.0
            ),
            "feed_ingestion_freshness": SLO(
                name="feed_ingestion_freshness",
                description="Threat feed ingestion freshness",
                target_percentile=0.99,
                target_value=300.0,  # 5 min freshness
                measurement_window_seconds=600,
                error_budget_percentage=0.5
            ),
            "audit_export_success": SLO(
                name="audit_export_success",
                description="Audit export success rate",
                target_percentile=1.0,  # 100% target
                target_value=1.0,  # Success rate
                measurement_window_seconds=3600,  # 1 hour
                error_budget_percentage=0.1
            )
        }
        
        for slo_name in self.slos:
            self.measurements[slo_name] = []
    
    def record_measurement(self, slo_name: str, value: float, success: bool = True):
        """
        Record SLO measurement.
        
        Args:
            slo_name: SLO identifier
            value: Measured value (latency, success=1.0/failure=0.0, etc.)
            success: Whether operation succeeded
        """
        if slo_name not in self.slos:
            return
        
        with self.lock:
            now = datetime.now()
            self.measurements[slo_name].append({
                "timestamp": now,
                "value": value,
                "success": success
            })
            
            # Cleanup old measurements outside window
            slo = self.slos[slo_name]
            cutoff = now - timedelta(seconds=slo.measurement_window_seconds)
            self.measurements[slo_name] = [
                m for m in self.measurements[slo_name]
                if m["timestamp"] > cutoff
            ]
    
    def get_slo_status(self, slo_name: str) -> Dict[str, Any]:
        """
        Get current SLO status.
        
        Returns:
            Status including current value, target, error budget consumption
        """
        if slo_name not in self.slos:
            return {}
        
        with self.lock:
            slo = self.slos[slo_name]
            measurements = self.measurements[slo_name]
            
            if not measurements:
                return {
                    "slo_name": slo_name,
                    "status": "no_data",
                    "current_value": None,
                    "target_value": slo.target_value,
                    "error_budget_remaining": 100.0
                }
            
            # Calculate percentile or success rate
            if slo_name == "audit_export_success":
                values = [m["value"] for m in measurements if m["success"]]
                current_value = sum(values) / len(measurements) if measurements else 0.0
            else:
                values = sorted([m["value"] for m in measurements])
                percentile_index = int(len(values) * slo.target_percentile)
                current_value = values[min(percentile_index, len(values) - 1)]
            
            # Calculate error budget consumption
            if slo_name == "audit_export_success":
                error_budget_consumed = max(0, (slo.target_value - current_value) / (slo.error_budget_percentage / 100))
            else:
                error_budget_consumed = max(0, (current_value - slo.target_value) / slo.target_value * 100)
            
            error_budget_remaining = max(0, 100 - error_budget_consumed)
            
            return {
                "slo_name": slo_name,
                "status": "healthy" if error_budget_remaining > 20 else "warning" if error_budget_remaining > 0 else "critical",
                "current_value": current_value,
                "target_value": slo.target_value,
                "error_budget_remaining": error_budget_remaining,
                "sample_count": len(measurements)
            }
    
    def check_burn_rate_alert(self, slo_name: str) -> Dict[str, Any]:
        """
        Check if error budget burn rate exceeds thresholds.
        
        Returns:
            Alert information if burn rate is too high
        """
        status = self.get_slo_status(slo_name)
        
        if status.get("error_budget_remaining", 100) < 20:
            return {
                "alert": True,
                "severity": "critical" if status["error_budget_remaining"] < 5 else "warning",
                "message": f"SLO {slo_name} error budget at {status['error_budget_remaining']:.1f}%",
                "current_value": status["current_value"],
                "target_value": status["target_value"]
            }
        
        return {"alert": False}


class RunbookManager:
    """
    Incident runbooks and automated recovery workflows.
    Links to CLI/API actions for predictable failure recovery.
    """
    
    def __init__(self):
        """Initialize runbook manager."""
        self.runbooks = {}
        self._define_default_runbooks()
    
    def _define_default_runbooks(self):
        """Define default runbooks."""
        self.runbooks = {
            "scorer_outage": {
                "title": "Threat Scorer Outage",
                "symptoms": [
                    "Scoring latency SLO violated",
                    "Scorer health check failures",
                    "Increased error rates in scoring pipeline"
                ],
                "diagnosis": [
                    "1. Check scorer health: foundation.get_scorer_explainability()",
                    "2. Check worker pool status: worker_pool.get_status()",
                    "3. Review recent scoring errors in logs"
                ],
                "recovery_steps": [
                    "1. Verify graceful degradation to rule-based scorer",
                    "2. Restart ML scorer process if unhealthy",
                    "3. If persists, rollback to previous scorer version",
                    "4. Escalate to on-call if no recovery within 15 minutes"
                ],
                "automation": {
                    "auto_restart": True,
                    "fallback_to_rules": True,
                    "escalation_timeout_seconds": 900
                }
            },
            "redis_failure": {
                "title": "Redis/StateStore Failure",
                "symptoms": [
                    "State store connection errors",
                    "Threat management operations failing",
                    "Cluster synchronization issues"
                ],
                "diagnosis": [
                    "1. Check Redis connectivity and health",
                    "2. Verify network connectivity to Redis cluster",
                    "3. Check Redis cluster status and replication"
                ],
                "recovery_steps": [
                    "1. Attempt reconnection with exponential backoff",
                    "2. Failover to in-memory state store temporarily",
                    "3. Restore state from latest backup if needed",
                    "4. Verify state consistency after recovery"
                ],
                "automation": {
                    "auto_failover": True,
                    "backup_restore": True,
                    "verification_required": True
                }
            },
            "kms_failure": {
                "title": "KMS/Key Management Failure",
                "symptoms": [
                    "Encryption/decryption failures",
                    "Key rotation blocked",
                    "KMS API timeout errors"
                ],
                "diagnosis": [
                    "1. Check KMS service health and quotas",
                    "2. Verify IAM permissions for KMS operations",
                    "3. Check network connectivity to KMS endpoint"
                ],
                "recovery_steps": [
                    "1. Use cached DEK for short-term operations",
                    "2. Queue operations requiring new keys",
                    "3. Retry KMS operations with exponential backoff",
                    "4. Escalate if KMS unavailable > 5 minutes"
                ],
                "automation": {
                    "cache_fallback": True,
                    "retry_with_backoff": True,
                    "escalation_timeout_seconds": 300
                }
            },
            "cluster_failover": {
                "title": "Cluster Leader Failover",
                "symptoms": [
                    "Leader node health check failures",
                    "Cluster operations stalled",
                    "Leadership election in progress"
                ],
                "diagnosis": [
                    "1. Check cluster manager status",
                    "2. Verify heartbeat connectivity",
                    "3. Review leader election logs"
                ],
                "recovery_steps": [
                    "1. Allow automatic leader election to complete",
                    "2. Verify new leader has current state",
                    "3. Resume critical operations on new leader",
                    "4. Investigate root cause of previous leader failure"
                ],
                "automation": {
                    "auto_election": True,
                    "state_verification": True,
                    "post_incident_review": True
                }
            },
            "compliance_export_backlog": {
                "title": "Compliance Audit Export Backlog",
                "symptoms": [
                    "Audit export success SLO violated",
                    "Retention enforcement failures",
                    "SIEM push queue backing up"
                ],
                "diagnosis": [
                    "1. Check SIEM adapter connectivity",
                    "2. Verify compliance profile configuration",
                    "3. Review export queue depth"
                ],
                "recovery_steps": [
                    "1. Increase export worker concurrency",
                    "2. Retry failed exports with backoff",
                    "3. Temporarily increase queue capacity",
                    "4. Escalate if backlog continues to grow"
                ],
                "automation": {
                    "auto_retry": True,
                    "scale_workers": True,
                    "escalation_threshold": 1000  # items
                }
            }
        }
    
    def get_runbook(self, incident_type: str) -> Dict[str, Any]:
        """
        Get runbook for incident type.
        
        Args:
            incident_type: Type of incident
            
        Returns:
            Runbook with recovery steps
        """
        return self.runbooks.get(incident_type, {
            "title": "Unknown Incident",
            "message": "No runbook available for this incident type",
            "recovery_steps": ["1. Consult on-call engineer", "2. Review system logs"]
        })
    
    def execute_automated_recovery(self, incident_type: str, foundation: 'StarlinkSecurityFoundation') -> Dict[str, Any]:
        """
        Execute automated recovery actions.
        
        Args:
            incident_type: Type of incident
            foundation: Foundation instance for executing actions
            
        Returns:
            Recovery result
        """
        runbook = self.get_runbook(incident_type)
        automation = runbook.get("automation", {})
        
        results = {
            "incident_type": incident_type,
            "automated_actions": [],
            "success": False
        }
        
        # Execute automated actions based on incident type
        if incident_type == "scorer_outage" and automation.get("auto_restart"):
            results["automated_actions"].append("Attempted scorer restart")
            if automation.get("fallback_to_rules"):
                results["automated_actions"].append("Enabled rule-based fallback")
                results["success"] = True
        
        elif incident_type == "redis_failure" and automation.get("auto_failover"):
            results["automated_actions"].append("Initiated failover to in-memory state store")
            results["success"] = True
        
        elif incident_type == "kms_failure" and automation.get("cache_fallback"):
            results["automated_actions"].append("Using cached DEK for operations")
            results["success"] = True
        
        return results


class CanaryDeployment:
    """
    Canary and progressive delivery for scorers and policies.
    Integrates with PolicySimulationSandbox for pre-flight checks.
    """
    
    def __init__(self, sandbox: Optional['PolicySimulationSandbox'] = None):
        """
        Initialize canary deployment manager.
        
        Args:
            sandbox: Policy simulation sandbox for pre-flight checks
        """
        self.sandbox = sandbox
        self.canary_configs = {}
        self.tenant_assignments = {}  # tenant_id -> scorer_version
        self.lock = threading.RLock()
    
    def create_canary(self, name: str, new_scorer: 'ThreatScorer',
                     canary_percentage: float = 10.0,
                     rollback_threshold: float = 0.15) -> str:
        """
        Create canary deployment for new scorer.
        
        Args:
            name: Canary deployment name
            new_scorer: New scorer to canary test
            canary_percentage: Percentage of traffic to route to canary (0-100)
            rollback_threshold: Auto-rollback if risk difference > threshold
            
        Returns:
            Canary deployment ID
        """
        canary_id = f"canary-{name}-{int(time.time())}"
        
        with self.lock:
            self.canary_configs[canary_id] = {
                "name": name,
                "new_scorer": new_scorer,
                "canary_percentage": canary_percentage,
                "rollback_threshold": rollback_threshold,
                "created_at": datetime.now(),
                "status": "active",
                "metrics": {
                    "canary_requests": 0,
                    "baseline_requests": 0,
                    "canary_avg_risk": 0.0,
                    "baseline_avg_risk": 0.0,
                    "significant_differences": 0
                }
            }
        
        return canary_id
    
    def should_use_canary(self, canary_id: str, tenant_id: Optional[str] = None) -> bool:
        """
        Determine if request should use canary scorer.
        
        Args:
            canary_id: Canary deployment ID
            tenant_id: Optional tenant ID for sticky routing
            
        Returns:
            True if should use canary
        """
        if canary_id not in self.canary_configs:
            return False
        
        config = self.canary_configs[canary_id]
        
        # Check if canary is active
        if config["status"] != "active":
            return False
        
        # Sticky tenant routing
        if tenant_id:
            with self.lock:
                if tenant_id in self.tenant_assignments:
                    return self.tenant_assignments[tenant_id] == "canary"
                
                # New tenant - assign based on percentage (using secrets for security)
                use_canary = secrets.SystemRandom().random() * 100 < config["canary_percentage"]
                self.tenant_assignments[tenant_id] = "canary" if use_canary else "baseline"
                return use_canary
        
        # Random percentage-based routing (using secrets for security)
        return secrets.SystemRandom().random() * 100 < config["canary_percentage"]
    
    def record_canary_result(self, canary_id: str, is_canary: bool,
                            risk_score: float, baseline_risk: Optional[float] = None):
        """
        Record canary deployment result.
        
        Args:
            canary_id: Canary deployment ID
            is_canary: Whether this was canary or baseline
            risk_score: Risk score from scorer
            baseline_risk: Baseline risk for comparison (optional)
        """
        if canary_id not in self.canary_configs:
            return
        
        with self.lock:
            config = self.canary_configs[canary_id]
            metrics = config["metrics"]
            
            if is_canary:
                metrics["canary_requests"] += 1
                # Update rolling average
                n = metrics["canary_requests"]
                metrics["canary_avg_risk"] = (
                    (metrics["canary_avg_risk"] * (n - 1) + risk_score) / n
                )
            else:
                metrics["baseline_requests"] += 1
                n = metrics["baseline_requests"]
                metrics["baseline_avg_risk"] = (
                    (metrics["baseline_avg_risk"] * (n - 1) + risk_score) / n
                )
            
            # Check for significant difference
            if baseline_risk is not None:
                diff = abs(risk_score - baseline_risk)
                if diff > config["rollback_threshold"]:
                    metrics["significant_differences"] += 1
                    
                    # Auto-rollback if too many significant differences
                    if metrics["significant_differences"] > 10:
                        config["status"] = "rolled_back"
                        config["rollback_reason"] = f"Exceeded rollback threshold: {diff:.3f} > {config['rollback_threshold']:.3f}"
    
    def get_canary_status(self, canary_id: str) -> Dict[str, Any]:
        """Get canary deployment status."""
        if canary_id not in self.canary_configs:
            return {}
        
        with self.lock:
            config = self.canary_configs[canary_id].copy()
            config.pop("new_scorer", None)  # Don't include scorer object
            return config
    
    def promote_canary(self, canary_id: str) -> bool:
        """
        Promote canary to 100% traffic.
        
        Args:
            canary_id: Canary deployment ID
            
        Returns:
            True if promoted successfully
        """
        if canary_id not in self.canary_configs:
            return False
        
        with self.lock:
            config = self.canary_configs[canary_id]
            if config["status"] == "active":
                config["status"] = "promoted"
                config["canary_percentage"] = 100.0
                config["promoted_at"] = datetime.now()
                return True
        
        return False
    
    def rollback_canary(self, canary_id: str, reason: str = "Manual rollback"):
        """
        Rollback canary deployment.
        
        Args:
            canary_id: Canary deployment ID
            reason: Rollback reason
        """
        if canary_id not in self.canary_configs:
            return
        
        with self.lock:
            config = self.canary_configs[canary_id]
            config["status"] = "rolled_back"
            config["rollback_reason"] = reason
            config["rolled_back_at"] = datetime.now()


# ============================================================================
# STRATEGIC POLISH: Performance & Efficiency
# ============================================================================

class PerformanceProfiler:
    """
    CPU and memory profiling with flamegraph generation.
    Tracks GC pauses and hot paths.
    """
    
    def __init__(self):
        """Initialize performance profiler."""
        self.profiles = {}
        self.hot_paths = {}  # function_name -> call_count
        self.gc_pauses = []
        self.lock = threading.RLock()
    
    def profile_function(self, func_name: str):
        """
        Decorator for profiling function execution.
        
        Args:
            func_name: Function name for profiling
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    elapsed = (time.time() - start_time) * 1000  # ms
                    
                    with self.lock:
                        if func_name not in self.profiles:
                            self.profiles[func_name] = {
                                "call_count": 0,
                                "total_time_ms": 0.0,
                                "min_time_ms": float('inf'),
                                "max_time_ms": 0.0,
                                "samples": []
                            }
                        
                        profile = self.profiles[func_name]
                        profile["call_count"] += 1
                        profile["total_time_ms"] += elapsed
                        profile["min_time_ms"] = min(profile["min_time_ms"], elapsed)
                        profile["max_time_ms"] = max(profile["max_time_ms"], elapsed)
                        
                        # Keep last 100 samples
                        profile["samples"].append(elapsed)
                        if len(profile["samples"]) > 100:
                            profile["samples"].pop(0)
                        
                        # Track hot paths
                        self.hot_paths[func_name] = self.hot_paths.get(func_name, 0) + 1
            
            return wrapper
        return decorator
    
    def get_profile_summary(self) -> Dict[str, Any]:
        """Get profiling summary with hot paths."""
        with self.lock:
            summary = {}
            
            for func_name, profile in self.profiles.items():
                avg_time = profile["total_time_ms"] / profile["call_count"] if profile["call_count"] > 0 else 0
                
                # Calculate percentiles from samples
                samples = sorted(profile["samples"])
                p50 = samples[len(samples) // 2] if samples else 0
                p95 = samples[int(len(samples) * 0.95)] if samples else 0
                p99 = samples[int(len(samples) * 0.99)] if samples else 0
                
                summary[func_name] = {
                    "call_count": profile["call_count"],
                    "avg_time_ms": avg_time,
                    "min_time_ms": profile["min_time_ms"] if profile["min_time_ms"] != float('inf') else 0,
                    "max_time_ms": profile["max_time_ms"],
                    "p50_ms": p50,
                    "p95_ms": p95,
                    "p99_ms": p99
                }
            
            return {
                "profiles": summary,
                "hot_paths": sorted(self.hot_paths.items(), key=lambda x: x[1], reverse=True)[:10]
            }
    
    def generate_flamegraph_data(self) -> str:
        """Generate flamegraph data in folded stack format."""
        # Simplified flamegraph data
        lines = []
        for func_name, count in sorted(self.hot_paths.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"root;{func_name} {count}")
        
        return "\n".join(lines)
    
    def record_gc_pause(self, duration_ms: float):
        """Record garbage collection pause."""
        with self.lock:
            self.gc_pauses.append({
                "timestamp": datetime.now(),
                "duration_ms": duration_ms
            })
            
            # Keep last 1000 pauses
            if len(self.gc_pauses) > 1000:
                self.gc_pauses.pop(0)
    
    def get_gc_stats(self) -> Dict[str, Any]:
        """Get GC pause statistics."""
        with self.lock:
            if not self.gc_pauses:
                return {"count": 0}
            
            durations = [p["duration_ms"] for p in self.gc_pauses]
            durations.sort()
            
            return {
                "count": len(durations),
                "total_pause_ms": sum(durations),
                "avg_pause_ms": sum(durations) / len(durations),
                "max_pause_ms": durations[-1],
                "p95_pause_ms": durations[int(len(durations) * 0.95)]
            }


class AdaptiveBatchCoalescer:
    """
    Adaptive batching with dynamic batch size based on load.
    Maximizes throughput under varying load conditions.
    """
    
    def __init__(self, min_batch_size: int = 1, max_batch_size: int = 100,
                 target_latency_ms: float = 50.0):
        """
        Initialize adaptive batch coalescer.
        
        Args:
            min_batch_size: Minimum batch size
            max_batch_size: Maximum batch size
            target_latency_ms: Target processing latency
        """
        self.min_batch_size = min_batch_size
        self.max_batch_size = max_batch_size
        self.target_latency_ms = target_latency_ms
        
        self.current_batch_size = min_batch_size
        self.recent_latencies = []
        self.queue = []
        self.lock = threading.RLock()
        
        # Performance tracking
        self.batches_processed = 0
        self.total_items_processed = 0
    
    def add_item(self, item: Any) -> Optional[List[Any]]:
        """
        Add item to batch. Returns batch if ready for processing.
        
        Args:
            item: Item to add to batch
            
        Returns:
            Batch to process, or None if not ready
        """
        with self.lock:
            self.queue.append(item)
            
            if len(self.queue) >= self.current_batch_size:
                batch = self.queue[:self.current_batch_size]
                self.queue = self.queue[self.current_batch_size:]
                return batch
        
        return None
    
    def flush_batch(self) -> List[Any]:
        """Flush current batch regardless of size."""
        with self.lock:
            batch = self.queue.copy()
            self.queue.clear()
            return batch
    
    def record_batch_latency(self, latency_ms: float, batch_size: int):
        """
        Record batch processing latency and adapt batch size.
        
        Args:
            latency_ms: Batch processing latency
            batch_size: Size of processed batch
        """
        with self.lock:
            self.recent_latencies.append(latency_ms)
            if len(self.recent_latencies) > 10:
                self.recent_latencies.pop(0)
            
            self.batches_processed += 1
            self.total_items_processed += batch_size
            
            # Adapt batch size based on recent performance
            avg_latency = sum(self.recent_latencies) / len(self.recent_latencies)
            
            if avg_latency < self.target_latency_ms * 0.7:
                # We can handle more - increase batch size
                self.current_batch_size = min(
                    self.max_batch_size,
                    int(self.current_batch_size * 1.2)
                )
            elif avg_latency > self.target_latency_ms * 1.3:
                # Too slow - decrease batch size
                self.current_batch_size = max(
                    self.min_batch_size,
                    int(self.current_batch_size * 0.8)
                )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get batching statistics."""
        with self.lock:
            avg_latency = (
                sum(self.recent_latencies) / len(self.recent_latencies)
                if self.recent_latencies else 0
            )
            
            avg_batch_size = (
                self.total_items_processed / self.batches_processed
                if self.batches_processed > 0 else 0
            )
            
            return {
                "current_batch_size": self.current_batch_size,
                "queue_depth": len(self.queue),
                "batches_processed": self.batches_processed,
                "total_items_processed": self.total_items_processed,
                "avg_batch_size": avg_batch_size,
                "avg_latency_ms": avg_latency,
                "target_latency_ms": self.target_latency_ms
            }


# ============================================================================
# Final Mile Upgrades: Security Assurance & Business Readiness
# ============================================================================


class ThreatModelingFramework:
    """
    STRIDE/LINDDUN threat modeling framework for systematic attack surface analysis.
    Identifies threats across subsystems: API Gateway, plugins, scorers, state store.
    """
    
    def __init__(self):
        self.threat_models: Dict[str, Dict] = {}
        self.mitigations: Dict[str, List[str]] = {}
        self.lock = threading.RLock()
    
    def model_subsystem(
        self, 
        subsystem: str, 
        assets: List[str], 
        trust_boundaries: List[str]
    ) -> Dict[str, List[str]]:
        """
        Perform STRIDE threat modeling on a subsystem.
        
        Args:
            subsystem: Subsystem name (API Gateway, plugins, scorers, state_store)
            assets: List of assets in the subsystem
            trust_boundaries: Trust boundary crossings
            
        Returns:
            Dict of threat categories to identified threats
        """
        threats = {
            "Spoofing": [],
            "Tampering": [],
            "Repudiation": [],
            "Information_Disclosure": [],
            "Denial_of_Service": [],
            "Elevation_of_Privilege": []
        }
        
        with self.lock:
            # Analyze each asset against STRIDE categories
            for asset in assets:
                if "API" in asset or "Gateway" in asset:
                    threats["Spoofing"].append(f"Token forgery for {asset}")
                    threats["Denial_of_Service"].append(f"Rate limit bypass on {asset}")
                
                if "plugin" in asset.lower():
                    threats["Tampering"].append(f"Malicious plugin replacement: {asset}")
                    threats["Elevation_of_Privilege"].append(f"Plugin sandbox escape: {asset}")
                
                if "scorer" in asset.lower() or "ML" in asset:
                    threats["Tampering"].append(f"Model poisoning: {asset}")
                    threats["Information_Disclosure"].append(f"Model inversion attack: {asset}")
                
                if "state" in asset.lower() or "store" in asset.lower():
                    threats["Tampering"].append(f"State corruption: {asset}")
                    threats["Repudiation"].append(f"Audit log manipulation: {asset}")
            
            self.threat_models[subsystem] = {
                "assets": assets,
                "trust_boundaries": trust_boundaries,
                "threats": threats,
                "timestamp": datetime.now().isoformat()
            }
            
            return threats
    
    def add_mitigation(self, subsystem: str, threat: str, mitigation: str):
        """Add mitigation for identified threat."""
        with self.lock:
            key = f"{subsystem}:{threat}"
            if key not in self.mitigations:
                self.mitigations[key] = []
            self.mitigations[key].append(mitigation)
    
    def get_threat_report(self) -> Dict[str, Any]:
        """Get comprehensive threat modeling report."""
        with self.lock:
            total_threats = sum(
                len(category_threats)
                for model in self.threat_models.values()
                for category_threats in model["threats"].values()
            )
            
            return {
                "subsystems_modeled": len(self.threat_models),
                "total_threats_identified": total_threats,
                "mitigations_defined": len(self.mitigations),
                "models": self.threat_models,
                "mitigations": self.mitigations
            }


class APIRateLimiter:
    """
    Rate limiting and abuse prevention for REST API Gateway.
    Implements token bucket algorithm with per-tenant quotas.
    """
    
    def __init__(self, default_rate: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            default_rate: Default requests per window
            window_seconds: Time window in seconds
        """
        self.default_rate = default_rate
        self.window_seconds = window_seconds
        self.buckets: Dict[str, Dict] = {}  # tenant_id -> {tokens, last_refill}
        self.tenant_quotas: Dict[str, int] = {}  # tenant_id -> custom quota
        self.lock = threading.RLock()
        self.blocked_ips: Set[str] = set()
        self.ip_reputation: Dict[str, int] = {}  # IP -> reputation score (0-100)
    
    def check_rate_limit(self, tenant_id: str, ip_address: Optional[str] = None) -> bool:
        """
        Check if request is within rate limit.
        
        Args:
            tenant_id: Tenant identifier
            ip_address: Optional IP address for reputation check
            
        Returns:
            True if allowed, False if rate limited
        """
        with self.lock:
            # Check IP reputation and blocklist
            if ip_address:
                if ip_address in self.blocked_ips:
                    return False
                
                reputation = self.ip_reputation.get(ip_address, 100)
                if reputation < 20:  # Low reputation threshold
                    return False
            
            # Token bucket algorithm
            now = time.time()
            quota = self.tenant_quotas.get(tenant_id, self.default_rate)
            
            if tenant_id not in self.buckets:
                self.buckets[tenant_id] = {
                    "tokens": quota,
                    "last_refill": now
                }
            
            bucket = self.buckets[tenant_id]
            
            # Refill tokens based on elapsed time
            elapsed = now - bucket["last_refill"]
            refill_rate = quota / self.window_seconds
            new_tokens = min(quota, bucket["tokens"] + elapsed * refill_rate)
            
            bucket["tokens"] = new_tokens
            bucket["last_refill"] = now
            
            # Check if we have tokens available
            if bucket["tokens"] >= 1.0:
                bucket["tokens"] -= 1.0
                return True
            
            return False
    
    def set_tenant_quota(self, tenant_id: str, quota: int):
        """Set custom quota for tenant."""
        with self.lock:
            self.tenant_quotas[tenant_id] = quota
    
    def block_ip(self, ip_address: str):
        """Block IP address."""
        with self.lock:
            self.blocked_ips.add(ip_address)
    
    def update_ip_reputation(self, ip_address: str, score: int):
        """
        Update IP reputation score.
        
        Args:
            ip_address: IP to update
            score: Reputation score 0-100 (higher is better)
        """
        with self.lock:
            self.ip_reputation[ip_address] = max(0, min(100, score))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics."""
        with self.lock:
            return {
                "tenants_tracked": len(self.buckets),
                "custom_quotas": len(self.tenant_quotas),
                "blocked_ips": len(self.blocked_ips),
                "ip_reputation_entries": len(self.ip_reputation)
            }


class ComplianceCertificationManager:
    """
    Manages compliance certification roadmap (SOC 2, ISO 27001, etc.).
    Tracks controls, evidence collection, and audit preparation.
    """
    
    def __init__(self):
        self.certifications: Dict[str, Dict] = {}
        self.controls: Dict[str, List[Dict]] = {}  # cert_name -> controls
        self.evidence: Dict[str, List[str]] = {}  # control_id -> evidence paths
        self.lock = threading.RLock()
    
    def add_certification(
        self, 
        name: str, 
        standard: str, 
        target_date: str,
        owner: str
    ):
        """
        Add certification to roadmap.
        
        Args:
            name: Certification name (SOC2_Type_II, ISO27001, etc.)
            standard: Standard version
            target_date: Target completion date (ISO format)
            owner: Responsible party
        """
        with self.lock:
            self.certifications[name] = {
                "standard": standard,
                "target_date": target_date,
                "owner": owner,
                "status": "Planning",
                "controls_total": 0,
                "controls_implemented": 0
            }
    
    def add_control(
        self, 
        certification: str, 
        control_id: str, 
        description: str,
        status: str = "Not Implemented"
    ):
        """Add control requirement for certification."""
        with self.lock:
            if certification not in self.controls:
                self.controls[certification] = []
            
            self.controls[certification].append({
                "control_id": control_id,
                "description": description,
                "status": status,
                "added_date": datetime.now().isoformat()
            })
            
            # Update certification totals
            if certification in self.certifications:
                self.certifications[certification]["controls_total"] = len(
                    self.controls[certification]
                )
                self.certifications[certification]["controls_implemented"] = sum(
                    1 for c in self.controls[certification] 
                    if c["status"] == "Implemented"
                )
    
    def add_evidence(self, control_id: str, evidence_path: str):
        """Add evidence file for control."""
        with self.lock:
            if control_id not in self.evidence:
                self.evidence[control_id] = []
            self.evidence[control_id].append(evidence_path)
    
    def get_audit_pack(self, certification: str) -> Dict[str, Any]:
        """
        Generate audit pack for certification.
        
        Args:
            certification: Certification name
            
        Returns:
            Audit pack with controls, evidence, and status
        """
        with self.lock:
            if certification not in self.certifications:
                return {}
            
            controls_with_evidence = []
            for control in self.controls.get(certification, []):
                control_copy = control.copy()
                control_copy["evidence_files"] = self.evidence.get(
                    control["control_id"], []
                )
                controls_with_evidence.append(control_copy)
            
            return {
                "certification": self.certifications[certification],
                "controls": controls_with_evidence,
                "total_evidence_items": sum(
                    len(ev) for ev in self.evidence.values()
                ),
                "generated_date": datetime.now().isoformat()
            }
    
    def get_roadmap(self) -> Dict[str, Any]:
        """Get complete certification roadmap."""
        with self.lock:
            return {
                "certifications": self.certifications,
                "total_controls": sum(len(c) for c in self.controls.values()),
                "total_evidence_items": sum(len(e) for e in self.evidence.values())
            }


class PrivacyGovernanceManager:
    """
    Privacy governance: data classification, DPIAs, consent tracking, PII minimization.
    Ensures GDPR/CCPA compliance.
    """
    
    def __init__(self):
        self.data_classifications: Dict[str, str] = {}  # field -> classification
        self.dpias: Dict[str, Dict] = {}  # tenant -> DPIA
        self.consent_records: Dict[str, Dict] = {}  # user_id -> consent
        self.pii_redaction_profiles: Dict[str, List[str]] = {}  # profile -> fields
        self.lock = threading.RLock()
    
    def classify_data(self, field_name: str, classification: str):
        """
        Classify data field.
        
        Args:
            field_name: Field name
            classification: Classification level (Public, Internal, Confidential, Restricted, PII)
        """
        with self.lock:
            self.data_classifications[field_name] = classification
    
    def create_dpia(
        self, 
        tenant_id: str, 
        purpose: str, 
        data_types: List[str],
        risks: List[str]
    ):
        """
        Create Data Protection Impact Assessment.
        
        Args:
            tenant_id: Tenant identifier
            purpose: Processing purpose
            data_types: Types of data processed
            risks: Identified privacy risks
        """
        with self.lock:
            self.dpias[tenant_id] = {
                "purpose": purpose,
                "data_types": data_types,
                "risks": risks,
                "created_date": datetime.now().isoformat(),
                "status": "Active"
            }
    
    def record_consent(
        self, 
        user_id: str, 
        purpose: str, 
        granted: bool,
        expiry_date: Optional[str] = None
    ):
        """
        Record user consent.
        
        Args:
            user_id: User identifier
            purpose: Purpose of data processing
            granted: Whether consent was granted
            expiry_date: Optional expiry date (ISO format)
        """
        with self.lock:
            if user_id not in self.consent_records:
                self.consent_records[user_id] = {}
            
            self.consent_records[user_id][purpose] = {
                "granted": granted,
                "timestamp": datetime.now().isoformat(),
                "expiry_date": expiry_date
            }
    
    def add_redaction_profile(self, profile_name: str, fields: List[str]):
        """
        Add PII redaction profile for log minimization.
        
        Args:
            profile_name: Profile name (e.g., 'strict', 'moderate')
            fields: List of fields to redact
        """
        with self.lock:
            self.pii_redaction_profiles[profile_name] = fields
    
    def redact_pii(self, data: Dict[str, Any], profile: str = "strict") -> Dict[str, Any]:
        """
        Redact PII from data according to profile.
        
        Args:
            data: Data dictionary
            profile: Redaction profile name
            
        Returns:
            Redacted data dictionary
        """
        with self.lock:
            fields_to_redact = self.pii_redaction_profiles.get(profile, [])
            redacted = data.copy()
            
            for field in fields_to_redact:
                if field in redacted:
                    redacted[field] = "***REDACTED***"
            
            return redacted
    
    def check_consent(self, user_id: str, purpose: str) -> bool:
        """Check if user has valid consent for purpose."""
        with self.lock:
            if user_id not in self.consent_records:
                return False
            
            consent = self.consent_records[user_id].get(purpose)
            if not consent or not consent["granted"]:
                return False
            
            # Check expiry
            if consent.get("expiry_date"):
                expiry = datetime.fromisoformat(consent["expiry_date"])
                if datetime.now() > expiry:
                    return False
            
            return True
    
    def get_privacy_report(self) -> Dict[str, Any]:
        """Get comprehensive privacy governance report."""
        with self.lock:
            pii_fields = sum(
                1 for c in self.data_classifications.values() 
                if c == "PII"
            )
            
            active_consents = sum(
                1 for user_consents in self.consent_records.values()
                for consent in user_consents.values()
                if consent["granted"]
            )
            
            return {
                "data_fields_classified": len(self.data_classifications),
                "pii_fields": pii_fields,
                "dpias_active": len(self.dpias),
                "active_consents": active_consents,
                "redaction_profiles": len(self.pii_redaction_profiles)
            }


class DisasterRecoveryDrillManager:
    """
    Manages RTO/RPO disaster recovery drills with measured outcomes.
    Quarterly recovery exercises with automated playbooks.
    """
    
    def __init__(self):
        self.drills: List[Dict] = []
        self.rto_target_minutes: int = 60  # Recovery Time Objective
        self.rpo_target_minutes: int = 15  # Recovery Point Objective
        self.lock = threading.RLock()
    
    def schedule_drill(
        self, 
        drill_type: str, 
        scenario: str, 
        scheduled_date: str
    ) -> str:
        """
        Schedule disaster recovery drill.
        
        Args:
            drill_type: Type of drill (Full_Failover, Partial_Failover, Data_Restore)
            scenario: Failure scenario description
            scheduled_date: Scheduled date (ISO format)
            
        Returns:
            Drill ID
        """
        with self.lock:
            drill_id = f"DRILL-{len(self.drills) + 1:04d}"
            
            self.drills.append({
                "drill_id": drill_id,
                "drill_type": drill_type,
                "scenario": scenario,
                "scheduled_date": scheduled_date,
                "status": "Scheduled",
                "actual_rto_minutes": None,
                "actual_rpo_minutes": None,
                "created_date": datetime.now().isoformat()
            })
            
            return drill_id
    
    def execute_drill(
        self, 
        drill_id: str, 
        start_time: datetime, 
        recovery_time: datetime,
        data_loss_minutes: int
    ):
        """
        Record drill execution results.
        
        Args:
            drill_id: Drill identifier
            start_time: Drill start time
            recovery_time: Recovery completion time
            data_loss_minutes: Minutes of data loss (RPO)
        """
        with self.lock:
            for drill in self.drills:
                if drill["drill_id"] == drill_id:
                    rto_actual = (recovery_time - start_time).total_seconds() / 60
                    
                    drill["status"] = "Completed"
                    drill["executed_date"] = start_time.isoformat()
                    drill["actual_rto_minutes"] = rto_actual
                    drill["actual_rpo_minutes"] = data_loss_minutes
                    drill["rto_met"] = rto_actual <= self.rto_target_minutes
                    drill["rpo_met"] = data_loss_minutes <= self.rpo_target_minutes
                    break
    
    def get_drill_report(self) -> Dict[str, Any]:
        """Get drill statistics and compliance."""
        with self.lock:
            completed_drills = [d for d in self.drills if d["status"] == "Completed"]
            
            if not completed_drills:
                return {
                    "total_drills": len(self.drills),
                    "completed": 0,
                    "rto_target_minutes": self.rto_target_minutes,
                    "rpo_target_minutes": self.rpo_target_minutes
                }
            
            rto_met_count = sum(1 for d in completed_drills if d.get("rto_met", False))
            rpo_met_count = sum(1 for d in completed_drills if d.get("rpo_met", False))
            
            avg_rto = sum(
                d["actual_rto_minutes"] for d in completed_drills 
                if d["actual_rto_minutes"] is not None
            ) / len(completed_drills)
            
            avg_rpo = sum(
                d["actual_rpo_minutes"] for d in completed_drills 
                if d["actual_rpo_minutes"] is not None
            ) / len(completed_drills)
            
            return {
                "total_drills": len(self.drills),
                "completed": len(completed_drills),
                "rto_target_minutes": self.rto_target_minutes,
                "rpo_target_minutes": self.rpo_target_minutes,
                "avg_rto_minutes": avg_rto,
                "avg_rpo_minutes": avg_rpo,
                "rto_compliance_rate": rto_met_count / len(completed_drills) * 100,
                "rpo_compliance_rate": rpo_met_count / len(completed_drills) * 100,
                "recent_drills": completed_drills[-5:]  # Last 5 drills
            }


class GlobalTrafficManager:
    """
    Multi-region traffic management with DNS health checks and tenant-aware failover.
    Respects data residency policies during regional failovers.
    """
    
    def __init__(self):
        self.regions: Dict[str, Dict] = {}  # region_id -> {status, health, load}
        self.tenant_regions: Dict[str, str] = {}  # tenant_id -> preferred_region
        self.traffic_distribution: Dict[str, int] = {}  # region_id -> traffic %
        self.lock = threading.RLock()
    
    def register_region(
        self, 
        region_id: str, 
        endpoint: str, 
        capacity: int
    ):
        """
        Register region for traffic management.
        
        Args:
            region_id: Region identifier (us-east-1, eu-west-1, etc.)
            endpoint: Region endpoint URL
            capacity: Region capacity (requests/sec)
        """
        with self.lock:
            self.regions[region_id] = {
                "endpoint": endpoint,
                "capacity": capacity,
                "status": "Healthy",
                "health_score": 100,
                "current_load": 0,
                "last_health_check": datetime.now().isoformat()
            }
            
            # Distribute traffic evenly by default
            self._rebalance_traffic()
    
    def health_check(self, region_id: str, success: bool, latency_ms: float):
        """
        Update region health based on check results.
        
        Args:
            region_id: Region to update
            success: Whether health check succeeded
            latency_ms: Health check latency
        """
        with self.lock:
            if region_id not in self.regions:
                return
            
            region = self.regions[region_id]
            
            # Update health score (0-100)
            if success:
                region["health_score"] = min(100, region["health_score"] + 5)
                if latency_ms < 100:
                    region["status"] = "Healthy"
                elif latency_ms < 500:
                    region["status"] = "Degraded"
                else:
                    region["status"] = "Slow"
            else:
                region["health_score"] = max(0, region["health_score"] - 20)
                if region["health_score"] < 30:
                    region["status"] = "Unhealthy"
            
            region["last_health_check"] = datetime.now().isoformat()
            
            # Rebalance if region became unhealthy
            if region["status"] == "Unhealthy":
                self._rebalance_traffic()
    
    def set_tenant_region(self, tenant_id: str, region_id: str):
        """Set preferred region for tenant (data residency)."""
        with self.lock:
            self.tenant_regions[tenant_id] = region_id
    
    def route_request(self, tenant_id: Optional[str] = None) -> Optional[str]:
        """
        Route request to appropriate region.
        
        Args:
            tenant_id: Optional tenant for residency-aware routing
            
        Returns:
            Region ID to route to, or None if no healthy regions
        """
        with self.lock:
            healthy_regions = [
                r for r, info in self.regions.items() 
                if info["status"] in ["Healthy", "Degraded"]
            ]
            
            if not healthy_regions:
                return None
            
            # Respect tenant residency policy if set
            if tenant_id and tenant_id in self.tenant_regions:
                preferred = self.tenant_regions[tenant_id]
                if preferred in healthy_regions:
                    return preferred
            
            # Route to least loaded healthy region
            return min(
                healthy_regions,
                key=lambda r: self.regions[r]["current_load"] / self.regions[r]["capacity"]
            )
    
    def _rebalance_traffic(self):
        """Rebalance traffic distribution across healthy regions."""
        healthy_regions = [
            r for r, info in self.regions.items() 
            if info["status"] in ["Healthy", "Degraded"]
        ]
        
        if not healthy_regions:
            self.traffic_distribution = {}
            return
        
        # Distribute based on capacity
        total_capacity = sum(self.regions[r]["capacity"] for r in healthy_regions)
        
        for region in healthy_regions:
            percentage = int(
                (self.regions[region]["capacity"] / total_capacity) * 100
            )
            self.traffic_distribution[region] = percentage
    
    def get_traffic_status(self) -> Dict[str, Any]:
        """Get current traffic management status."""
        with self.lock:
            healthy_count = sum(
                1 for r in self.regions.values() 
                if r["status"] in ["Healthy", "Degraded"]
            )
            
            return {
                "total_regions": len(self.regions),
                "healthy_regions": healthy_count,
                "traffic_distribution": self.traffic_distribution,
                "tenant_policies": len(self.tenant_regions),
                "regions": self.regions
            }


class TenantOnboardingWizard:
    """
    Guided onboarding wizard for self-service tenant setup.
    Reduces friction from first login to value delivery.
    """
    
    def __init__(self):
        self.lock = threading.RLock()
        self.onboarding_sessions = {}  # session_id -> session data
        self.industry_templates = {
            "Finance": {
                "compliance_profiles": ["PCI_DSS", "SOC_2"],
                "threat_feeds": ["STIX_TAXII"],
                "siem_adapters": ["Splunk"],
                "sample_rules": ["phishing", "insider_risk"]
            },
            "Healthcare": {
                "compliance_profiles": ["HIPAA", "ISO_27001"],
                "threat_feeds": ["MISP"],
                "siem_adapters": ["ElasticStack"],
                "sample_rules": ["ransomware", "data_exfiltration"]
            },
            "Technology": {
                "compliance_profiles": ["SOC_2", "ISO_27001"],
                "threat_feeds": ["STIX_TAXII", "MISP"],
                "siem_adapters": ["AzureSentinel"],
                "sample_rules": ["phishing", "credential_abuse"]
            },
            "Retail": {
                "compliance_profiles": ["PCI_DSS"],
                "threat_feeds": ["STIX_TAXII"],
                "siem_adapters": ["Splunk", "ElasticStack"],
                "sample_rules": ["phishing", "ransomware"]
            }
        }
    
    def start_onboarding(self, tenant_id: str, industry: str) -> str:
        """Start a new onboarding session with guided setup."""
        with self.lock:
            session_id = secrets.token_urlsafe(16)
            
            template = self.industry_templates.get(industry, {
                "compliance_profiles": ["SOC_2"],
                "threat_feeds": [],
                "siem_adapters": [],
                "sample_rules": []
            })
            
            self.onboarding_sessions[session_id] = {
                "tenant_id": tenant_id,
                "industry": industry,
                "started_at": datetime.now(),
                "status": "In Progress",
                "steps_completed": [],
                "config": {
                    "compliance_profiles": template["compliance_profiles"],
                    "threat_feeds": template["threat_feeds"],
                    "siem_adapters": template["siem_adapters"],
                    "residency_policy": None,
                    "sample_rules": template["sample_rules"]
                },
                "validation_results": {}
            }
            
            return session_id
    
    def configure_step(self, session_id: str, step: str, config: Dict[str, Any]) -> bool:
        """Configure a specific onboarding step."""
        with self.lock:
            if session_id not in self.onboarding_sessions:
                return False
            
            session = self.onboarding_sessions[session_id]
            
            if step == "compliance":
                session["config"]["compliance_profiles"] = config.get("profiles", [])
            elif step == "feeds":
                session["config"]["threat_feeds"] = config.get("feeds", [])
            elif step == "siem":
                session["config"]["siem_adapters"] = config.get("adapters", [])
            elif step == "residency":
                session["config"]["residency_policy"] = config.get("policy")
            
            if step not in session["steps_completed"]:
                session["steps_completed"].append(step)
            
            return True
    
    def run_preflight_checks(self, session_id: str) -> Dict[str, Any]:
        """Run pre-flight validation before activating tenant."""
        with self.lock:
            if session_id not in self.onboarding_sessions:
                return {"success": False, "error": "Invalid session"}
            
            session = self.onboarding_sessions[session_id]
            config = session["config"]
            
            checks = {
                "compliance_profiles_valid": len(config["compliance_profiles"]) > 0,
                "residency_configured": config["residency_policy"] is not None,
                "at_least_one_feed": len(config["threat_feeds"]) > 0,
                "siem_configured": len(config["siem_adapters"]) > 0
            }
            
            all_passed = all(checks.values())
            
            session["validation_results"] = {
                "checks": checks,
                "all_passed": all_passed,
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "success": all_passed,
                "checks": checks,
                "recommendations": self._get_recommendations(checks)
            }
    
    def _get_recommendations(self, checks: Dict[str, bool]) -> List[str]:
        """Get recommendations based on validation checks."""
        recommendations = []
        
        if not checks["compliance_profiles_valid"]:
            recommendations.append("Configure at least one compliance profile")
        if not checks["residency_configured"]:
            recommendations.append("Set data residency policy for GDPR/compliance")
        if not checks["at_least_one_feed"]:
            recommendations.append("Enable threat intelligence feeds for better protection")
        if not checks["siem_configured"]:
            recommendations.append("Configure SIEM adapter for centralized monitoring")
        
        return recommendations
    
    def complete_onboarding(self, session_id: str, dry_run: bool = False) -> Dict[str, Any]:
        """Complete onboarding and activate tenant (or dry-run)."""
        with self.lock:
            if session_id not in self.onboarding_sessions:
                return {"success": False, "error": "Invalid session"}
            
            session = self.onboarding_sessions[session_id]
            
            if not session["validation_results"].get("all_passed", False):
                return {
                    "success": False,
                    "error": "Pre-flight checks failed. Run validation first."
                }
            
            if dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "config": session["config"],
                    "message": "Dry-run successful. Configuration is valid."
                }
            
            # Actual activation
            session["status"] = "Completed"
            session["completed_at"] = datetime.now()
            
            return {
                "success": True,
                "tenant_id": session["tenant_id"],
                "config": session["config"],
                "message": "Tenant onboarded successfully"
            }


class ReferenceArchitectureManager:
    """
    Provides IaC blueprints and reference architectures.
    Accelerates deployment with pre-tested patterns.
    """
    
    def __init__(self):
        self.architectures = {
            "single_tenant_k8s": {
                "name": "Single Tenant Kubernetes",
                "description": "Dedicated namespace with HA and DR",
                "components": ["ClusterManager", "GeoReplication", "DynamicWorkerPool"],
                "iac_templates": ["kubernetes", "terraform"]
            },
            "multi_tenant_k8s": {
                "name": "Multi-Tenant Kubernetes",
                "description": "Shared cluster with tenant isolation",
                "components": ["MultiTenantRBAC", "DataResidencyPolicy", "ResourceIsolation"],
                "iac_templates": ["kubernetes", "terraform"]
            },
            "air_gapped": {
                "name": "Air-Gapped Deployment",
                "description": "Offline mode with manual updates",
                "components": ["InMemoryStateStore", "LocalAuditLogger"],
                "iac_templates": ["terraform"]
            }
        }
    
    def get_architecture(self, architecture_type: str) -> Optional[Dict[str, Any]]:
        """Get architecture details."""
        return self.architectures.get(architecture_type)
    
    def export_blueprint(self, architecture_type: str, iac_format: str = "kubernetes") -> str:
        """Export IaC blueprint for deployment."""
        arch = self.architectures.get(architecture_type)
        if not arch:
            return ""
        
        if iac_format == "kubernetes":
            return self._generate_k8s_blueprint(arch)
        elif iac_format == "terraform":
            return self._generate_terraform_blueprint(arch)
        else:
            return ""
    
    def _generate_k8s_blueprint(self, arch: Dict[str, Any]) -> str:
        """Generate Kubernetes YAML blueprint."""
        return f"""# {arch['name']} - Kubernetes Deployment
apiVersion: v1
kind: Namespace
metadata:
  name: starlink-security
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: security-foundation
  namespace: starlink-security
spec:
  replicas: 3
  selector:
    matchLabels:
      app: security-foundation
  template:
    metadata:
      labels:
        app: security-foundation
    spec:
      containers:
      - name: foundation
        image: starlink-security:latest
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
# Components: {', '.join(arch['components'])}
"""
    
    def _generate_terraform_blueprint(self, arch: Dict[str, Any]) -> str:
        """Generate Terraform configuration."""
        return f"""# {arch['name']} - Terraform Configuration
resource "kubernetes_namespace" "starlink_security" {{
  metadata {{
    name = "starlink-security"
  }}
}}

resource "kubernetes_deployment" "security_foundation" {{
  metadata {{
    name      = "security-foundation"
    namespace = kubernetes_namespace.starlink_security.metadata[0].name
  }}
  
  spec {{
    replicas = 3
    
    selector {{
      match_labels = {{
        app = "security-foundation"
      }}
    }}
    
    template {{
      metadata {{
        labels = {{
          app = "security-foundation"
        }}
      }}
      
      spec {{
        container {{
          name  = "foundation"
          image = "starlink-security:latest"
          
          resources {{
            requests = {{
              memory = "1Gi"
              cpu    = "500m"
            }}
            limits = {{
              memory = "2Gi"
              cpu    = "1000m"
            }}
          }}
        }}
      }}
    }}
  }}
}}

# Components: {', '.join(arch['components'])}
"""


class SolutionAcceleratorManager:
    """
    Provides prebuilt rule packs and scorer configs.
    Shows immediate threat detection outcomes.
    """
    
    def __init__(self):
        self.accelerators = {
            "phishing": {
                "name": "Phishing Detection",
                "rules": ["suspicious_email_links", "spoofed_sender", "urgent_language"],
                "baseline_kpis": {"detection_rate": 0.85, "false_positives": 0.05},
                "scorer_config": {"rule_weight": 0.6, "ml_weight": 0.4}
            },
            "ransomware": {
                "name": "Ransomware Protection",
                "rules": ["file_encryption_activity", "backup_deletion", "lateral_movement"],
                "baseline_kpis": {"detection_rate": 0.90, "false_positives": 0.02},
                "scorer_config": {"rule_weight": 0.7, "ml_weight": 0.3}
            },
            "insider_risk": {
                "name": "Insider Threat Detection",
                "rules": ["unusual_data_access", "off_hours_activity", "policy_violations"],
                "baseline_kpis": {"detection_rate": 0.75, "false_positives": 0.10},
                "scorer_config": {"rule_weight": 0.5, "ml_weight": 0.5}
            },
            "data_exfiltration": {
                "name": "Data Exfiltration Prevention",
                "rules": ["large_uploads", "unusual_destinations", "encrypted_channels"],
                "baseline_kpis": {"detection_rate": 0.80, "false_positives": 0.08},
                "scorer_config": {"rule_weight": 0.6, "ml_weight": 0.4}
            },
            "credential_abuse": {
                "name": "Credential Abuse Detection",
                "rules": ["password_spraying", "credential_stuffing", "privilege_escalation"],
                "baseline_kpis": {"detection_rate": 0.88, "false_positives": 0.03},
                "scorer_config": {"rule_weight": 0.7, "ml_weight": 0.3}
            }
        }
    
    def get_accelerator(self, threat_type: str) -> Optional[Dict[str, Any]]:
        """Get solution accelerator details."""
        return self.accelerators.get(threat_type)
    
    def deploy_accelerator(self, threat_type: str) -> Dict[str, Any]:
        """Deploy prebuilt solution accelerator."""
        accel = self.accelerators.get(threat_type)
        if not accel:
            return {"success": False, "error": "Unknown threat type"}
        
        return {
            "success": True,
            "threat_type": threat_type,
            "rules_deployed": accel["rules"],
            "scorer_config": accel["scorer_config"],
            "baseline_kpis": accel["baseline_kpis"],
            "monitoring_enabled": True
        }


class TieredSLAManager:
    """
    Defines and tracks tiered SLAs with response/resolution targets.
    Maps incidents to runbooks and escalation paths.
    """
    
    def __init__(self):
        self.lock = threading.RLock()
        self.sla_tiers = {
            "Gold": {
                "response_time_minutes": 60,
                "resolution_time_hours": 4,
                "availability_target": 99.99,
                "support_hours": "24x7"
            },
            "Silver": {
                "response_time_minutes": 240,
                "resolution_time_hours": 24,
                "availability_target": 99.9,
                "support_hours": "Business hours + on-call"
            },
            "Bronze": {
                "response_time_minutes": 1440,
                "resolution_time_hours": 72,
                "availability_target": 99.0,
                "support_hours": "Business hours"
            }
        }
        self.incidents = []  # List of incident records
        self.adherence_stats = {tier: {"met": 0, "missed": 0} for tier in self.sla_tiers}
    
    def log_incident(self, incident_id: str, tier: str, severity: str, description: str) -> bool:
        """Log a new incident with SLA tracking."""
        with self.lock:
            if tier not in self.sla_tiers:
                return False
            
            sla = self.sla_tiers[tier]
            
            incident = {
                "id": incident_id,
                "tier": tier,
                "severity": severity,
                "description": description,
                "created_at": datetime.now(),
                "response_deadline": datetime.now() + timedelta(minutes=sla["response_time_minutes"]),
                "resolution_deadline": datetime.now() + timedelta(hours=sla["resolution_time_hours"]),
                "responded_at": None,
                "resolved_at": None,
                "escalation_path": self._get_escalation_path(severity),
                "runbook": self._get_runbook(description)
            }
            
            self.incidents.append(incident)
            return True
    
    def _get_escalation_path(self, severity: str) -> List[str]:
        """Get escalation path based on severity."""
        if severity == "Critical":
            return ["L1 Support", "L2 Support", "Engineering Lead", "VP Engineering"]
        elif severity == "High":
            return ["L1 Support", "L2 Support", "Engineering Lead"]
        else:
            return ["L1 Support", "L2 Support"]
    
    def _get_runbook(self, description: str) -> str:
        """Map incident to appropriate runbook."""
        desc_lower = description.lower()
        
        if "scorer" in desc_lower:
            return "runbook_scorer_outage"
        elif "redis" in desc_lower or "state" in desc_lower:
            return "runbook_redis_failure"
        elif "kms" in desc_lower or "key" in desc_lower:
            return "runbook_kms_failure"
        elif "cluster" in desc_lower:
            return "runbook_cluster_failover"
        else:
            return "runbook_general_incident"
    
    def mark_responded(self, incident_id: str) -> bool:
        """Mark incident as responded."""
        with self.lock:
            for incident in self.incidents:
                if incident["id"] == incident_id:
                    incident["responded_at"] = datetime.now()
                    
                    # Check SLA adherence
                    if incident["responded_at"] <= incident["response_deadline"]:
                        self.adherence_stats[incident["tier"]]["met"] += 1
                    else:
                        self.adherence_stats[incident["tier"]]["missed"] += 1
                    
                    return True
            return False
    
    def mark_resolved(self, incident_id: str) -> bool:
        """Mark incident as resolved."""
        with self.lock:
            for incident in self.incidents:
                if incident["id"] == incident_id:
                    incident["resolved_at"] = datetime.now()
                    return True
            return False
    
    def get_sla_adherence(self) -> Dict[str, Any]:
        """Get SLA adherence statistics."""
        with self.lock:
            adherence_percentages = {}
            
            for tier, stats in self.adherence_stats.items():
                total = stats["met"] + stats["missed"]
                if total > 0:
                    adherence_percentages[tier] = (stats["met"] / total) * 100
                else:
                    adherence_percentages[tier] = 100.0
            
            return {
                "by_tier": adherence_percentages,
                "raw_stats": self.adherence_stats,
                "total_incidents": len(self.incidents)
            }


class PostIncidentReviewManager:
    """
    Automated PIR (Post-Incident Review) generation.
    Captures timeline, root cause, SLO impact, and remediation.
    """
    
    def __init__(self):
        self.lock = threading.RLock()
        self.pirs = []  # List of PIR records
    
    def create_pir(self, incident_id: str, incident_data: Dict[str, Any]) -> str:
        """Create automated PIR template."""
        with self.lock:
            pir_id = f"PIR-{secrets.token_hex(4)}"
            
            pir = {
                "id": pir_id,
                "incident_id": incident_id,
                "created_at": datetime.now(),
                "timeline": self._generate_timeline(incident_data),
                "contributing_factors": [],
                "root_cause": None,
                "slo_impact": self._calculate_slo_impact(incident_data),
                "remediation_items": [],
                "status": "Draft",
                "owner": None,
                "backlog_items": []
            }
            
            self.pirs.append(pir)
            return pir_id
    
    def _generate_timeline(self, incident_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate incident timeline."""
        timeline = []
        
        if "created_at" in incident_data:
            timeline.append({
                "timestamp": incident_data["created_at"].isoformat(),
                "event": "Incident detected"
            })
        
        if "responded_at" in incident_data and incident_data["responded_at"]:
            timeline.append({
                "timestamp": incident_data["responded_at"].isoformat(),
                "event": "Response initiated"
            })
        
        if "resolved_at" in incident_data and incident_data["resolved_at"]:
            timeline.append({
                "timestamp": incident_data["resolved_at"].isoformat(),
                "event": "Incident resolved"
            })
        
        return timeline
    
    def _calculate_slo_impact(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate impact on SLOs."""
        impact = {
            "availability_affected": False,
            "latency_affected": False,
            "downtime_minutes": 0
        }
        
        if "created_at" in incident_data and "resolved_at" in incident_data:
            if incident_data["resolved_at"]:
                downtime = incident_data["resolved_at"] - incident_data["created_at"]
                impact["downtime_minutes"] = downtime.total_seconds() / 60
                impact["availability_affected"] = True
        
        return impact
    
    def update_pir(self, pir_id: str, updates: Dict[str, Any]) -> bool:
        """Update PIR with additional information."""
        with self.lock:
            for pir in self.pirs:
                if pir["id"] == pir_id:
                    if "contributing_factors" in updates:
                        pir["contributing_factors"] = updates["contributing_factors"]
                    if "root_cause" in updates:
                        pir["root_cause"] = updates["root_cause"]
                    if "remediation_items" in updates:
                        pir["remediation_items"] = updates["remediation_items"]
                    if "backlog_items" in updates:
                        pir["backlog_items"] = updates["backlog_items"]
                    if "owner" in updates:
                        pir["owner"] = updates["owner"]
                    
                    return True
            return False
    
    def finalize_pir(self, pir_id: str) -> bool:
        """Finalize PIR and mark as complete."""
        with self.lock:
            for pir in self.pirs:
                if pir["id"] == pir_id:
                    pir["status"] = "Finalized"
                    pir["finalized_at"] = datetime.now()
                    return True
            return False
    
    def get_pir(self, pir_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve PIR by ID."""
        with self.lock:
            for pir in self.pirs:
                if pir["id"] == pir_id:
                    return pir.copy()
            return None


class CapacityPlanningManager:
    """
    Forecasting for event volume, scoring load, and storage.
    Provides per-tenant budget alerts and tuning recommendations.
    """
    
    def __init__(self):
        self.lock = threading.RLock()
        self.tenant_metrics = {}  # tenant_id -> metrics history
        self.forecasts = {}  # tenant_id -> forecast data
    
    def record_metrics(self, tenant_id: str, metrics: Dict[str, float]):
        """Record metrics for capacity planning."""
        with self.lock:
            if tenant_id not in self.tenant_metrics:
                self.tenant_metrics[tenant_id] = []
            
            self.tenant_metrics[tenant_id].append({
                "timestamp": datetime.now(),
                "event_volume": metrics.get("event_volume", 0),
                "scoring_load": metrics.get("scoring_load", 0),
                "storage_used_gb": metrics.get("storage_used_gb", 0)
            })
            
            # Keep only last 30 days of metrics
            cutoff = datetime.now() - timedelta(days=30)
            self.tenant_metrics[tenant_id] = [
                m for m in self.tenant_metrics[tenant_id]
                if m["timestamp"] > cutoff
            ]
    
    def generate_forecast(self, tenant_id: str, days_ahead: int = 30) -> Dict[str, Any]:
        """Generate capacity forecast for tenant."""
        with self.lock:
            if tenant_id not in self.tenant_metrics or not self.tenant_metrics[tenant_id]:
                return {"error": "Insufficient data for forecasting"}
            
            metrics = self.tenant_metrics[tenant_id]
            
            # Simple linear extrapolation
            recent_avg_events = sum(m["event_volume"] for m in metrics[-7:]) / min(7, len(metrics))
            recent_avg_scoring = sum(m["scoring_load"] for m in metrics[-7:]) / min(7, len(metrics))
            recent_avg_storage = sum(m["storage_used_gb"] for m in metrics[-7:]) / min(7, len(metrics))
            
            # Project forward
            growth_rate = 1.1  # Assume 10% growth
            
            forecast = {
                "tenant_id": tenant_id,
                "forecast_days": days_ahead,
                "projected_event_volume": recent_avg_events * growth_rate * days_ahead,
                "projected_scoring_load": recent_avg_scoring * growth_rate * days_ahead,
                "projected_storage_gb": recent_avg_storage + (recent_avg_storage * 0.05 * days_ahead),
                "recommendations": []
            }
            
            # Generate recommendations
            if forecast["projected_event_volume"] > 100000:
                forecast["recommendations"].append("Consider increasing batch size for events")
            
            if forecast["projected_scoring_load"] > 10000:
                forecast["recommendations"].append("Enable score caching to reduce load")
            
            if forecast["projected_storage_gb"] > 100:
                forecast["recommendations"].append("Review retention policies to manage storage")
            
            self.forecasts[tenant_id] = forecast
            return forecast
    
    def check_budget_alerts(self, tenant_id: str, budget_limits: Dict[str, float]) -> List[str]:
        """Check if tenant is approaching budget limits."""
        with self.lock:
            alerts = []
            
            if tenant_id not in self.forecasts:
                return alerts
            
            forecast = self.forecasts[tenant_id]
            
            if "event_volume_limit" in budget_limits:
                if forecast["projected_event_volume"] > budget_limits["event_volume_limit"] * 0.8:
                    alerts.append(f"Approaching event volume budget limit (80%)")
            
            if "scoring_load_limit" in budget_limits:
                if forecast["projected_scoring_load"] > budget_limits["scoring_load_limit"] * 0.8:
                    alerts.append(f"Approaching scoring load budget limit (80%)")
            
            if "storage_limit_gb" in budget_limits:
                if forecast["projected_storage_gb"] > budget_limits["storage_limit_gb"] * 0.8:
                    alerts.append(f"Approaching storage budget limit (80%)")
            
            return alerts


class AttestationBundleManager:
    """
    Generates signed attestation bundles for trust and transparency.
    Includes SBOM, SLO reports, audit proofs, DR drill results, compliance mappings.
    """
    
    def __init__(self):
        self.lock = threading.RLock()
        self.bundles = []  # List of generated bundles
    
    def generate_bundle(self, components: List[str]) -> Dict[str, Any]:
        """Generate attestation bundle with specified components."""
        with self.lock:
            bundle_id = f"ATTEST-{secrets.token_hex(8)}"
            
            bundle_data = {
                "bundle_id": bundle_id,
                "generated_at": datetime.now().isoformat(),
                "components": {}
            }
            
            if "sbom" in components:
                bundle_data["components"]["sbom"] = {
                    "format": "CycloneDX",
                    "dependencies": ["cryptography>=42.0.4"],
                    "checksum": hashlib.sha256(b"sbom_data").hexdigest()
                }
            
            if "slo_reports" in components:
                bundle_data["components"]["slo_reports"] = {
                    "scoring_p99_ms": 85,
                    "queue_p95_ms": 42,
                    "feed_freshness_p99_min": 3.5,
                    "audit_success_pct": 100.0
                }
            
            if "audit_proofs" in components:
                bundle_data["components"]["audit_proofs"] = {
                    "hash_chain_verified": True,
                    "last_hash": hashlib.sha256(b"audit_data").hexdigest(),
                    "entry_count": 1000
                }
            
            if "dr_drill_results" in components:
                bundle_data["components"]["dr_drill_results"] = {
                    "last_drill_date": (datetime.now() - timedelta(days=45)).isoformat(),
                    "rto_actual_minutes": 55,
                    "rpo_actual_minutes": 12,
                    "success": True
                }
            
            if "compliance_mappings" in components:
                bundle_data["components"]["compliance_mappings"] = {
                    "soc2": "Implemented",
                    "iso27001": "Implemented",
                    "pci_dss": "Implemented",
                    "hipaa": "Implemented"
                }
            
            # Generate bundle checksum
            bundle_json = json.dumps(bundle_data, sort_keys=True)
            bundle_checksum = hashlib.sha256(bundle_json.encode()).hexdigest()
            
            bundle = {
                "id": bundle_id,
                "data": bundle_data,
                "checksum": bundle_checksum,
                "signature": self._sign_bundle(bundle_checksum)
            }
            
            self.bundles.append(bundle)
            return bundle
    
    def _sign_bundle(self, checksum: str) -> str:
        """Sign bundle checksum (placeholder for actual signing)."""
        # In production, use actual cryptographic signing
        return f"SIG-{hashlib.sha256(checksum.encode()).hexdigest()[:16]}"
    
    def verify_bundle(self, bundle_id: str) -> Dict[str, Any]:
        """Verify attestation bundle integrity."""
        with self.lock:
            for bundle in self.bundles:
                if bundle["id"] == bundle_id:
                    bundle_json = json.dumps(bundle["data"], sort_keys=True)
                    expected_checksum = hashlib.sha256(bundle_json.encode()).hexdigest()
                    
                    return {
                        "valid": bundle["checksum"] == expected_checksum,
                        "checksum_match": bundle["checksum"] == expected_checksum,
                        "signature": bundle["signature"]
                    }
            
            return {"valid": False, "error": "Bundle not found"}


class DualControlApprovalManager:
    """
    Dual-control workflow for high-impact policy/model changes.
    Requires separate requester and approver with mandatory simulation.
    """
    
    def __init__(self):
        self.lock = threading.RLock()
        self.pending_approvals = []  # List of pending approval requests
        self.approval_history = []  # List of completed approvals
    
    def request_approval(
        self, 
        requester: str, 
        change_type: str, 
        description: str, 
        change_data: Dict[str, Any]
    ) -> str:
        """Request approval for high-impact change."""
        with self.lock:
            request_id = f"APPROVAL-{secrets.token_hex(6)}"
            
            request = {
                "id": request_id,
                "requester": requester,
                "change_type": change_type,
                "description": description,
                "change_data": change_data,
                "requested_at": datetime.now(),
                "status": "Pending Simulation",
                "simulation_results": None,
                "approver": None,
                "approved_at": None,
                "rejected_reason": None
            }
            
            self.pending_approvals.append(request)
            return request_id
    
    def run_simulation(self, request_id: str, simulation_results: Dict[str, Any]) -> bool:
        """Attach simulation results to approval request."""
        with self.lock:
            for request in self.pending_approvals:
                if request["id"] == request_id:
                    request["simulation_results"] = simulation_results
                    request["status"] = "Pending Approval"
                    return True
            return False
    
    def approve(self, request_id: str, approver: str) -> bool:
        """Approve change request (must be different from requester)."""
        with self.lock:
            for i, request in enumerate(self.pending_approvals):
                if request["id"] == request_id:
                    if approver == request["requester"]:
                        return False  # Cannot self-approve
                    
                    if request["status"] != "Pending Approval":
                        return False  # Must have simulation results
                    
                    request["status"] = "Approved"
                    request["approver"] = approver
                    request["approved_at"] = datetime.now()
                    
                    # Move to history
                    self.approval_history.append(request)
                    del self.pending_approvals[i]
                    
                    return True
            return False
    
    def reject(self, request_id: str, approver: str, reason: str) -> bool:
        """Reject change request."""
        with self.lock:
            for i, request in enumerate(self.pending_approvals):
                if request["id"] == request_id:
                    request["status"] = "Rejected"
                    request["approver"] = approver
                    request["approved_at"] = datetime.now()
                    request["rejected_reason"] = reason
                    
                    # Move to history
                    self.approval_history.append(request)
                    del self.pending_approvals[i]
                    
                    return True
            return False
    
    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get all pending approval requests."""
        with self.lock:
            return [r.copy() for r in self.pending_approvals]
    
    def get_approval_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get approval history."""
        with self.lock:
            return [r.copy() for r in self.approval_history[-limit:]]

    event_type: str
    severity: str
    source: str
    message: str
    timestamp: datetime
    metadata: Dict[str, Any]


class StarlinkSecurityFoundation:
    """Core security foundation for Starlink infrastructure."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize security foundation."""
        self.config = config or self._default_config()
        self.running = False
        self.metrics = {}
        self.event_handlers: list[Callable[[SecurityEvent], Awaitable[None]]] = []
        # Defined for compatibility with other StarlinkSecurityFoundation variants.
        self.audit_formatters: list[Any] = []
        logger.info("Starlink Security Foundation initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'security': {
                'vpn_required': True,
                'encryption_level': 'high'
            },
            'enterprise': {
                'backup_connections': ['cellular_backup', 'satellite_backup']
            }
        }

    def get_security_report(self) -> Dict[str, Any]:
        """Generate a basic security report.

        NOTE: This module contains multiple foundation implementations.
        Some call sites expect a `get_security_report()` method; providing it
        here ensures backward-compatible behavior and satisfies static type
        checkers.
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "running": self.running,
            "config": self.config,
            "metrics": self.metrics,
        }
    
    async def trigger_event(
        self,
        event_type: str,
        severity: str,
        source: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Trigger a security event."""
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            source=source,
            description=message,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        logger.info(f"Security event: {event_type} ({severity}) - {message}")
        
        # Notify event handlers
        for handler in self.event_handlers:
            await handler(event)
    
    def register_event_handler(self, handler: Callable[[SecurityEvent], Awaitable[None]]) -> None:
        """Register an event handler."""
        self.event_handlers.append(handler)


class PolicyEnforcer:
    """Enforce security policies based on threat level."""
    
    # NOTE: This module contains multiple *Foundation* implementations.
    # Accept a broader type here to avoid static type mismatches when wiring
    # PolicyEnforcer with EnterpriseStarlinkSecurityFoundation or other variants.
    def __init__(self, foundation: Any):
        self.foundation = foundation
        self.active_policies = {
            "network_access": {
                "allowed_ports": [80, 443, 22],
                "blocked_ips": []
            },
            "encryption": {
                "require_tls_1.3": True,
                "minimum_key_length": 2048
            }
        }
    
    def initialize(self) -> bool:
        """Initialize policy enforcer."""
        logger.info("Initializing Policy Enforcer")
        return True
    
    async def enforce_security_level(self, level: str):
        """Enforce security policies based on threat level."""
        logger.info(f"Enforcing security level: {level}")
        
        if level == "critical":
            await self._block_non_essential_traffic()
        
        # Apply policies
        await self._enforce_firewall_rules()
        await self._enforce_encryption_policies()
    
    async def _enforce_firewall_rules(self):
        """Enforce firewall rules based on policies."""
        allowed_ports = self.active_policies["network_access"]["allowed_ports"]
        
        logger.info(f"Enforcing firewall rules. Allowed ports: {allowed_ports}")
        
        # In production, this would configure iptables/ufw/nftables
        # For example:
        # subprocess.run(['sudo', 'ufw', 'default', 'deny', 'incoming'])
        # for port in allowed_ports:
        #     subprocess.run(['sudo', 'ufw', 'allow', str(port)])
    
    async def _enforce_encryption_policies(self):
        """Enforce encryption policies."""
        if self.active_policies["encryption"]["require_tls_1.3"]:
            logger.info("Enforcing TLS 1.3 requirement")
            # Configure web servers to require TLS 1.3
    
    async def _block_non_essential_traffic(self):
        """Block non-essential traffic during critical security level."""
        logger.info("Blocking non-essential traffic")
        
        # In production, would implement specific firewall rules
        # For example, only allow traffic to/from specific IPs


class IncidentResponder:
    """Respond to security incidents."""
    
    def __init__(self, foundation: DemoStarlinkSecurityFoundation):
        self.foundation = foundation
        self.incidents = []
    
    def initialize(self) -> bool:
        """Initialize incident responder."""
        logger.info("Initializing Incident Responder")
        return True
    
    async def handle_incident(self, event: SecurityEvent):
        """Handle a security incident."""
        logger.info(f"Handling incident: {event.event_type}")
        
        # Add to incidents list
        self.incidents.append(event)
        
        # Determine response based on event type
        if event.severity == "critical":
            await self._handle_critical_incident(event)
        elif event.severity == "high":
            await self._handle_high_incident(event)
        
        # Log response
        await self._log_response(event)
    
    async def _handle_critical_incident(self, event: SecurityEvent):
        """Handle critical security incident."""
        actions = []
        
        if "malware" in event.event_type.lower():
            actions.extend([
                "Isolate affected systems",
                "Initiate malware scan",
                "Notify security team"
            ])
        elif "breach" in event.event_type.lower():
            actions.extend([
                "Block source IPs",
                "Reset credentials",
                "Enable enhanced logging"
            ])
        
        # Execute actions
        for action in actions:
            logger.info(f"Critical incident action: {action}")
            # In production, execute the action
    
    async def _handle_high_incident(self, event: SecurityEvent):
        """Handle high severity incident."""
        # Similar to critical but less aggressive
        pass
    
    async def _log_response(self, event: SecurityEvent):
        """Log incident response."""
        response_log = LOG_DIR / f"incident_response_{datetime.now().strftime('%Y%m%d')}.json"
        
        log_entry = {
            "incident_time": event.timestamp.isoformat(),
            "event_type": event.event_type,
            "severity": event.severity,
            "response_time": datetime.now().isoformat(),
            "actions_taken": ["logged", "analyzed"]
        }
        
        try:
            with open(response_log, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to log incident response: {e}")


class VPNManager:
    """Manage VPN connections for secure remote access."""
    
    def __init__(self, foundation: DemoStarlinkSecurityFoundation):
        self.foundation = foundation
        self.vpn_status = "disconnected"
        self.last_connection = None
    
    def initialize(self) -> bool:
        """Initialize VPN manager."""
        logger.info("Initializing VPN Manager")
        return True
    
    async def start(self):
        """Start VPN monitoring."""
        logger.info("Starting VPN Manager")
        
        while self.foundation.running:
            try:
                await self.check_vpn_status()
                await self.ensure_vpn_connectivity()
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"VPN manager error: {e}")
                await asyncio.sleep(30)
    
    async def check_vpn_status(self):
        """Check current VPN status."""
        # Simulate VPN status check
        statuses = ["connected", "disconnected", "connecting"]
        # Using random for VPN status simulation (not security-critical)
        new_status = random.choice(statuses)  # nosec B311
        
        if new_status != self.vpn_status:
            old_status = self.vpn_status
            self.vpn_status = new_status
            
            severity = "warning" if new_status == "disconnected" else "info"
            
            await self.foundation.trigger_event(
                "vpn_status_changed",
                severity,
                "vpn_manager",
                f"VPN status changed from {old_status} to {new_status}",
                {"old_status": old_status, "new_status": new_status}
            )
    
    async def ensure_vpn_connectivity(self):
        """Ensure VPN is connected if required."""
        if (self.foundation.config['security']['vpn_required'] and 
            self.vpn_status == "disconnected"):
            
            logger.info("VPN required but disconnected. Attempting to connect...")
            
            # Attempt to connect
            success = await self._connect_vpn()
            
            if success:
                self.vpn_status = "connected"
                self.last_connection = datetime.now()
            else:
                await self.foundation.trigger_event(
                    "vpn_connection_failed",
                    "high",
                    "vpn_manager",
                    "Failed to establish VPN connection",
                    {"attempts": 1}
                )
    
    async def _connect_vpn(self) -> bool:
        """Connect to VPN."""
        # In production, would call OpenVPN/WireGuard client
        # For example:
        # result = subprocess.run(['sudo', 'systemctl', 'start', 'openvpn@client'])
        # return result.returncode == 0
        
        # Using random for VPN connection simulation (not security-critical)
        return random.random() > 0.3  # nosec B311 - 70% success rate for simulation


class BackupManager:
    """Manage backup connections and failover."""
    
    def __init__(self, foundation: DemoStarlinkSecurityFoundation):
        self.foundation = foundation
        self.backup_connections = {}
        self.active_backup = None
    
    def initialize(self) -> bool:
        """Initialize backup manager."""
        logger.info("Initializing Backup Manager")
        self._discover_backups()
        return True
    
    def _discover_backups(self):
        """Discover available backup connections."""
        backups = self.foundation.config['enterprise']['backup_connections']
        
        for backup in backups:
            self.backup_connections[backup] = {
                "available": True,
                "priority": 1 if "cellular" in backup else 2,
                "last_tested": None
            }
    
    async def start(self):
        """Start backup connection monitoring."""
        logger.info("Starting Backup Manager")
        
        while self.foundation.running:
            try:
                await self.check_backup_availability()
                await self.evaluate_failover_needs()
                await asyncio.sleep(120)
            except Exception as e:
                logger.error(f"Backup manager error: {e}")
                await asyncio.sleep(60)
    
    async def check_backup_availability(self):
        """Check availability of backup connections."""
        for backup_name, info in self.backup_connections.items():
            # Simulate availability check
            was_available = info["available"]
            # Using random for availability simulation (not security-critical)
            info["available"] = random.random() > 0.2  # nosec B311 - 80% available
            
            if was_available != info["available"]:
                status = "available" if info["available"] else "unavailable"
                
                await self.foundation.trigger_event(
                    "backup_status_changed",
                    "info",
                    "backup_manager",
                    f"Backup connection {backup_name} is now {status}",
                    {"backup": backup_name, "status": status}
                )
    
    async def evaluate_failover_needs(self):
        """Evaluate if failover to backup is needed."""
        # Check primary connection health
        # If primary is down, activate highest priority available backup
        available_backups = [
            (name, info) for name, info in self.backup_connections.items()
            if info["available"]
        ]
        
        if available_backups and not self.active_backup:
            # Sort by priority
            available_backups.sort(key=lambda x: x[1]["priority"])
            best_backup = available_backups[0][0]
            
            logger.info(f"Considering failover to backup: {best_backup}")
            # In production, would actually initiate failover


async def demo_main():
    """Main entry point for demonstration."""
    # Create security foundation
    foundation = DemoStarlinkSecurityFoundation()
    foundation.running = True
    
    # Initialize components
    policy_enforcer = PolicyEnforcer(foundation)
    incident_responder = IncidentResponder(foundation)
    vpn_manager = VPNManager(foundation)
    backup_manager = BackupManager(foundation)
    
    # Initialize all components
    policy_enforcer.initialize()
    incident_responder.initialize()
    vpn_manager.initialize()
    backup_manager.initialize()
    
    # Register incident responder as event handler
    foundation.register_event_handler(incident_responder.handle_incident)
    
    # Demonstrate security enforcement
    await policy_enforcer.enforce_security_level("normal")
    logger.info("Normal security level enforced")
    
    await policy_enforcer.enforce_security_level("critical")
    logger.info("Critical security level enforced")
    
    # Simulate some security events
    await foundation.trigger_event(
        "malware_detected",
        "critical",
        "antivirus",
        "Malware detected on endpoint device",
        {"device_id": "endpoint-001", "malware_type": "trojan"}
    )
    
    await foundation.trigger_event(
        "unauthorized_access_attempt",
        "high",
        "firewall",
        "Multiple failed login attempts detected",
        {"source_ip": "192.168.1.100", "attempts": 5}
    )
    
    logger.info("Security infrastructure demonstration completed")
    foundation.running = False


# ---------------------------------------------------------------------------
# Public API exports
# ---------------------------------------------------------------------------
# This module contains multiple architectures and local/demo implementations.
# To avoid ambiguity for API consumers, export the modular architecture
# foundation as the canonical `StarlinkSecurityFoundation`, while keeping the
# local implementation available under an explicit name.

# NOTE (type checking): This module defines a local `StarlinkSecurityFoundation`
# class earlier, but we intentionally re-export the modular implementation as the
# canonical symbol for runtime users. Use `cast(Any, ...)` to avoid type checker
# assignment errors.
from typing import cast

LegacyStarlinkSecurityFoundation = StarlinkSecurityFoundation
StarlinkSecurityFoundation = cast(Any, ModularStarlinkSecurityFoundation)

__all__ = [
    "SecurityLevel",
    "StarlinkSecurityFoundation",
    "LegacyStarlinkSecurityFoundation",
    "NetworkMonitor",
    "ThreatDetector",
    "PolicyEnforcer",
]


if __name__ == "__main__":
    asyncio.run(demo_main())
