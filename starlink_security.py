"""
Starlink Security Foundation Module

Foundation for securing enterprise infrastructures using Starlink connectivity.
Provides monitoring, enforcement, and response capabilities.
"""

import json
import logging
import os
import queue
import threading
import warnings
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
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


class StarlinkSecurityFoundation:
    """
    Foundation for securing enterprise infrastructures using Starlink connectivity.
    Provides monitoring, enforcement, and response capabilities with lifecycle management.
    """
    
    def __init__(self, config_path: Optional[str] = None, 
                 module_factory: Optional[Callable[[str, bool], SecurityModule]] = None):
        """
        Initialize the security foundation.
        
        Args:
            config_path: Path to configuration file (optional)
            module_factory: Factory function for creating security modules (for dependency injection)
            
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
        
        # Module factory for dependency injection
        self._module_factory = module_factory or self._default_module_factory
        self.security_modules: Dict[str, SecurityModule] = {}
        self._initialize_modules()
        
        # Key rotation tracking
        self._key_created_at = datetime.now()
        self._key_rotation_days = self.config.get('key_rotation_days', DEFAULT_KEY_ROTATION_DAYS)
        
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
            for name, module in self.security_modules.items():
                try:
                    module.start()
                    self.logger.info(f"Started module: {name}")
                except Exception as e:
                    self.logger.error(f"Failed to start module {name}: {e}")
            
            self.running = True
            self.logger.info("Starlink Security Foundation started")
    
    def stop(self) -> None:
        """Stop all security modules and cease operations."""
        with self._lock:
            if not self.running:
                self.logger.warning("Not running")
                return
            
            self.logger.info("Stopping Starlink Security Foundation")
            for name, module in self.security_modules.items():
                try:
                    module.stop()
                    self.logger.info(f"Stopped module: {name}")
                except Exception as e:
                    self.logger.error(f"Failed to stop module {name}: {e}")
            
            self.running = False
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
    
    def rotate_encryption_key(self) -> None:
        """
        Rotate the encryption key for security hardening.
        
        Raises:
            IOError: If key rotation fails
        """
        self.logger.info("Rotating encryption key")
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
            self.logger.info("Encryption key rotated successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to rotate encryption key: {e}")
            raise IOError(f"Key rotation failed: {e}") from e
    
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
        Log a security event with thread safety.
        
        Args:
            event: SecurityEvent to log
        """
        with self._lock:
            self.events.append(event)
        
        # Also log to structured logger
        event_data = {
            "event_type": event.event_type,
            "severity": event.severity,
            "source": event.source,
            "description": event.description
        }
        self.logger.info(f"Security event logged: {json.dumps(event_data)}")
    
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
        Add an active threat with thread safety.
        
        Args:
            threat_id: Unique identifier for the threat
        """
        with self._lock:
            self.active_threats.add(threat_id)
        self.logger.warning(f"Threat added: {threat_id}")
    
    def remove_threat(self, threat_id: str) -> None:
        """
        Remove an active threat with thread safety.
        
        Args:
            threat_id: Unique identifier for the threat
        """
        with self._lock:
            self.active_threats.discard(threat_id)
        self.logger.info(f"Threat removed: {threat_id}")
    
    def get_unresolved_events(self) -> List[SecurityEvent]:
        """
        Get all unresolved security events with thread safety.
        
        Returns:
            List of unresolved SecurityEvent objects
        """
        with self._lock:
            return [event for event in self.events if not event.resolved]
