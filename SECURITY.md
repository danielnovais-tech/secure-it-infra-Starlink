# Security Best Practices

This document outlines security best practices for the Starlink Connection Metrics system.

## Configuration Protection

### Threshold Configuration

**DO:**

- Store threshold configurations in secure configuration files (e.g., `config.yaml`, `config.json`)
- Use environment variables for sensitive settings
- Implement role-based access control (RBAC) for configuration changes
- Version control configuration files with proper access controls
- Validate all configuration inputs

**DON'T:**

- Hard-code thresholds in application code
- Allow unauthenticated users to modify thresholds
- Store sensitive configuration in public repositories
- Skip input validation

### Example Secure Configuration

```python
import os
import json
from pathlib import Path

def load_secure_config():
    """Load configuration from secure location with validation."""
    config_path = os.getenv('STARLINK_CONFIG_PATH', '/etc/starlink/config.json')
    
    # Verify file permissions (should be 600 or 400)
    path = Path(config_path)
    if path.exists():
        stat_info = path.stat()
        if stat_info.st_mode & 0o077:  # Check if group/others have permissions
            raise SecurityError(f"Config file {config_path} has insecure permissions")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Validate configuration
    validate_config(config)
    
    return config

def validate_config(config):
    """Validate configuration values."""
    # Validate quality thresholds
    if 'quality_thresholds' in config:
        qt = config['quality_thresholds']
        assert 0 <= qt.get('packet_loss_threshold', 5) <= 100
        assert qt.get('packet_loss_penalty', 10) >= 0
        assert qt.get('latency_threshold', 150) >= 0
        assert qt.get('latency_penalty', 5) >= 0
    
    # Validate stability thresholds
    if 'stability_thresholds' in config:
        st = config['stability_thresholds']
        assert st.get('max_latency', 500) > 0
        assert 0 <= st.get('packet_loss_weight', 0.7) <= 1
        assert 0 <= st.get('latency_weight', 0.3) <= 1
        weights = st.get('packet_loss_weight', 0.7) + st.get('latency_weight', 0.3)
        assert abs(weights - 1.0) < 0.01
```

## Input Validation

The system already includes comprehensive input validation:

### ConnectionMetrics Validation

```python
# Automatically validates:
# - packet_loss: must be 0-100
# - latency: must be non-negative

metrics = ConnectionMetrics(packet_loss=150.0, latency=-10.0)
# Raises ValueError
```

### Threshold Validation

```python
# QualityThresholds validation
QualityThresholds(
    packet_loss_threshold=150.0  # Invalid: must be 0-100
)
# Raises ValueError

# StabilityThresholds validation
StabilityThresholds(
    packet_loss_weight=0.6,
    latency_weight=0.6  # Invalid: weights must sum to 1.0
)
# Raises ValueError

# AlertThresholds validation
AlertThresholds(
    critical_stability=0.7,
    degraded_stability=0.5,
    stable_stability=0.3  # Invalid: must be ascending order
)
# Raises ValueError
```

## Logging and Monitoring Security

### Structured Logging

When using structured logging for SIEM integration:

**DO:**

- Sanitize log data to prevent log injection attacks
- Avoid logging sensitive information (credentials, PII)
- Use proper log levels (INFO, WARNING, ERROR, CRITICAL)
- Implement log rotation and retention policies
- Monitor for anomalous log patterns

**DON'T:**

- Log raw user input without sanitization
- Include sensitive data in logs
- Use debug logging in production
- Ignore log security alerts

### Example Secure Logging

```python
import re
from observability import StructuredLogger

def sanitize_log_data(data):
    """Sanitize data before logging."""
    # Remove potential injection attempts
    if isinstance(data, str):
        # Remove control characters
        data = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', data)
    elif isinstance(data, dict):
        return {k: sanitize_log_data(v) for k, v in data.items()}
    return data

logger = StructuredLogger("production")

# Safe logging
alert_data = {
    "stability": 0.25,
    "service_level": "Critical",
    "packet_loss": 35.0,
    "latency": 450.0
}
sanitized_data = sanitize_log_data(alert_data)
logger.log_alert("critical", sanitized_data)
```

## Alert Callback Security

### Preventing Callback Abuse

**DO:**

- Validate callback functions before registration
- Implement timeout mechanisms for callbacks
- Use try-except blocks to prevent callback crashes
- Rate-limit alert callbacks
- Log all callback executions

**DON'T:**

- Allow arbitrary code execution in callbacks
- Block the main thread with long-running callbacks
- Ignore callback exceptions
- Allow infinite callback loops

### Example Secure Alert Handler

```python
import time
from functools import wraps

def rate_limit(max_calls=10, time_window=60):
    """Rate limiter decorator for alert callbacks."""
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls outside window
            calls[:] = [t for t in calls if now - t < time_window]
            
            if len(calls) >= max_calls:
                print(f"Rate limit exceeded for {func.__name__}")
                return
            
            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_calls=10, time_window=60)
def secure_alert_handler(level, data):
    """Secure alert handler with timeout and error handling."""
    try:
        # Set timeout for alert processing
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Alert processing timeout")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)  # 5 second timeout
        
        try:
            # Process alert safely
            if level == "critical":
                # Trigger failover mechanism
                trigger_failover_safely(data)
            elif level == "degraded":
                # Send notification
                send_notification_safely(data)
        finally:
            signal.alarm(0)  # Cancel timeout
            
    except TimeoutError:
        print("Alert processing timed out")
    except Exception as e:
        print(f"Error in alert handler: {e}")
        # Log error but don't crash
```

## Metrics Export Security

### Prometheus Export

**DO:**

- Use TLS for Prometheus scraping endpoints
- Implement authentication for /metrics endpoint
- Rate-limit metric scrapes
- Validate label values to prevent injection

**DON'T:**

- Expose metrics publicly without authentication
- Include sensitive data in metric labels
- Allow unlimited scrape frequency

### CloudWatch Export

**DO:**

- Use IAM roles with least privilege
- Encrypt data in transit (HTTPS)
- Validate metric data before sending
- Implement retry logic with exponential backoff
- Monitor CloudWatch API costs

**DON'T:**

- Use long-term access keys in code
- Send unvalidated data to CloudWatch
- Ignore API errors
- Exceed CloudWatch API limits

### Example Secure CloudWatch Export

```python
import boto3
from botocore.exceptions import ClientError

def secure_cloudwatch_export(status, region='us-east-1'):
    """Securely export metrics to CloudWatch."""
    # Use IAM role (no credentials in code)
    cloudwatch = boto3.client('cloudwatch', region_name=region)
    
    exporter = MetricsExporter()
    metric_data = exporter.export_cloudwatch(status)
    
    try:
        response = cloudwatch.put_metric_data(**metric_data)
        return response
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'Throttling':
            # Implement backoff
            time.sleep(2)
            return secure_cloudwatch_export(status, region)
        else:
            print(f"CloudWatch error: {e}")
            return None
```

## Audit and Compliance

### Audit Trail

Maintain audit trails for:

- Configuration changes
- Threshold modifications
- Alert triggers
- Status changes
- Access attempts

### Example Audit Logging

```python
import logging
import json
from datetime import datetime

audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

def log_config_change(user, old_config, new_config):
    """Log configuration changes for audit."""
    audit_event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": "config_change",
        "user": user,
        "old_config": old_config,
        "new_config": new_config,
        "ip_address": get_client_ip()
    }
    audit_logger.info(json.dumps(audit_event))
```

## Network Security

### Failover Security

When implementing automatic failover:

**DO:**

- Use secure communication channels (TLS)
- Verify failover target before switching
- Implement circuit breakers
- Log all failover events
- Have manual override capability
- Test failover regularly

**DON'T:**

- Failover without verification
- Create failover loops
- Ignore failover failures
- Disable security during failover

## Summary Checklist

- [ ] Configuration stored securely with proper permissions
- [ ] Input validation on all user-provided data
- [ ] Alert callbacks implement timeout and error handling
- [ ] Logging sanitizes data and excludes sensitive information
- [ ] Metrics export uses authentication and encryption
- [ ] Audit trail maintained for critical operations
- [ ] Regular security reviews and updates
- [ ] Penetration testing of alert/failover mechanisms
- [ ] Incident response plan documented
- [ ] Security monitoring and alerting configured

## Resources

- OWASP Top 10: [https://owasp.org/www-project-top-ten/](https://owasp.org/www-project-top-ten/)
- CWE/SANS Top 25: [https://cwe.mitre.org/top25/](https://cwe.mitre.org/top25/)
- NIST Cybersecurity Framework: [https://www.nist.gov/cyberframework](https://www.nist.gov/cyberframework)
- AWS Security Best Practices: [https://aws.amazon.com/security/best-practices/](https://aws.amazon.com/security/best-practices/)