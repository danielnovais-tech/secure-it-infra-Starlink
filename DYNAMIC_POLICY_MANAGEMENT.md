# Dynamic Policy Management and Audit Trail

Comprehensive guide for runtime policy management with cryptographically signed audit trails.

## Overview

The Dynamic Policy Management system provides:

- **Runtime Policy Reloading**: Update enforcement rules without service restart
- **Cryptographic Audit Trail**: Tamper-evident log of all policy changes
- **Policy Versioning**: Rollback to previous policy versions
- **Compliance Evidence**: Generate auditor-friendly evidence bundles
- **Signal-Based Control**: Reload policies via UNIX signals
- **API-Based Control**: Programmatic policy management

## Architecture

### Components

1. **PolicyManager**: Main orchestrator for policy lifecycle
2. **PolicyAuditTrail**: Maintains append-only, hash-chained audit log
3. **Signal Handlers**: SIGUSR2 triggers policy reload
4. **Thread-Safe Access**: RLock ensures safe concurrent access

### Hash Chain Design

Each policy change is cryptographically linked to the previous change:

```
Genesis (all zeros)
    ↓ (hash link)
Policy Load #1 → hash_1
    ↓ (hash link)
Policy Reload #2 → hash_2
    ↓ (hash link)
Policy Rollback #3 → hash_3
```

Any tampering breaks the chain and is immediately detectable.

## Quick Start

### Basic Usage

```python
from policy_manager import get_policy_manager, reload_policy, get_current_policy

# Get current policy
policy = get_current_policy()
print(f"Enforcement level: {policy['enforcement_level']}")

# Reload policy from disk
reload_policy(reason="Updated PII detection rules")

# Access policy manager for advanced operations
manager = get_policy_manager()
audit_summary = manager.get_audit_summary()
```

### Command-Line Interface

```bash
# Reload current policy
python policy_manager.py reload "Updated for GDPR compliance"

# Rollback 1 version
python policy_manager.py rollback 1 "Reverting problematic update"

# Verify audit trail integrity
python policy_manager.py verify

# Generate compliance evidence
python policy_manager.py evidence policies/audit_evidence.json

# View audit history
python policy_manager.py history 10
```

### Signal-Based Reload

```bash
# Send SIGUSR2 to trigger policy reload
kill -SIGUSR2 <pid>

# Or using killall
killall -SIGUSR2 python
```

## Policy Lifecycle

### 1. Initial Load

When the application starts, the policy manager loads the default policy:

```python
manager = PolicyManager(default_policy_path="policies/privacy_policy_production.json")
```

This creates the first audit entry:

```json
{
  "timestamp": "2026-01-16T22:00:00.000Z",
  "action": "load",
  "policy_path": "policies/privacy_policy_production.json",
  "policy_hash": "abc123...",
  "previous_hash": "0000000000000000...",
  "user": "system",
  "reason": "Initial load at startup",
  "hash": "def456..."
}
```

### 2. Runtime Reload

Update the policy file on disk, then trigger reload:

```python
# API method
reload_policy(reason="Emergency redaction rule added")

# Signal method
os.kill(os.getpid(), signal.SIGUSR2)

# CLI method
# python policy_manager.py reload "Updated PII patterns"
```

### 3. Rollback

If a policy update causes issues, rollback to a previous version:

```python
# Rollback 1 version (most recent)
rollback_policy(steps=1, reason="Reverting overly strict rules")

# Rollback 3 versions
rollback_policy(steps=3, reason="Return to known-good configuration")
```

### 4. Verification

Verify the integrity of the audit trail at any time:

```python
is_valid, errors = verify_audit_trail()

if not is_valid:
    print("ALERT: Audit trail has been tampered with!")
    for error in errors:
        print(f"  - {error}")
```

## Audit Trail Features

### Tamper Detection

The hash chain ensures any modification is immediately detectable:

```python
# Each entry includes:
# 1. Hash of previous entry (linkage)
# 2. Hash of current entry data
# 3. Hash of policy content

entry = {
    'previous_hash': 'abc123...',  # Links to previous
    'policy_hash': 'def456...',     # Content hash
    'hash': 'ghi789...'             # This entry's hash
}
```

If someone modifies entry #5, the hash won't match, and entry #6's `previous_hash` will be invalid.

### Time-Based Queries

Prove which policy was active at any specific time:

```python
# What policy was active on Jan 15, 2026?
manager = get_policy_manager()
policy_entry = manager.audit_trail.get_policy_at_time("2026-01-15T10:00:00Z")

print(f"Active policy hash: {policy_entry['policy_hash']}")
print(f"Environment: {policy_entry['metadata']['environment']}")
```

### Compliance Evidence

Generate a complete evidence bundle for auditors:

```python
generate_compliance_evidence("audit_package_2026_Q1.json")
```

Output includes:
- Current policy with hash
- Complete audit history
- Integrity verification results
- Policy change statistics

## Integration Patterns

### Web Application Middleware

```python
from flask import Flask, jsonify
from policy_manager import reload_policy, get_current_policy, verify_audit_trail

app = Flask(__name__)

@app.route('/admin/policy/reload', methods=['POST'])
def reload_policy_endpoint():
    """Reload policy via HTTP endpoint."""
    reason = request.json.get('reason', 'API reload')
    user = request.headers.get('X-User', 'anonymous')
    
    # Update reason to include user
    success = reload_policy(reason=f"{reason} (by {user})")
    
    return jsonify({
        'success': success,
        'policy': get_current_policy()
    })

@app.route('/admin/policy/verify', methods=['GET'])
def verify_policy_trail():
    """Verify audit trail integrity."""
    is_valid, errors = verify_audit_trail()
    
    return jsonify({
        'valid': is_valid,
        'errors': errors
    }), 200 if is_valid else 500
```

### Kubernetes ConfigMap Watcher

```python
import time
import hashlib
from kubernetes import client, config, watch

def watch_policy_configmap():
    """Watch Kubernetes ConfigMap for policy updates."""
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    
    w = watch.Watch()
    for event in w.stream(v1.list_namespaced_config_map, namespace='default'):
        if event['object'].metadata.name == 'privacy-policy':
            print(f"ConfigMap changed: {event['type']}")
            
            # Write updated policy to disk
            policy_data = event['object'].data.get('policy.json')
            with open('policies/privacy_policy_production.json', 'w') as f:
                f.write(policy_data)
            
            # Trigger reload
            reload_policy(reason=f"ConfigMap update: {event['type']}")
```

### Systemd Service Integration

```ini
[Unit]
Description=Starlink Security Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/starlink/starlink_security.py
ExecReload=/usr/bin/python3 /opt/starlink/policy_manager.py reload "Systemd reload"
Restart=on-failure

# Policy reload via systemd
# systemctl reload starlink-security

[Install]
WantedBy=multi-user.target
```

### Docker Signal Handling

```bash
# Reload policy in Docker container
docker kill --signal=SIGUSR2 starlink-security

# Or using docker-compose
docker-compose kill -s SIGUSR2 starlink-security
```

## Advanced Features

### Per-Service Policy Overrides

Support different policies for different components:

```python
class MultiServicePolicyManager:
    def __init__(self):
        self.policies = {
            'auth': PolicyManager("policies/privacy_policy_auth.json"),
            'api': PolicyManager("policies/privacy_policy_api.json"),
            'debug': PolicyManager("policies/privacy_policy_debug.json")
        }
    
    def get_policy_for_service(self, service: str) -> dict:
        """Get service-specific policy."""
        return self.policies.get(service, self.policies['api']).get_policy()
    
    def reload_all(self, reason: str = ""):
        """Reload all service policies."""
        for service, manager in self.policies.items():
            manager.reload_policy(reason=f"{reason} (service: {service})")
```

### Policy Coverage Metrics

Track which logs are validated against which policies:

```python
class PolicyCoverageTracker:
    def __init__(self):
        self.coverage_stats = {
            'validated': 0,
            'unclassified': 0,
            'by_policy': {}
        }
        self.lock = threading.Lock()
    
    def record_validation(self, policy_path: str, success: bool):
        """Record validation result."""
        with self.lock:
            if success:
                self.coverage_stats['validated'] += 1
                policy_key = Path(policy_path).stem
                self.coverage_stats['by_policy'][policy_key] = \
                    self.coverage_stats['by_policy'].get(policy_key, 0) + 1
            else:
                self.coverage_stats['unclassified'] += 1
    
    def get_coverage_report(self) -> dict:
        """Generate coverage report."""
        total = self.coverage_stats['validated'] + self.coverage_stats['unclassified']
        
        return {
            'total_logs': total,
            'validated': self.coverage_stats['validated'],
            'validated_percent': (self.coverage_stats['validated'] / total * 100) if total > 0 else 0,
            'unclassified': self.coverage_stats['unclassified'],
            'by_policy': self.coverage_stats['by_policy']
        }
```

### Emergency Policy Modes

Implement emergency enforcement modes for incidents:

```python
EMERGENCY_POLICY = {
    "version": "1.0.0-emergency",
    "environment": "production-lockdown",
    "enforcement_level": "strict",
    "pii_enforcement": {
        "suspect_fields": ["*"],  # All fields suspect
        "require_tags": ["REDACTED", "ENCRYPTED"],
        "reject_unredacted": True,
        "block_all_untagged": True
    },
    "reason": "Data breach response - maximum protection"
}

def activate_emergency_mode():
    """Activate emergency privacy mode."""
    import tempfile
    
    # Write emergency policy to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(EMERGENCY_POLICY, f)
        emergency_path = f.name
    
    # Load emergency policy
    manager = get_policy_manager()
    manager.load_policy(emergency_path, reason="EMERGENCY: Data breach response")
    
    print("EMERGENCY MODE ACTIVATED")
```

## Monitoring and Alerting

### Prometheus Metrics

```python
from prometheus_client import Counter, Gauge, Histogram

policy_reloads = Counter('policy_reloads_total', 'Total policy reloads')
policy_rollbacks = Counter('policy_rollbacks_total', 'Total policy rollbacks')
audit_trail_size = Gauge('audit_trail_entries', 'Number of audit trail entries')
reload_duration = Histogram('policy_reload_duration_seconds', 'Policy reload duration')

# In PolicyManager.reload_policy():
with reload_duration.time():
    success = self._do_reload()
    if success:
        policy_reloads.inc()
        audit_trail_size.set(len(self.audit_trail.get_audit_history()))
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Policy Management",
    "panels": [
      {
        "title": "Policy Reloads Over Time",
        "targets": [{
          "expr": "rate(policy_reloads_total[5m])"
        }]
      },
      {
        "title": "Audit Trail Size",
        "targets": [{
          "expr": "audit_trail_entries"
        }]
      },
      {
        "title": "Reload Duration (p95)",
        "targets": [{
          "expr": "histogram_quantile(0.95, policy_reload_duration_seconds)"
        }]
      }
    ]
  }
}
```

### Alert Rules

```yaml
groups:
  - name: policy_alerts
    rules:
      - alert: AuditTrailTampered
        expr: audit_trail_integrity_valid == 0
        for: 1m
        annotations:
          summary: "Policy audit trail integrity check failed"
          description: "The policy audit trail may have been tampered with"
        
      - alert: PolicyReloadFailed
        expr: rate(policy_reload_failures_total[5m]) > 0
        for: 5m
        annotations:
          summary: "Policy reload failures detected"
          description: "Multiple policy reload attempts have failed"
      
      - alert: ExcessivePolicyChanges
        expr: rate(policy_reloads_total[1h]) > 10
        for: 10m
        annotations:
          summary: "Unusual number of policy changes"
          description: "More than 10 policy changes in the last hour"
```

## Security Considerations

### Access Control

Implement RBAC for policy management operations:

```python
def reload_policy_with_rbac(user: str, reason: str) -> bool:
    """Reload policy with RBAC check."""
    # Check if user has permission
    if not has_permission(user, 'policy:reload'):
        audit_log(f"DENIED: {user} attempted policy reload")
        raise PermissionError(f"User {user} not authorized for policy reload")
    
    # Audit the authorized action
    audit_log(f"AUTHORIZED: {user} reloading policy: {reason}")
    
    # Include user in audit trail
    manager = get_policy_manager()
    manager.audit_trail.log_policy_change(
        action="reload",
        policy_path=str(manager.policy_path),
        policy_content=manager.current_policy,
        user=user,
        reason=reason
    )
    
    return manager.reload_policy(reason=f"{reason} (by {user})")
```

### Audit Trail Protection

Protect the audit trail file from modification:

```bash
# Set immutable flag (Linux)
sudo chattr +i policies/audit_trail.jsonl

# Or use append-only flag
sudo chattr +a policies/audit_trail.jsonl

# Set restrictive permissions
chmod 0400 policies/audit_trail.jsonl
chown root:root policies/audit_trail.jsonl
```

### Cryptographic Signing

For maximum security, sign audit entries with HSM:

```python
import hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

class SignedPolicyAuditTrail(PolicyAuditTrail):
    def __init__(self, private_key_path: str, **kwargs):
        super().__init__(**kwargs)
        with open(private_key_path, 'rb') as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(), password=None
            )
    
    def log_policy_change(self, *args, **kwargs) -> str:
        """Log policy change with digital signature."""
        entry_hash = super().log_policy_change(*args, **kwargs)
        
        # Sign the hash
        signature = self.private_key.sign(
            entry_hash.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Append signature to audit trail
        # (Implementation details omitted for brevity)
        
        return entry_hash
```

## Testing

### Unit Tests

```python
import unittest
import tempfile
import json
from policy_manager import PolicyManager, PolicyAuditTrail

class TestPolicyManager(unittest.TestCase):
    def setUp(self):
        # Create temporary policy file
        self.policy = {
            "version": "1.0.0",
            "environment": "test",
            "enforcement_level": "lenient"
        }
        
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        )
        json.dump(self.policy, self.temp_file)
        self.temp_file.close()
        
        self.manager = PolicyManager(self.temp_file.name)
    
    def test_initial_load(self):
        """Test initial policy load."""
        policy = self.manager.get_policy()
        self.assertEqual(policy['version'], "1.0.0")
    
    def test_reload(self):
        """Test policy reload."""
        # Modify policy file
        self.policy['version'] = "1.0.1"
        with open(self.temp_file.name, 'w') as f:
            json.dump(self.policy, f)
        
        # Reload
        success = self.manager.reload_policy(reason="Test reload")
        self.assertTrue(success)
        
        # Verify new version loaded
        policy = self.manager.get_policy()
        self.assertEqual(policy['version'], "1.0.1")
    
    def test_rollback(self):
        """Test policy rollback."""
        initial_policy = self.manager.get_policy()
        
        # Update policy
        self.policy['version'] = "2.0.0"
        with open(self.temp_file.name, 'w') as f:
            json.dump(self.policy, f)
        self.manager.reload_policy()
        
        # Rollback
        success = self.manager.rollback_policy(steps=1, reason="Test rollback")
        self.assertTrue(success)
        
        # Verify rollback
        current = self.manager.get_policy()
        self.assertEqual(current['version'], initial_policy['version'])
    
    def test_audit_integrity(self):
        """Test audit trail integrity."""
        # Make several changes
        for i in range(3):
            self.policy['version'] = f"1.0.{i}"
            with open(self.temp_file.name, 'w') as f:
                json.dump(self.policy, f)
            self.manager.reload_policy(reason=f"Test {i}")
        
        # Verify integrity
        is_valid, errors = self.manager.audit_trail.verify_integrity()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
```

### Integration Tests

```bash
#!/bin/bash
# test_policy_management.sh

# Start service in background
python starlink_security.py &
PID=$!

sleep 2

# Test reload via CLI
python policy_manager.py reload "Integration test reload"
if [ $? -ne 0 ]; then
    echo "FAIL: Reload command"
    exit 1
fi

# Test reload via signal
kill -SIGUSR2 $PID
sleep 1

# Verify audit trail
python policy_manager.py verify
if [ $? -ne 0 ]; then
    echo "FAIL: Audit trail verification"
    exit 1
fi

# Generate evidence
python policy_manager.py evidence test_evidence.json
if [ ! -f test_evidence.json ]; then
    echo "FAIL: Evidence generation"
    exit 1
fi

echo "PASS: All integration tests"
kill $PID
```

## Troubleshooting

### Common Issues

**Issue**: Policy reload has no effect
- **Cause**: File permissions or file not modified
- **Solution**: Check file modification time, verify permissions

**Issue**: Audit trail integrity check fails
- **Cause**: Manual file modification or corruption
- **Solution**: Review audit history, restore from backup

**Issue**: Signal handler not triggering
- **Cause**: Signal not supported on platform
- **Solution**: Use API-based reload instead

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

manager = get_policy_manager()
manager.reload_policy(reason="Debug test")
```

## Best Practices

1. **Always Provide Reasons**: Include meaningful reasons for all policy changes
2. **Verify After Reload**: Always verify audit trail after critical changes
3. **Regular Evidence Generation**: Generate compliance evidence monthly
4. **Monitor Reload Failures**: Alert on repeated reload failures
5. **Protect Audit Trail**: Use file system protections and signatures
6. **Test Rollback**: Regularly test rollback procedures
7. **Document Changes**: Maintain external documentation of policy changes
8. **Access Control**: Implement RBAC for policy operations
9. **Backup Policies**: Maintain versioned backups of all policies
10. **Audit the Auditors**: Log all access to audit trail

## Compliance Mapping

### GDPR Article 30 (Records of Processing)
- Audit trail provides required records of data processing activities
- Timestamp and hash prove when policies were active

### SOC 2 CC6.1 (Logical and Physical Access)
- Policy changes are logged and auditable
- Access controls can be enforced on policy operations

### HIPAA §164.308(a)(1)(ii)(D) (Information System Activity Review)
- Complete audit trail of privacy policy changes
- Tamper-evident logging ensures reliability

### ISO 27001 A.12.4.1 (Event Logging)
- Cryptographic hash chain provides non-repudiation
- Time-stamped entries support incident investigation

## Future Enhancements

1. **Distributed Policy Synchronization**: Sync policies across cluster
2. **AI-Powered Policy Optimization**: Suggest policy improvements based on violations
3. **Regulatory Change Tracking**: Auto-update policies when regulations change
4. **Policy Diff Visualization**: Show visual diff between policy versions
5. **Conflict Resolution**: Merge concurrent policy changes
6. **External Signing Service**: Integrate with HSM or external CA
7. **Blockchain Anchoring**: Anchor audit trail to public blockchain
8. **Zero-Knowledge Audits**: Prove compliance without revealing policy details

## References

- [NIST SP 800-92](https://csrc.nist.gov/publications/detail/sp/800-92/final): Guide to Computer Security Log Management
- [GDPR Article 30](https://gdpr-info.eu/art-30-gdpr/): Records of Processing Activities
- [SOC 2 Trust Services Criteria](https://www.aicpa.org/): Common Criteria
- [ISO 27001:2013](https://www.iso.org/standard/54534.html): Information Security Management

## Support

For questions or issues:
- Review audit trail with: `python policy_manager.py history`
- Verify integrity with: `python policy_manager.py verify`
- Generate evidence for review: `python policy_manager.py evidence`

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-16  
**Maintainer**: Starlink Security Team
