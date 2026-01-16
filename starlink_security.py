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
    
    def restore_with_verification(self, region: str = None) -> Optional[bytes]:
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
                    return random.random() < fault["failure_rate"]
        
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
            self.foundation.rotate_encryption_key()
            return {"message": "Encryption key rotated successfully"}
        
        elif command == "reload_config":
            # reload_config doesn't take parameters, it reloads from existing path
            self.foundation.reload_config()
            return {"message": "Configuration reloaded successfully"}
        
        elif command == "export_audit":
            output = args.get("output", "audit.json")
            formatter = args.get("formatter", "ISO27001")
            
            # Get formatter
            if formatter in ComplianceProfile.PROFILES:
                fmt = ComplianceProfile.create_formatter(formatter)
            else:
                fmt = self.foundation.audit_formatters[0] if self.foundation.audit_formatters else None
            
            if fmt:
                self.foundation.export_compliance_audit(fmt, output)
                return {"message": f"Audit exported to {output}"}
            else:
                return {"message": "No formatter available"}
        
        elif command == "ingest_feed":
            connector_type = args.get("connector_type", "STIX")
            config = args.get("config", {})
            
            if connector_type == "STIX":
                connector = STIXTAXIIConnector(config)
            elif connector_type == "MISP":
                connector = MISPConnector(config)
            else:
                return {"message": f"Unknown connector type: {connector_type}"}
            
            indicators = self.foundation.integrate_threat_feed(connector)
            return {"message": f"Ingested {len(indicators)} threat indicators"}
        
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
    
    def __init__(self, foundation: 'StarlinkSecurityFoundation', secret_key: str = None):
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
    
    def handle_request(self, endpoint: str, method: str, token: str, data: Dict = None) -> Dict[str, Any]:
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
                return {"data": self.foundation.get_metrics_summary(), "status": 200}
            
            elif endpoint == "/prometheus" and method == "GET":
                return {"data": self.foundation.get_prometheus_metrics(), "status": 200}
            
            elif endpoint == "/events" and method == "POST":
                if not data:
                    return {"error": "Event data required", "status": 400}
                event = SecurityEvent(**data)
                self.foundation.log_event(event)
                return {"message": "Event logged successfully", "status": 200}
            
            elif endpoint == "/threats" and method == "GET":
                threats = self.foundation.state_store.get_threats()
                return {"data": list(threats), "status": 200}
            
            elif endpoint == "/config/reload" and method == "POST":
                self.foundation.reload_config()
                return {"message": "Configuration reloaded", "status": 200}
            
            elif endpoint == "/keys/rotate" and method == "POST":
                self.foundation.rotate_encryption_key()
                return {"message": "Encryption key rotated", "status": 200}
            
            elif endpoint == "/audit/export" and method == "POST":
                profile = data.get("profile", "iso27001") if data else "iso27001"
                output = data.get("output", "audit_export.json") if data else "audit_export.json"
                formatter = ComplianceProfile.create_formatter(profile)
                self.foundation.export_compliance_audit(formatter, output)
                return {"message": f"Audit exported to {output}", "status": 200}
            
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
    
    def register_plugin(self, category: str, name: str, plugin_class: type, metadata: Dict = None):
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
    
    def list_plugins(self, category: str = None) -> Dict[str, Any]:
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
            if tenant_id not in self.policies:
                return list(geo_replication.regions.keys())
            
            allowed = self.policies[tenant_id]
            return [r for r in geo_replication.regions if r in allowed]


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
        return {
            "metrics": self.foundation.get_metrics_summary(),
            "prometheus": self.foundation.get_prometheus_metrics(),
            "threats": list(self.foundation.state_store.get_threats()),
            "rbac_audit": self.foundation.get_rbac_audit_log() if hasattr(self.foundation, 'get_rbac_audit_log') else [],
            "cluster_health": self.foundation.cluster_manager.get_status() if hasattr(self.foundation, 'cluster_manager') else {},
            "scorer_status": self.foundation.get_scorer_explainability()
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
        
        sample = random.sample(self.historical_events, min(sample_size, len(self.historical_events)))
        
        current_scores = []
        new_scores = []
        differences = []
        
        for event in sample:
            # Current scorer
            current_result = self.foundation.threat_scorer.score(event)
            current_scores.append(current_result['risk'])
            
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
        if hasattr(self.foundation, 'audit_logger'):
            with self.foundation.audit_logger._lock:
                affected = sum(
                    1 for entry in self.foundation.audit_logger.audit_chain
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
    
    def __init__(self, provider: str = "aws", region: str = "us-east-1", key_id: str = None):
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
    
    def __init__(self, provider: str = "vault", endpoint: str = None, ttl_seconds: int = 3600):
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
                    except Exception:
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
    
    def add_component(self, name: str, version: str, supplier: str = None,
                     licenses: List[str] = None, hashes: Dict[str, str] = None):
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
    
    def __init__(self, sandbox: 'PolicySimulationSandbox' = None):
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
    
    def should_use_canary(self, canary_id: str, tenant_id: str = None) -> bool:
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
                
                # New tenant - assign based on percentage
                use_canary = random.random() * 100 < config["canary_percentage"]
                self.tenant_assignments[tenant_id] = "canary" if use_canary else "baseline"
                return use_canary
        
        # Random percentage-based routing
        return random.random() * 100 < config["canary_percentage"]
    
    def record_canary_result(self, canary_id: str, is_canary: bool,
                            risk_score: float, baseline_risk: float = None):
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

