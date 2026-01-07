"""
Tests for Bandwidth Optimizer Module
"""

import pytest
from datetime import datetime
from starlink_security.bandwidth_optimizer import (
    BandwidthOptimizer,
    CompressionLevel,
    Priority,
    QueuedOperation,
    BandwidthBudget
)


def test_bandwidth_optimizer_initialization():
    """Test bandwidth optimizer initialization"""
    optimizer = BandwidthOptimizer(
        bandwidth_limit_mbps=100.0,
        enable_compression=True,
        enable_caching=True,
        enable_deferred_ops=True
    )
    
    assert optimizer.bandwidth_limit == 100.0
    assert optimizer.compression_enabled is True
    assert optimizer.caching_enabled is True


def test_compression_ratio():
    """Test compression ratio calculation"""
    optimizer = BandwidthOptimizer()
    
    optimizer.set_compression_level(CompressionLevel.NONE)
    assert optimizer.get_compression_ratio() == 1.0
    
    optimizer.set_compression_level(CompressionLevel.MEDIUM)
    assert optimizer.get_compression_ratio() == 0.6
    
    optimizer.set_compression_level(CompressionLevel.MAXIMUM)
    assert optimizer.get_compression_ratio() == 0.25


def test_caching():
    """Test response caching"""
    optimizer = BandwidthOptimizer()
    
    # Cache a response
    optimizer.cache_response("test_key", {"data": "value"}, ttl_seconds=3600)
    
    # Retrieve cached response
    cached = optimizer.get_cached_response("test_key")
    assert cached is not None
    assert cached["data"] == "value"
    
    # Non-existent key
    missing = optimizer.get_cached_response("missing_key")
    assert missing is None


def test_cache_hit_rate():
    """Test cache hit rate calculation"""
    optimizer = BandwidthOptimizer()
    
    optimizer.cache_response("key1", "value1")
    
    # Hit
    optimizer.get_cached_response("key1")
    
    # Miss
    optimizer.get_cached_response("key2")
    
    hit_rate = optimizer.get_cache_hit_rate()
    assert hit_rate == 0.5  # 1 hit, 1 miss


def test_operation_queueing():
    """Test queuing operations"""
    optimizer = BandwidthOptimizer()
    
    operation = QueuedOperation(
        operation_id="test_op_1",
        priority=Priority.LOW,
        estimated_bandwidth_mb=50.0,
        queued_at=datetime.now(),
        execute_after=None,
        operation_type="log_upload"
    )
    
    optimizer.queue_operation(operation)
    assert optimizer.get_queued_operations_count() == 1


def test_bandwidth_budget_calculation():
    """Test bandwidth budget calculation"""
    optimizer = BandwidthOptimizer()
    
    budget = optimizer.calculate_bandwidth_budget(
        total_bandwidth_mbps=100.0,
        security_percent=10.0
    )
    
    assert isinstance(budget, BandwidthBudget)
    assert budget.total_mbps == 100.0
    assert budget.security_ops_mbps > 0
    assert budget.logging_mbps > 0


def test_can_execute_operation():
    """Test operation execution check"""
    optimizer = BandwidthOptimizer(bandwidth_limit_mbps=100.0)
    
    # Should be able to execute small operation
    can_execute = optimizer.can_execute_operation(10.0)
    assert can_execute is True
    
    # Should not be able to execute operation exceeding limit
    can_execute = optimizer.can_execute_operation(150.0)
    assert can_execute is False


def test_optimization_summary():
    """Test getting optimization summary"""
    optimizer = BandwidthOptimizer()
    
    summary = optimizer.get_optimization_summary()
    
    assert "total_data_mb" in summary
    assert "bandwidth_saved_mb" in summary
    assert "cache_hit_rate" in summary
    assert "compression_level" in summary


def test_metrics_recording():
    """Test recording bandwidth metrics"""
    optimizer = BandwidthOptimizer()
    
    optimizer.record_metrics(data_sent_mb=100.0, data_received_mb=50.0)
    
    summary = optimizer.get_optimization_summary()
    assert summary["total_data_mb"] == 150.0
