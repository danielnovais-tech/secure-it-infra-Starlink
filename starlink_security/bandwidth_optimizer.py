"""
Bandwidth Optimizer Module

Optimizes security operations for satellite bandwidth constraints,
minimizing data usage while maintaining security effectiveness.
"""

from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta


class CompressionLevel(Enum):
    """Data compression levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


class Priority(Enum):
    """Operation priority levels"""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    BACKGROUND = 4


@dataclass
class BandwidthBudget:
    """Bandwidth allocation budget"""
    total_mbps: float
    security_ops_mbps: float
    logging_mbps: float
    updates_mbps: float
    monitoring_mbps: float
    reserved_mbps: float


@dataclass
class OptimizationMetrics:
    """Bandwidth optimization metrics"""
    timestamp: datetime
    data_sent_mb: float
    data_received_mb: float
    compression_ratio: float
    cached_requests: int
    deferred_operations: int
    bandwidth_saved_mb: float


@dataclass
class QueuedOperation:
    """Queued bandwidth-intensive operation"""
    operation_id: str
    priority: Priority
    estimated_bandwidth_mb: float
    queued_at: datetime
    execute_after: Optional[datetime]
    operation_type: str
    callback: Optional[Callable] = None


class BandwidthOptimizer:
    """
    Optimizes security operations for satellite bandwidth constraints.
    Implements intelligent caching, compression, and deferred operations.
    """
    
    def __init__(self, 
                 bandwidth_limit_mbps: float = 100.0,
                 enable_compression: bool = True,
                 enable_caching: bool = True,
                 enable_deferred_ops: bool = True):
        """
        Initialize bandwidth optimizer
        
        Args:
            bandwidth_limit_mbps: Maximum bandwidth for security operations
            enable_compression: Enable data compression
            enable_caching: Enable response caching
            enable_deferred_ops: Enable deferred non-critical operations
        """
        self.bandwidth_limit = bandwidth_limit_mbps
        self.compression_enabled = enable_compression
        self.caching_enabled = enable_caching
        self.deferred_ops_enabled = enable_deferred_ops
        
        self._compression_level = CompressionLevel.MEDIUM
        self._operation_queue: List[QueuedOperation] = []
        self._cache: Dict[str, Tuple[Any, datetime, int]] = {}  # key -> (data, timestamp, size)
        self._metrics_history: List[OptimizationMetrics] = []
        self._current_usage_mbps = 0.0
        self._cache_hit_count = 0
        self._cache_miss_count = 0
    
    def set_compression_level(self, level: CompressionLevel) -> None:
        """Set data compression level"""
        self._compression_level = level
    
    def get_compression_ratio(self) -> float:
        """
        Get current compression ratio
        
        Returns:
            Compression ratio (e.g., 0.3 means 70% reduction)
        """
        ratios = {
            CompressionLevel.NONE: 1.0,
            CompressionLevel.LOW: 0.85,
            CompressionLevel.MEDIUM: 0.6,
            CompressionLevel.HIGH: 0.4,
            CompressionLevel.MAXIMUM: 0.25,
        }
        return ratios[self._compression_level]
    
    def compress_data(self, data: bytes) -> bytes:
        """
        Compress data based on current compression level
        
        Args:
            data: Data to compress
            
        Returns:
            Compressed data
        """
        if not self.compression_enabled or self._compression_level == CompressionLevel.NONE:
            return data
        
        # Placeholder for actual compression implementation
        # In production, would use gzip, lz4, or zstd based on level
        compression_ratio = self.get_compression_ratio()
        compressed_size = int(len(data) * compression_ratio)
        return data[:compressed_size]  # Simulated compression
    
    def cache_response(self, key: str, data: Any, ttl_seconds: int = 3600) -> None:
        """
        Cache a response to reduce bandwidth usage
        
        Args:
            key: Cache key
            data: Data to cache
            ttl_seconds: Time to live in seconds
        """
        if not self.caching_enabled:
            return
        
        expiry = datetime.now() + timedelta(seconds=ttl_seconds)
        size = len(str(data))  # Simplified size calculation
        self._cache[key] = (data, expiry, size)
        
        # Limit cache size (simple LRU)
        if len(self._cache) > 1000:
            oldest_key = min(self._cache.items(), key=lambda x: x[1][1])[0]
            del self._cache[oldest_key]
    
    def get_cached_response(self, key: str) -> Optional[Any]:
        """
        Get cached response if available and not expired
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        if not self.caching_enabled or key not in self._cache:
            self._cache_miss_count += 1
            return None
        
        data, expiry, size = self._cache[key]
        
        if datetime.now() > expiry:
            del self._cache[key]
            self._cache_miss_count += 1
            return None
        
        self._cache_hit_count += 1
        return data
    
    def get_cache_hit_rate(self) -> float:
        """
        Calculate cache hit rate
        
        Returns:
            Cache hit rate (0.0 to 1.0)
        """
        total = self._cache_hit_count + self._cache_miss_count
        if total == 0:
            return 0.0
        return self._cache_hit_count / total
    
    def queue_operation(self, operation: QueuedOperation) -> None:
        """
        Queue a bandwidth-intensive operation for later execution
        
        Args:
            operation: Operation to queue
        """
        if not self.deferred_ops_enabled:
            # Execute immediately if deferred ops disabled
            if operation.callback:
                operation.callback()
            return
        
        self._operation_queue.append(operation)
        # Sort by priority (lower value = higher priority)
        self._operation_queue.sort(key=lambda x: x.priority.value)
    
    def can_execute_operation(self, bandwidth_required_mbps: float) -> bool:
        """
        Check if operation can be executed within bandwidth budget
        
        Args:
            bandwidth_required_mbps: Required bandwidth in Mbps
            
        Returns:
            True if operation can be executed now
        """
        return (self._current_usage_mbps + bandwidth_required_mbps) <= self.bandwidth_limit
    
    def execute_queued_operations(self, max_operations: int = 5) -> int:
        """
        Execute queued operations that fit within bandwidth budget
        
        Args:
            max_operations: Maximum number of operations to execute
            
        Returns:
            Number of operations executed
        """
        executed = 0
        
        for operation in self._operation_queue[:]:
            if executed >= max_operations:
                break
            
            # Check if operation should be executed now
            if operation.execute_after and datetime.now() < operation.execute_after:
                continue
            
            # Check bandwidth availability
            if not self.can_execute_operation(operation.estimated_bandwidth_mb):
                continue
            
            # Execute operation
            if operation.callback:
                operation.callback()
            
            self._operation_queue.remove(operation)
            executed += 1
        
        return executed
    
    def get_queued_operations_count(self) -> int:
        """Get number of queued operations"""
        return len(self._operation_queue)
    
    def calculate_bandwidth_budget(self, total_bandwidth_mbps: float,
                                   security_percent: float = 10.0) -> BandwidthBudget:
        """
        Calculate bandwidth allocation budget
        
        Args:
            total_bandwidth_mbps: Total available bandwidth
            security_percent: Percentage allocated to security operations
            
        Returns:
            Bandwidth budget allocation
        """
        security_total = total_bandwidth_mbps * (security_percent / 100.0)
        
        return BandwidthBudget(
            total_mbps=total_bandwidth_mbps,
            security_ops_mbps=security_total * 0.4,  # 40% for operations
            logging_mbps=security_total * 0.2,       # 20% for logging
            updates_mbps=security_total * 0.2,       # 20% for updates
            monitoring_mbps=security_total * 0.15,   # 15% for monitoring
            reserved_mbps=security_total * 0.05,     # 5% reserved
        )
    
    def record_metrics(self, data_sent_mb: float, data_received_mb: float) -> None:
        """
        Record bandwidth usage metrics
        
        Args:
            data_sent_mb: Data sent in MB
            data_received_mb: Data received in MB
        """
        compression_ratio = self.get_compression_ratio()
        bandwidth_saved = (data_sent_mb + data_received_mb) * (1 - compression_ratio)
        
        metrics = OptimizationMetrics(
            timestamp=datetime.now(),
            data_sent_mb=data_sent_mb,
            data_received_mb=data_received_mb,
            compression_ratio=compression_ratio,
            cached_requests=self._cache_hit_count,
            deferred_operations=len(self._operation_queue),
            bandwidth_saved_mb=bandwidth_saved,
        )
        
        self._metrics_history.append(metrics)
        
        # Keep only last 24 hours
        if len(self._metrics_history) > 1440:  # Assuming minute-level recording
            self._metrics_history = self._metrics_history[-1440:]
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """
        Get summary of bandwidth optimization effectiveness
        
        Returns:
            Dictionary with optimization metrics
        """
        if not self._metrics_history:
            return {
                'total_data_mb': 0,
                'bandwidth_saved_mb': 0,
                'savings_percentage': 0,
                'cache_hit_rate': 0,
                'queued_operations': 0,
                'compression_level': self._compression_level.value,
            }
        
        total_sent = sum(m.data_sent_mb for m in self._metrics_history)
        total_received = sum(m.data_received_mb for m in self._metrics_history)
        total_saved = sum(m.bandwidth_saved_mb for m in self._metrics_history)
        
        return {
            'total_data_mb': total_sent + total_received,
            'bandwidth_saved_mb': total_saved,
            'savings_percentage': (total_saved / (total_sent + total_received) * 100) 
                                 if (total_sent + total_received) > 0 else 0,
            'cache_hit_rate': self.get_cache_hit_rate(),
            'queued_operations': len(self._operation_queue),
            'compression_level': self._compression_level.value,
        }
    
    def optimize_log_transmission(self, log_data: str, 
                                  priority: Priority = Priority.LOW) -> str:
        """
        Optimize log data for transmission
        
        Args:
            log_data: Log data to optimize
            priority: Log priority level
            
        Returns:
            Optimized log data
        """
        if priority == Priority.CRITICAL or priority == Priority.HIGH:
            # Send immediately, minimal compression
            return log_data
        
        # For lower priority logs, apply more aggressive optimization
        # Remove timestamps if not critical
        # Compress repeated patterns
        # Batch for periodic transmission
        
        return log_data  # Placeholder
