"""
Structured logging module with event correlation.

Provides comprehensive logging with JSON formatting, event correlation,
and multiple output destinations.
"""

import logging
import time
import socket
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import deque
from pythonjsonlogger import jsonlogger


class EventCorrelator:
    """
    Event correlation engine for detecting patterns across multiple events.
    
    Correlates events based on common fields and detects predefined patterns
    such as brute force attacks and data exfiltration attempts.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize event correlator.
        
        Args:
            config: Correlation configuration
        """
        self.config = config
        self.enabled = config.get('enabled', True)
        self.window_size = config.get('window_size', 300)
        self.correlation_fields = config.get('correlation_fields', [])
        self.patterns = config.get('patterns', [])
        
        # Store events for correlation
        self.event_buffer: deque = deque(maxlen=1000)
        self.correlated_events: List[Dict[str, Any]] = []
    
    def add_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Add an event to the correlation buffer and check for patterns.
        
        Args:
            event: Event to correlate
            
        Returns:
            Correlated incident if pattern detected, None otherwise
        """
        if not self.enabled:
            return None
        
        # Add timestamp if not present
        if 'timestamp' not in event:
            event['timestamp'] = time.time()
        
        self.event_buffer.append(event)
        
        # Check for pattern matches
        return self._check_patterns(event)
    
    def _check_patterns(self, current_event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check if current event triggers any correlation patterns.
        
        Args:
            current_event: Event to check
            
        Returns:
            Incident details if pattern matched
        """
        current_time = time.time()
        
        for pattern in self.patterns:
            pattern_name = pattern.get('name')
            required_events = pattern.get('events', [])
            count_threshold = pattern.get('count', 1)
            timeframe = pattern.get('timeframe', 60)
            
            # Get events within timeframe
            recent_events = [
                e for e in self.event_buffer
                if current_time - e['timestamp'] <= timeframe
            ]
            
            # Check if pattern matches
            matching_events = [
                e for e in recent_events
                if self._event_matches_pattern(e, required_events)
            ]
            
            if len(matching_events) >= count_threshold:
                incident = self._create_incident(pattern_name, matching_events)
                self.correlated_events.append(incident)
                return incident
        
        return None
    
    def _event_matches_pattern(self, event: Dict[str, Any], pattern_events: List[str]) -> bool:
        """Check if an event matches any of the pattern event types."""
        event_type = event.get('event_type', event.get('type', ''))
        return event_type in pattern_events
    
    def _create_incident(self, pattern_name: str, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create an incident from correlated events."""
        return {
            'incident_type': pattern_name,
            'timestamp': datetime.now().isoformat(),
            'event_count': len(events),
            'events': events,
            'correlation_fields': self._extract_correlation_fields(events),
            'severity': 'high' if len(events) >= 10 else 'medium'
        }
    
    def _extract_correlation_fields(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract common correlation fields from events."""
        correlation_data = {}
        
        for field in self.correlation_fields:
            values = [e.get(field) for e in events if field in e]
            if values:
                # Get unique values and their counts
                unique_values = list(set(values))
                correlation_data[field] = {
                    'unique_count': len(unique_values),
                    'values': unique_values[:10]  # Limit to first 10
                }
        
        return correlation_data
    
    def get_correlated_events(self, timeframe: int = 3600) -> List[Dict[str, Any]]:
        """
        Get correlated events within a timeframe.
        
        Args:
            timeframe: Timeframe in seconds
            
        Returns:
            List of correlated incidents
        """
        current_time = time.time()
        recent_incidents = []
        
        for incident in self.correlated_events:
            try:
                # Try parsing with microseconds first
                timestamp = incident['timestamp']
                try:
                    incident_time = time.mktime(time.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f'))
                except ValueError:
                    # Fall back to parsing without microseconds
                    incident_time = time.mktime(time.strptime(timestamp, '%Y-%m-%dT%H:%M:%S'))
                
                if current_time - incident_time <= timeframe:
                    recent_incidents.append(incident)
            except (ValueError, KeyError):
                # Skip incidents with invalid timestamps
                continue
        
        return recent_incidents


class CustomJsonFormatter(jsonlogger.JsonFormatter):  # pyright: ignore[reportPrivateImportUsage]
    """
    Custom JSON formatter for structured logging.
    
    Adds additional fields like hostname, process ID, and custom metadata.
    """
    
    def __init__(self, include_hostname=True, include_process_id=True, *args, **kwargs):
        """
        Initialize JSON formatter.
        
        Args:
            include_hostname: Include hostname in logs
            include_process_id: Include process ID in logs
        """
        super().__init__(*args, **kwargs)
        self.include_hostname = include_hostname
        self.include_process_id = include_process_id
        self.hostname = socket.gethostname() if include_hostname else None
    
    def add_fields(self, log_record, record, message_dict):
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add hostname
        if self.include_hostname and self.hostname:
            log_record['hostname'] = self.hostname
        
        # Add process ID
        if self.include_process_id:
            log_record['process_id'] = os.getpid()
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name


class StructuredLogger:
    """
    Main structured logging system with multiple output destinations.
    
    Provides comprehensive logging with JSON formatting, file rotation,
    console output, and event correlation.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize structured logger.
        
        Args:
            config: Logging configuration
        """
        self.config = config
        self.structured_config = config.get('structured', {})
        self.correlation_config = config.get('correlation', {})
        self.destinations = config.get('destinations', [])
        self.levels = config.get('levels', {})
        
        # Initialize event correlator
        self.correlator = EventCorrelator(self.correlation_config)
        
        # Setup loggers
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup the main logger with all handlers."""
        logger = logging.getLogger('secure_it_starlink')
        logger.setLevel(self._get_log_level(self.levels.get('root', 'INFO')))
        
        # Clear existing handlers
        logger.handlers = []
        
        # Add handlers for each destination
        for dest in self.destinations:
            handler = self._create_handler(dest)
            if handler:
                logger.addHandler(handler)
        
        return logger
    
    def _create_handler(self, dest_config: Dict[str, Any]) -> Optional[logging.Handler]:
        """
        Create a log handler based on destination configuration.
        
        Args:
            dest_config: Destination configuration
            
        Returns:
            Configured handler or None
        """
        dest_type = dest_config.get('type')
        
        if dest_type == 'file':
            return self._create_file_handler(dest_config)
        elif dest_type == 'console':
            return self._create_console_handler(dest_config)
        elif dest_type == 'syslog':
            return self._create_syslog_handler(dest_config)
        
        return None
    
    def _create_file_handler(self, config: Dict[str, Any]) -> logging.Handler:
        """Create a file handler with rotation."""
        from logging.handlers import RotatingFileHandler
        
        log_path = config.get('path', '/var/log/secure-it-starlink/app.log')
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        # Parse max size (e.g., "100MB")
        max_size_str = config.get('max_size', '100MB')
        max_bytes = self._parse_size(max_size_str)
        
        backup_count = config.get('backup_count', 30)
        
        handler = RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        
        # Set formatter
        formatter = self._get_formatter()
        handler.setFormatter(formatter)
        
        return handler
    
    def _create_console_handler(self, config: Dict[str, Any]) -> Optional[logging.Handler]:
        """Create a console handler."""
        if not config.get('enabled', True):
            return None
        
        handler = logging.StreamHandler()
        
        # Set log level
        level = config.get('level', 'INFO')
        handler.setLevel(self._get_log_level(level))
        
        # Set formatter
        formatter = self._get_formatter()
        handler.setFormatter(formatter)
        
        return handler
    
    def _create_syslog_handler(self, config: Dict[str, Any]) -> Optional[logging.Handler]:
        """Create a syslog handler."""
        if not config.get('enabled', False):
            return None
        
        from logging.handlers import SysLogHandler
        
        host = config.get('host', 'localhost')
        port = config.get('port', 514)
        
        handler = SysLogHandler(address=(host, port))
        
        formatter = self._get_formatter()
        handler.setFormatter(formatter)
        
        return handler
    
    def _get_formatter(self) -> logging.Formatter:
        """Get the appropriate formatter based on configuration."""
        log_format = self.structured_config.get('format', 'json')
        
        if log_format == 'json':
            return CustomJsonFormatter(
                include_hostname=self.structured_config.get('include_hostname', True),
                include_process_id=self.structured_config.get('include_process_id', True)
            )
        else:
            # Standard text format
            return logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    def _get_log_level(self, level_str: str) -> int:
        """Convert log level string to logging constant."""
        return getattr(logging, level_str.upper(), logging.INFO)
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string (e.g., '100MB') to bytes."""
        size_str = size_str.upper().strip()
        
        try:
            if size_str.endswith('KB'):
                return int(size_str[:-2]) * 1024
            elif size_str.endswith('MB'):
                return int(size_str[:-2]) * 1024 * 1024
            elif size_str.endswith('GB'):
                return int(size_str[:-2]) * 1024 * 1024 * 1024
            else:
                return int(size_str)
        except (ValueError, TypeError):
            # Default to 100MB if parsing fails
            return 100 * 1024 * 1024
    
    def log(self, level: str, message: str, **kwargs):
        """
        Log a message with optional correlation.
        
        Args:
            level: Log level (debug, info, warning, error, critical)
            message: Log message
            **kwargs: Additional fields to include in the log
        """
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        
        # Add event to correlator if it's an event
        if kwargs.get('event_type'):
            incident = self.correlator.add_event(kwargs)
            if incident:
                # Log the correlated incident
                self.logger.warning(
                    f"Correlated incident detected: {incident['incident_type']}",
                    extra={'incident': incident}
                )
        
        # Log the message
        log_method(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.log('debug', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.log('info', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.log('warning', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.log('error', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.log('critical', message, **kwargs)
    
    def get_logger(self) -> logging.Logger:
        """Get the underlying logger instance."""
        return self.logger
    
    def get_correlated_events(self, timeframe: int = 3600) -> List[Dict[str, Any]]:
        """
        Get correlated events.
        
        Args:
            timeframe: Timeframe in seconds
            
        Returns:
            List of correlated incidents
        """
        return self.correlator.get_correlated_events(timeframe)
