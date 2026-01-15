#!/usr/bin/env python3
"""
Starlink Security Foundation
Security monitoring system for Starlink infrastructure

This is the main entry point that provides backward compatibility
while using the new modular architecture.
"""

import asyncio
from security import (
    SecurityLevel,
    StarlinkSecurityFoundation,
    NetworkMonitor,
    ThreatDetector,
    PolicyEnforcer
)

# Re-export for backward compatibility
__all__ = [
    'SecurityLevel',
    'StarlinkSecurityFoundation', 
    'NetworkMonitor',
    'ThreatDetector',
    'PolicyEnforcer'
]


async def main():
    """Main entry point."""
    foundation = StarlinkSecurityFoundation()
    
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


if __name__ == "__main__":
    asyncio.run(main())
