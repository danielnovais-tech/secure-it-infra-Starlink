"""
Core StarlinkSecurityFoundation class
"""

import asyncio
from datetime import datetime
from typing import Dict, Set, List, Callable
from .types import SecurityLevel
from .logging_utils import StructuredLogger
from .metrics import MetricsCollector


class StarlinkSecurityFoundation:
    """Main security foundation class with metrics and structured logging."""
    
    def __init__(self, config: Dict = None):
        self.config = config or self._default_config()
        self.running = False
        self.active_threats: Set[str] = set()
        self.security_level = SecurityLevel.NORMAL
        self.event_handlers: List[Callable] = []
        self.logger = StructuredLogger(__name__)
        self.metrics = MetricsCollector()
        
    def _default_config(self) -> Dict:
        """Return default configuration."""
        return {
            'monitoring': {
                'network_scan_interval': 300,
                'threat_check_interval': 60
            },
            'security': {
                'threat_intelligence_feeds': [
                    'https://example.com/threat-feed-1',
                    'https://example.com/threat-feed-2'
                ]
            }
        }
    
    async def trigger_event(self, event_type: str, severity: str, source: str, 
                          message: str, data: Dict = None):
        """Trigger a security event with metrics tracking."""
        event = {
            'type': event_type,
            'severity': severity,
            'source': source,
            'message': message,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Record metrics
        self.metrics.record_event(event_type)
        
        # Structured logging
        self.logger.log_event(
            severity.upper() if severity in ['info', 'warning', 'error'] else 'INFO',
            message,
            event_type=event_type,
            source=source,
            data=data
        )
        
        # Call registered event handlers
        for handler in self.event_handlers:
            try:
                await handler(event)
            except Exception as e:
                self.logger.error(f"Event handler error: {e}", handler=str(handler))
                self.metrics.record_error('event_handler_error')
    
    async def start(self):
        """Start the security foundation."""
        self.running = True
        self.logger.info("Starting Starlink Security Foundation", security_level=self.security_level.value)
        
        # Components will be started externally
        # This allows for better modularity and testing
        
    async def stop(self):
        """Stop the security foundation."""
        self.logger.info("Stopping Starlink Security Foundation")
        self.running = False
    
    def get_metrics(self) -> Dict:
        """Get current performance metrics."""
        return self.metrics.get_metrics()
