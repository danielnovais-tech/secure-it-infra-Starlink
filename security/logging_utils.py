"""
Structured logging utilities for Starlink Security Foundation
"""

import json
import logging
from datetime import datetime, timezone


class StructuredLogger:
    """Provides structured JSON logging for better SIEM/ELK integration."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # JSON formatter for structured logs
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        self.logger.addHandler(handler)
    
    def log_event(self, level: str, message: str, **kwargs):
        """Log a structured event."""
        log_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': level,
            'message': message,
            **kwargs
        }
        
        # Validate level is a string and get appropriate log method
        if isinstance(level, str):
            log_method = getattr(self.logger, level.lower(), self.logger.info)
        else:
            log_method = self.logger.info
        log_method(json.dumps(log_data))
    
    def info(self, message: str, **kwargs):
        """Log info level message."""
        self.log_event('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning level message."""
        self.log_event('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error level message."""
        self.log_event('ERROR', message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug level message."""
        self.log_event('DEBUG', message, **kwargs)


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for log records."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        try:
            # Try to parse as JSON if already formatted
            log_dict = json.loads(record.getMessage())
        except (json.JSONDecodeError, TypeError):
            # Fall back to traditional format
            log_dict = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
        
        return json.dumps(log_dict)
