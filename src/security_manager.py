"""Security Manager - Main orchestration class for security monitoring."""
import asyncio
import importlib
import logging
from typing import Dict, Any, List, Optional, Protocol
from datetime import datetime

from security_modules import PolicyEnforcer, IncidentResponder

# NOTE:
# Pylance reports `SecurityEvent` as an unknown symbol when imported from the
# `security_modules` package directly (e.g., when it is defined in a submodule
# but not re-exported in `security_modules/__init__.py`). To keep this module
# working regardless of where `SecurityEvent` is defined, resolve it dynamically.
_SECURITY_EVENT_IMPORT_CANDIDATES = (
    "security_modules.security_event",
    "security_modules.events",
    "security_modules.models",
    "security_modules",  # fallback if it is actually exported here
)

# NOTE: Typed as `Any` so static analyzers don't treat it as `Optional`.
# A runtime guard below ensures we fail fast if it cannot be resolved.
SecurityEvent: Any = None  # will be replaced with the actual class
for _mod_name in _SECURITY_EVENT_IMPORT_CANDIDATES:
    try:
        _mod = importlib.import_module(_mod_name)
        SecurityEvent = getattr(_mod, "SecurityEvent")
        break
    except (ImportError, AttributeError):
        continue

if SecurityEvent is None:
    raise ImportError(
        "Could not import 'SecurityEvent' from security_modules. "
        "Expected it in one of: " + ", ".join(_SECURITY_EVENT_IMPORT_CANDIDATES)
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecurityEventLike(Protocol):
    """Structural type for security events.

    This avoids using the runtime-resolved `SecurityEvent` variable in type
    annotations (which Pylance disallows), while still documenting the expected
    event shape.
    """

    event_type: str
    severity: str
    source: str
    timestamp: datetime
    description: str
    metadata: Optional[Dict[str, Any]]


class SecurityManager:
    """Main security manager orchestrating security modules."""
    
    def __init__(self):
        """Initialize the security manager."""
        self.security_modules: Dict[str, Any] = {
            'policy_enforcer': PolicyEnforcer(),
            'incident_responder': IncidentResponder()
        }
        self.events_queue: asyncio.Queue = asyncio.Queue()
        self.event_log: List[SecurityEventLike] = []
        self.running = False
    
    async def start(self):
        """Start the security manager."""
        logger.info("Starting Security Manager")
        self.running = True
        
        # Start event processing loop
        asyncio.create_task(self._event_processing_loop())
    
    async def stop(self):
        """Stop the security manager."""
        logger.info("Stopping Security Manager")
        self.running = False
    
    async def _event_processing_loop(self):
        """Continuous event processing loop."""
        while self.running:
            await self._process_events()
            await asyncio.sleep(0.1)  # Small delay to prevent busy-waiting
    
    async def adjust_security_level(self, new_level: str):
        """Adjust security level based on threat assessment.
        
        Args:
            new_level: New security level to apply
        """
        logger.info(f"Adjusting security level to: {new_level}")
        
        # Apply new security policies
        await self.security_modules['policy_enforcer'].apply_security_level(new_level)
    
    async def _process_events(self):
        """Process queued security events."""
        try:
            while not self.events_queue.empty():
                event = await self.events_queue.get()
                await self._handle_event(event)
        except Exception as e:
            logger.error(f"Error processing events: {e}")
    
    async def _handle_event(self, event: SecurityEventLike):
        """Handle a security event."""
        # Log the event
        self._log_event(event)
        
        # Take action based on event type and severity
        if event.severity in ["critical", "high"]:
            await self.security_modules['incident_responder'].handle_incident(event)
    
    def _log_event(self, event: SecurityEventLike):
        """Log a security event.
        
        Args:
            event: SecurityEvent to log
        """
        self.event_log.append(event)
        logger.info(f"Event logged: {event.event_type} - {event.severity} - {event.description}")
    
    def add_event(self, event: SecurityEventLike):
        """Add a security event to the queue.
        
        Args:
            event: SecurityEvent to add
        """
        self.events_queue.put_nowait(event)
        logger.debug(f"Event queued: {event.event_type}")
    
    def create_and_queue_event(
        self,
        event_type: str,
        severity: str,
        source: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Create and queue a security event.
        
        Args:
            event_type: Type of the event
            severity: Severity level
            source: Source of the event
            description: Description of the event
            metadata: Additional metadata
        """
        if SecurityEvent is None:
            raise RuntimeError(
                "SecurityEvent class was not resolved. This should have been caught at import time."
            )
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            source=source,
            timestamp=datetime.now(),
            description=description,
            metadata=metadata
        )
        self.add_event(event)
    
    def get_event_log(self) -> List[SecurityEventLike]:
        """Get the event log.
        
        Returns:
            List of logged events
        """
        return self.event_log.copy()
    
    def get_incidents(self) -> List[SecurityEventLike]:
        """Get list of handled incidents.
        
        Returns:
            List of incidents
        """
        return self.security_modules['incident_responder'].incidents.copy()
