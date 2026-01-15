"""
Starlink Security Foundation Module

Foundation for securing enterprise infrastructures using Starlink connectivity.
Provides monitoring, enforcement, and response capabilities.
"""

import hashlib
import json
import logging
import os
import pickle
import queue
import threading
import time
import warnings
from abc import ABC, abstractmethod
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
        
        # Load last hash if file exists
        if self.audit_file.exists():
            try:
                with open(self.audit_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_entry = json.loads(lines[-1])
                        self.last_hash = last_entry.get("hash", self.last_hash)
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


class StarlinkSecurityFoundation:
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
            
            with open(self._state_file, 'wb') as f:
                pickle.dump(state, f)
            
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
            with open(self._state_file, 'rb') as f:
                state = pickle.load(f)
            
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
        Check if a role has a specific permission.
        
        Args:
            permission: Permission to check
            role: Role to check (defaults to admin for backward compatibility)
            
        Returns:
            True if permitted, False otherwise
        """
        if not self._rbac_enabled:
            return True  # Always allow if RBAC disabled
        
        return permission in self._permissions.get(role, set())
    
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
        formatter = formatter or self.audit_formatters[0]
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
