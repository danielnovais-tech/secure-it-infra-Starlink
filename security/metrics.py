"""
Performance metrics tracking for Starlink Security Foundation
"""

import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional


class MetricsCollector:
    """Collects and tracks performance metrics."""
    
    def __init__(self):
        self.event_counts: Dict[str, int] = defaultdict(int)
        self.response_times: Dict[str, List[float]] = defaultdict(list)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.start_time = datetime.now(timezone.utc)
    
    def record_event(self, event_type: str):
        """Record an event occurrence."""
        self.event_counts[event_type] += 1
    
    def record_response_time(self, operation: str, duration: float):
        """Record operation response time."""
        self.response_times[operation].append(duration)
    
    def record_error(self, error_type: str):
        """Record an error occurrence."""
        self.error_counts[error_type] += 1
    
    def get_metrics(self) -> Dict:
        """Get current metrics summary."""
        uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        
        avg_response_times = {}
        for op, times in self.response_times.items():
            if times:
                avg_response_times[op] = sum(times) / len(times)
        
        return {
            'uptime_seconds': uptime,
            'event_counts': dict(self.event_counts),
            'avg_response_times': avg_response_times,
            'error_counts': dict(self.error_counts),
            'total_events': sum(self.event_counts.values()),
            'total_errors': sum(self.error_counts.values())
        }
    
    def reset(self):
        """Reset all metrics."""
        self.event_counts.clear()
        self.response_times.clear()
        self.error_counts.clear()
        self.start_time = datetime.now(timezone.utc)


class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, metrics: MetricsCollector, operation: str):
        self.metrics = metrics
        self.operation = operation
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is None:
            return False

        duration = time.time() - self.start_time
        self.metrics.record_response_time(self.operation, duration)
        return False
