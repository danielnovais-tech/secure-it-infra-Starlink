#!/usr/bin/env python3
"""
Simple test script to verify Secure IT Starlink functionality.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from secure_it_starlink.config import ConfigurationManager
from secure_it_starlink.metrics import MetricsCollector
from secure_it_starlink.automated_responses import AutomatedResponseCoordinator, SeverityLevel
from secure_it_starlink.logging import StructuredLogger


def test_configuration():
    """Test configuration management."""
    print("\n=== Testing Configuration Management ===")
    
    # Test loading default configuration
    config = ConfigurationManager()
    assert config.get('metrics.security.weight') == 0.4
    print("✓ Default configuration loaded")
    
    # Test deep merge
    base = {'a': 1, 'b': {'c': 2, 'd': 3}}
    override = {'b': {'c': 5, 'e': 6}, 'f': 7}
    merged = config.deep_merge(base, override)
    assert merged == {'a': 1, 'b': {'c': 5, 'd': 3, 'e': 6}, 'f': 7}
    print("✓ Deep merge working correctly")
    
    # Test set and get
    config.set('test.nested.value', 100)
    assert config.get('test.nested.value') == 100
    print("✓ Set/Get with dot notation working")
    
    print("✓ Configuration management tests passed!\n")


def test_metrics():
    """Test metrics collection."""
    print("=== Testing Metrics Collection ===")
    
    config = {
        'security': {'weight': 0.4, 'thresholds': {'critical': 90, 'high': 70}},
        'connection': {'weight': 0.3, 'thresholds': {}},
        'performance': {'weight': 0.3, 'thresholds': {}}
    }
    
    collector = MetricsCollector(config)
    
    # Test metrics collection
    metrics = collector.collect_metrics(
        security_data={
            'firewall_status': 95.0,
            'encryption_level': 90.0,
            'authentication_strength': 85.0,
            'vulnerability_count': 92.0,
            'patch_level': 88.0
        },
        connection_data={
            'uptime_percentage': 99.8,
            'packet_loss': 0.1,
            'latency': 25.0,
            'signal_strength': 95.0
        },
        performance_data={
            'throughput_score': 85.0,
            'bandwidth_utilization': 65.0,
            'cpu_usage': 45.0,
            'memory_usage': 60.0,
            'disk_io_usage': 30.0
        }
    )
    
    assert 'composite_score' in metrics
    assert 'security' in metrics
    assert 'connection' in metrics
    assert 'performance' in metrics
    print(f"✓ Metrics collected - Composite Score: {metrics['composite_score']:.2f}")
    print(f"  - Security: {metrics['security']['score']:.2f} ({metrics['security']['level']})")
    print(f"  - Connection: {metrics['connection']['score']:.2f} ({metrics['connection']['level']})")
    print(f"  - Performance: {metrics['performance']['score']:.2f} ({metrics['performance']['level']})")
    
    # Test metrics summary
    summary = collector.get_metrics_summary(3600)
    assert 'averages' in summary
    print("✓ Metrics summary generated")
    
    print("✓ Metrics collection tests passed!\n")


def test_automated_responses():
    """Test automated responses."""
    print("=== Testing Automated Responses ===")
    
    config = {
        'threat_containment': {
            'enabled': True,
            'auto_execute': False,
            'actions': [
                {'type': 'isolate_device', 'cooldown': 300},
                {'type': 'block_ip', 'cooldown': 600}
            ]
        },
        'policy_enforcement': {
            'enabled': True,
            'auto_execute': True,
            'policies': [
                {'name': 'bandwidth_limit', 'condition': 'bandwidth_usage > 90%', 
                 'action': 'throttle_connection', 'threshold': 90}
            ]
        },
        'failover': {
            'enabled': True,
            'auto_execute': True,
            'triggers': [],
            'backup_links': [
                {'name': 'backup_1', 'priority': 1},
                {'name': 'backup_2', 'priority': 2}
            ]
        }
    }
    
    coordinator = AutomatedResponseCoordinator(config)
    
    # Test threat containment
    action = coordinator.threat_containment.isolate_device(
        'device-001',
        SeverityLevel.HIGH,
        'Malware detected'
    )
    assert action.action_type == 'isolate_device'
    print("✓ Threat containment action created")
    
    # Test processing security event
    event = {
        'type': 'security_threat',
        'severity': 'high',
        'device_id': 'device-002',
        'source_ip': '192.168.1.100',
        'reason': 'Intrusion detected',
        'context': {},
        'metrics': {}
    }
    
    actions = coordinator.process_event(event)
    assert len(actions) > 0
    print(f"✓ Security event processed - {len(actions)} actions triggered")
    
    print("✓ Automated responses tests passed!\n")


def test_logging():
    """Test structured logging."""
    print("=== Testing Structured Logging ===")
    
    config = {
        'structured': {
            'enabled': True,
            'format': 'json',
            'level': 'INFO',
            'include_timestamp': True,
            'include_hostname': True,
            'include_process_id': True
        },
        'correlation': {
            'enabled': True,
            'window_size': 300,
            'correlation_fields': ['source_ip', 'user_id'],
            'patterns': [
                {
                    'name': 'brute_force_attack',
                    'events': ['failed_login'],
                    'count': 3,
                    'timeframe': 60
                }
            ]
        },
        'destinations': [
            {
                'type': 'console',
                'enabled': True,
                'level': 'INFO'
            }
        ],
        'levels': {
            'root': 'INFO'
        }
    }
    
    logger = StructuredLogger(config)
    
    # Test basic logging
    logger.info("Test info message", test_field="test_value")
    print("✓ Basic logging working")
    
    # Test event correlation
    for i in range(3):
        logger.warning("Failed login attempt",
                      event_type='failed_login',
                      source_ip='192.168.1.100',
                      user_id='admin')
    
    correlated = logger.get_correlated_events(3600)
    print(f"✓ Event correlation working - {len(correlated)} incidents detected")
    
    print("✓ Structured logging tests passed!\n")


def test_integration():
    """Test full integration."""
    print("=== Testing Full Integration ===")
    
    # Load configuration
    config_manager = ConfigurationManager()
    config = config_manager.get_all()
    
    # Initialize all components
    logger = StructuredLogger(config.get('logging', {}))
    metrics_collector = MetricsCollector(config.get('metrics', {}))
    response_coordinator = AutomatedResponseCoordinator(config.get('automated_responses', {}))
    
    # Simulate a complete monitoring cycle
    logger.info("Starting monitoring cycle")
    
    # Collect metrics
    metrics = metrics_collector.collect_metrics(
        security_data={'firewall_status': 95, 'encryption_level': 90},
        connection_data={'uptime_percentage': 99.5, 'latency': 25},
        performance_data={'cpu_usage': 45, 'memory_usage': 60}
    )
    
    logger.info("Metrics collected", composite_score=metrics['composite_score'])
    
    # Process event
    event = {
        'type': 'metrics_update',
        'metrics': metrics,
        'context': {'security_score': metrics['security']['score']}
    }
    
    actions = response_coordinator.process_event(event)
    logger.info("Event processed", action_count=len(actions))
    
    print("✓ Full integration test passed!\n")


def main():
    """Run all tests."""
    print("\n" + "="*50)
    print("Secure IT Starlink - Functionality Tests")
    print("="*50)
    
    try:
        test_configuration()
        test_metrics()
        test_automated_responses()
        test_logging()
        test_integration()
        
        print("="*50)
        print("✓ ALL TESTS PASSED!")
        print("="*50 + "\n")
        
        return 0
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
