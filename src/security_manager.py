"""Security Manager - Main orchestration class for security monitoring."""
import asyncio
import logging
import queue
from typing import Dict, Any
from datetime import datetime

from security_modules import SecurityEvent, PolicyEnforcer, IncidentResponder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecurityManager:
    """Main security manager orchestrating security modules."""
    
    def __init__(self):
        """Initialize the security manager."""
        self.security_modules: Dict[str, Any] = {
            'policy_enforcer': PolicyEnforcer(),
            'incident_responder': IncidentResponder()
        }
        self.events_queue: queue.Queue = queue.Queue()
        self.event_log: list = []
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
                event = self.events_queue.get_nowait()
                await self._handle_event(event)
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Error processing events: {e}")
    
    async def _handle_event(self, event: SecurityEvent):
        """Handle a security event."""
        # Log the event
        self._log_event(event)
        
        # Take action based on event type and severity
        if event.severity in ["critical", "high"]:
            await self.security_modules['incident_responder'].handle_incident(event)
    
    def _log_event(self, event: SecurityEvent):
        """Log a security event.
        
        Args:
            event: SecurityEvent to log
        """
        self.event_log.append(event)
        logger.info(f"Event logged: {event.event_type} - {event.severity} - {event.description}")
    
    def add_event(self, event: SecurityEvent):
        """Add a security event to the queue.
        
        Args:
            event: SecurityEvent to add
        """
        self.events_queue.put(event)
        logger.debug(f"Event queued: {event.event_type}")
    
    def create_and_queue_event(
        self,
        event_type: str,
        severity: str,
        source: str,
        description: str,
        metadata: Dict[str, Any] = None
    ):
        """Create and queue a security event.
        
        Args:
            event_type: Type of the event
            severity: Severity level
            source: Source of the event
            description: Description of the event
            metadata: Additional metadata
        """
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            source=source,
            timestamp=datetime.now(),
            description=description,
            metadata=metadata
        )
        self.add_event(event)
    
    def get_event_log(self) -> list:
        """Get the event log.
        
        Returns:
            List of logged events
        """
        return self.event_log.copy()
    
    def get_incidents(self) -> list:
        """Get list of handled incidents.
        
        Returns:
            List of incidents
        """
        return self.security_modules['incident_responder'].incidents.copy()
