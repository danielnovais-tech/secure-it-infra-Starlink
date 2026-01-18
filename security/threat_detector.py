"""
ThreatDetector module - Detects security threats and anomalies
"""

import asyncio
import random
from datetime import datetime
import aiohttp
from .types import THREAT_INTELLIGENCE_FEED_LIMIT, THREAT_SIMULATION_PROBABILITY
from .logging_utils import StructuredLogger
from .metrics import PerformanceTimer

# Exponential backoff constants for resilience
FEED_BASE_SLEEP_TIME = 300  # Base sleep time in seconds for failed feeds
FEED_MAX_SLEEP_TIME = 3600  # Maximum sleep time in seconds (1 hour)
FEED_MAX_BACKOFF_EXPONENT = 4  # Maximum exponent for backoff calculation


class ThreatDetector:
    """Detect security threats and anomalies with resilience features."""
    
    def __init__(self, foundation):
        self.foundation = foundation
        self.threat_intelligence = set()
        self.last_feed_update = None
        self.logger = StructuredLogger(__name__)
        self.feed_failures = 0  # Track consecutive failures for resilience
    
    def initialize(self) -> bool:
        """Initialize threat detector."""
        self.logger.info("Initializing Threat Detector", component="threat_detector")
        asyncio.create_task(self.update_threat_intelligence())
        return True
    
    async def start(self):
        """Start threat detection."""
        self.logger.info("Starting Threat Detector", component="threat_detector")
        
        while self.foundation.running:
            try:
                await self.scan_for_threats()
                await self.analyze_logs()
                await asyncio.sleep(self.foundation.config['monitoring']['threat_check_interval'])
            except Exception as e:
                self.logger.error(f"Threat detector error: {e}", component="threat_detector")
                self.foundation.metrics.record_error('threat_detector_error')
                await asyncio.sleep(30)
    
    async def update_threat_intelligence(self):
        """Update threat intelligence feeds with resilience and fallback."""
        while self.foundation.running:
            try:
                with PerformanceTimer(self.foundation.metrics, 'threat_feed_update'):
                    feeds = self.foundation.config['security']['threat_intelligence_feeds']
                    successful_feeds = 0
                    
                    for feed_url in feeds:
                        async with aiohttp.ClientSession() as session:
                            try:
                                timeout = aiohttp.ClientTimeout(total=10)
                                async with session.get(feed_url, timeout=timeout) as response:
                                    if response.status == 200:
                                        content = await response.text()
                                        # Parse and add to intelligence set
                                        lines = content.split('\n')
                                        for line in lines[:THREAT_INTELLIGENCE_FEED_LIMIT]:
                                            if line and not line.startswith('#'):
                                                self.threat_intelligence.add(line.strip())
                                        successful_feeds += 1
                            except asyncio.TimeoutError:
                                self.logger.warning(
                                    f"Feed timeout: {feed_url}",
                                    component="threat_detector",
                                    feed_url=feed_url
                                )
                                self.foundation.metrics.record_error('feed_timeout')
                            except Exception as e:
                                self.logger.debug(
                                    f"Failed to fetch feed {feed_url}: {e}",
                                    component="threat_detector",
                                    feed_url=feed_url,
                                    error=str(e)
                                )
                                self.foundation.metrics.record_error('feed_fetch_error')
                    
                    # Track feed health for resilience
                    if successful_feeds == 0:
                        self.feed_failures += 1
                        self.logger.warning(
                            f"All threat feeds failed (consecutive failures: {self.feed_failures})",
                            component="threat_detector",
                            consecutive_failures=self.feed_failures
                        )
                    else:
                        self.feed_failures = 0
                    
                    self.last_feed_update = datetime.now()
                    self.logger.info(
                        f"Updated threat intelligence: {len(self.threat_intelligence)} indicators",
                        component="threat_detector",
                        indicator_count=len(self.threat_intelligence),
                        successful_feeds=successful_feeds,
                        total_feeds=len(feeds)
                    )
                
                # Use exponential backoff if feeds are failing
                if self.feed_failures == 0:
                    sleep_time = FEED_MAX_SLEEP_TIME
                else:
                    backoff_exponent = min(self.feed_failures, FEED_MAX_BACKOFF_EXPONENT)
                    sleep_time = min(FEED_MAX_SLEEP_TIME, FEED_BASE_SLEEP_TIME * (2 ** backoff_exponent))
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(
                    f"Threat intelligence update failed: {e}",
                    component="threat_detector",
                    error=str(e)
                )
                self.foundation.metrics.record_error('threat_intelligence_update_error')
                await asyncio.sleep(300)
    
    async def scan_for_threats(self):
        """Scan for known threats with performance tracking."""
        try:
            with PerformanceTimer(self.foundation.metrics, 'threat_scan'):
                # Simulate threat detection
                if random.random() < THREAT_SIMULATION_PROBABILITY:
                    threat_types = ["suspicious_traffic", "malware_indicator", "brute_force_attempt"]
                    threat = random.choice(threat_types)
                    
                    self.foundation.active_threats.add(threat)
                    
                    await self.foundation.trigger_event(
                        "threat_detected",
                        "high" if threat == "malware_indicator" else "medium",
                        "threat_detector",
                        f"Detected potential threat: {threat}",
                        {"threat_type": threat, "indicators": ["simulated_indicator"]}
                    )
        except Exception as e:
            self.logger.error(f"Threat scan failed: {e}", component="threat_detector")
            self.foundation.metrics.record_error('threat_scan_error')
    
    async def analyze_logs(self):
        """Analyze system logs for security events with proper error handling."""
        try:
            with PerformanceTimer(self.foundation.metrics, 'log_analysis'):
                # Check auth logs for failed attempts
                try:
                    with open('/var/log/auth.log', 'r') as f:
                        lines = f.readlines()[-50:]  # Last 50 lines
                        
                        failed_attempts = sum(1 for line in lines if "Failed password" in line)
                        
                        if failed_attempts > 10:
                            await self.foundation.trigger_event(
                                "brute_force_suspected",
                                "high",
                                "threat_detector",
                                f"Multiple failed login attempts: {failed_attempts}",
                                {"failed_attempts": failed_attempts}
                            )
                except FileNotFoundError:
                    pass  # File might not exist on all systems
                except PermissionError:
                    self.logger.debug("Permission denied accessing auth.log", component="threat_detector")
                except IOError as e:
                    self.logger.debug(f"I/O error reading auth.log: {e}", component="threat_detector")
                    
        except Exception as e:
            self.logger.error(f"Log analysis failed: {e}", component="threat_detector")
            self.foundation.metrics.record_error('log_analysis_error')
