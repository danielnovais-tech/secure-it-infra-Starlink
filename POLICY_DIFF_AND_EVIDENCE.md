# Policy Diff and Signed Evidence Bundle Guide

## Overview

This guide covers the advanced policy management features that make privacy enforcement transparent, auditable, and independently verifiable:

1. **Field-Level Policy Diffs**: Compare policies with granular change tracking
2. **Signed Evidence Bundles**: Cryptographically signed audit packages for compliance
3. **Granular Rollback**: Rollback by timestamp or policy ID
4. **Observability Metrics**: Track policy operations for monitoring
5. **External Verification**: Independent verification without system access

## Table of Contents

- [Policy Diff System](#policy-diff-system)
- [Signed Evidence Bundles](#signed-evidence-bundles)
- [Granular Rollback](#granular-rollback)
- [Observability Metrics](#observability-metrics)
- [External Verification API](#external-verification-api)
- [Integration Examples](#integration-examples)
- [Best Practices](#best-practices)

---

## Policy Diff System

### Overview

The Policy Diff system provides field-level comparison between policy versions, making it easy for auditors and developers to understand exactly what changed and why.

### Features

- **Field-Level Granularity**: Track changes to individual fields, not just entire files
- **Nested Object Support**: Handles deep object hierarchies and arrays
- **Human-Readable Output**: Clear textual format for manual review
- **Machine-Readable Output**: JSON format for automated processing
- **Change Classification**: Categorizes changes as added, removed, or modified

### Usage

#### Command-Line Interface

```bash
# Compare two policy versions
python policy_diff.py diff \
    --old policies/privacy_policy_production_v1.json \
    --new policies/privacy_policy_production_v2.json \
    --output diff_report.txt

# Machine-readable JSON output
python policy_diff.py diff \
    --old policies/privacy_policy_production_v1.json \
    --new policies/privacy_policy_production_v2.json \
    --format json \
    --output diff_report.json

# Compare current policy with specific version from history
python policy_manager.py diff --version 3 --format human
```

#### Programmatic API

```python
from policy_diff import PolicyDiffer

# Load policies
with open('old_policy.json') as f:
    old_policy = json.load(f)
    
with open('new_policy.json') as f:
    new_policy = json.load(f)

# Generate diff
differ = PolicyDiffer()
changes = differ.diff(old_policy, new_policy)

# Human-readable output
print(differ.format_human_readable(changes))

# Machine-readable output
diff_json = differ.format_machine_readable(changes)
print(json.dumps(diff_json, indent=2))
```

### Output Formats

#### Human-Readable Format

```
================================================================================
POLICY DIFF SUMMARY
================================================================================
Total changes: 5

ADDED FIELDS (2):
--------------------------------------------------------------------------------
  + phi_fields
      Value: ["patient_id", "medical_record"]

  + retention.phi
      Value: "7 years"

REMOVED FIELDS (1):
--------------------------------------------------------------------------------
  - debug_mode
      Was: true

MODIFIED FIELDS (2):
--------------------------------------------------------------------------------
  ~ enforcement_level
      Old: "strict"
      New: "moderate"

  ~ pii_fields
      Old: ["email", "user_id"]
      New: ["email", "user_id", "ip_address"]

================================================================================
```

#### Machine-Readable Format

```json
{
  "summary": {
    "total_changes": 5,
    "added": 2,
    "removed": 1,
    "modified": 2
  },
  "changes": [
    {
      "field_path": "phi_fields",
      "old_value": null,
      "new_value": ["patient_id", "medical_record"],
      "change_type": "added"
    },
    {
      "field_path": "enforcement_level",
      "old_value": "strict",
      "new_value": "moderate",
      "change_type": "modified"
    }
  ],
  "generated_at": "2026-01-16T22:20:00.000Z"
}
```

---

## Signed Evidence Bundles

### Overview

Signed Evidence Bundles provide cryptographically verifiable audit packages that combine policy history, audit trails, and diffs in a tamper-evident format.

### Features

- **PGP/GPG Signatures**: Industry-standard cryptographic signatures
- **Detached Signatures**: Separate signature files for independent verification
- **Bundle Integrity**: SHA-256 hashes of all components
- **Self-Contained**: Includes everything needed for audit
- **Timestamp Proofs**: Precise timestamps for all changes

### Setup

#### Configure GPG Key

```bash
# Generate GPG key (if needed)
gpg --full-generate-key

# List keys to get key ID
gpg --list-secret-keys --keyid-format=long

# Export public key for auditors
gpg --armor --export YOUR_KEY_ID > policy_signing_key.asc
```

#### Configure Policy Manager

```python
from policy_diff import SignedEvidenceGenerator

# Initialize with GPG key
generator = SignedEvidenceGenerator(gpg_key_id='YOUR_KEY_ID')
```

### Generating Signed Evidence

#### Command-Line

```bash
# Generate evidence bundle with signature
python policy_manager.py evidence \
    --sign \
    --key-id YOUR_KEY_ID \
    --output evidence_bundle.json \
    --signature evidence_bundle.sig

# Generate bundle with embedded diffs
python policy_manager.py evidence \
    --sign \
    --include-diffs \
    --from-version 1 \
    --to-version 5
```

#### Programmatic API

```python
from policy_diff import SignedEvidenceGenerator

# Initialize generator
generator = SignedEvidenceGenerator(gpg_key_id='YOUR_KEY_ID')

# Create evidence bundle
bundle = generator.generate_evidence_bundle(
    policy_history=policy_versions,
    audit_trail=audit_entries,
    diff_results=diff_data
)

# Sign the bundle
signed_bundle, detached_signature = generator.sign_bundle(bundle)

# Save bundle and signature
with open('evidence_bundle.json', 'w') as f:
    json.dump(signed_bundle, f, indent=2)
    
with open('evidence_bundle.sig', 'w') as f:
    f.write(detached_signature)
```

### Evidence Bundle Structure

```json
{
  "metadata": {
    "generated_at": "2026-01-16T22:20:00.000Z",
    "bundle_version": "1.0.0",
    "generator": "PolicyManager v1.0",
    "signed": true,
    "bundle_hash": "abc123..."
  },
  "policy_history": [
    {
      "version": 1,
      "timestamp": "2026-01-01T00:00:00Z",
      "policy": { /* policy content */ },
      "hash": "def456..."
    }
  ],
  "audit_trail": [
    {
      "timestamp": "2026-01-01T00:00:00Z",
      "action": "load",
      "hash": "ghi789...",
      "previous_hash": "000...",
      "reason": "Initial policy load"
    }
  ],
  "integrity": {
    "policy_count": 5,
    "audit_entry_count": 12,
    "policy_hashes": ["hash1", "hash2", ...],
    "audit_chain_valid": true
  },
  "diffs": {
    "v1_to_v2": { /* diff data */ },
    "v2_to_v3": { /* diff data */ }
  },
  "signature": {
    "algorithm": "PGP/GPG",
    "key_id": "YOUR_KEY_ID",
    "created_at": "2026-01-16T22:20:00.000Z"
  }
}
```

### Verifying Signed Evidence

#### Command-Line

```bash
# Verify bundle signature
gpg --verify evidence_bundle.sig evidence_bundle.json

# Verify programmatically
python policy_manager.py verify-evidence \
    --bundle evidence_bundle.json \
    --signature evidence_bundle.sig
```

#### Programmatic API

```python
from policy_diff import SignedEvidenceGenerator

generator = SignedEvidenceGenerator()

# Verify signature
is_valid = generator.verify_signature(
    bundle_path='evidence_bundle.json',
    signature_path='evidence_bundle.sig'
)

if is_valid:
    print("✓ Signature valid - bundle is authentic")
else:
    print("✗ Signature invalid - bundle may be tampered")
```

---

## Granular Rollback

### Rollback by Timestamp

Find and restore the exact policy active at a specific time:

```bash
# Rollback to policy active at specific timestamp
python policy_manager.py rollback --timestamp "2026-01-15T14:30:00Z"

# Find policy active at timestamp (dry-run)
python policy_manager.py find-policy --timestamp "2026-01-15T14:30:00Z"
```

```python
from policy_manager import PolicyManager

manager = PolicyManager()

# Find policy by timestamp
policy = manager.get_policy_at_time("2026-01-15T14:30:00Z")

# Rollback to that policy
manager.rollback_to_timestamp("2026-01-15T14:30:00Z", 
                              reason="Compliance investigation")
```

### Rollback by Policy ID

Rollback to a specific policy version by its hash:

```bash
# List all policy IDs
python policy_manager.py list --show-ids

# Rollback to specific policy ID
python policy_manager.py rollback --policy-id abc123def456
```

```python
# Rollback by policy hash
manager.rollback_to_policy_id(
    policy_id="abc123def456",
    reason="Restore known-good configuration"
)
```

### Rollback Safety Features

- **Audit Trail**: All rollbacks are logged with reason
- **Version Preservation**: Original policy remains in history
- **Integrity Checks**: Verifies policy integrity before rollback
- **Notification**: Emits alerts when rollback occurs

---

## Observability Metrics

### Metrics Tracked

The system tracks key policy operation metrics:

| Metric | Type | Description |
|--------|------|-------------|
| `policy_reload_count` | Counter | Number of policy reloads |
| `policy_rollback_count` | Counter | Number of rollbacks performed |
| `policy_verification_failures` | Counter | Failed integrity checks |
| `audit_chain_breaks` | Counter | Broken audit chain links |
| `evidence_bundles_generated` | Counter | Evidence bundles created |
| `diffs_generated` | Counter | Policy diffs generated |
| `last_reload_timestamp` | Timestamp | Last policy reload time |
| `last_rollback_timestamp` | Timestamp | Last rollback time |

### Exporting Metrics

#### Prometheus Format

```bash
# Export metrics for Prometheus scraping
python policy_manager.py metrics --format prometheus

# Metrics endpoint (if running as service)
curl http://localhost:9090/metrics
```

```python
from policy_diff import PolicyMetrics

metrics = PolicyMetrics()
prometheus_output = metrics.export_prometheus()
print(prometheus_output)
```

#### JSON Format

```bash
# Get metrics as JSON
python policy_manager.py metrics --format json
```

```python
metrics_data = metrics.get_metrics()
print(json.dumps(metrics_data, indent=2))
```

### Prometheus Integration

Example Prometheus configuration:

```yaml
scrape_configs:
  - job_name: 'policy_manager'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 30s
```

Example alert rules:

```yaml
groups:
  - name: policy_alerts
    rules:
      - alert: PolicyVerificationFailure
        expr: increase(policy_verification_failures[5m]) > 0
        annotations:
          summary: "Policy verification failed"
          
      - alert: AuditChainBroken
        expr: audit_chain_breaks > 0
        annotations:
          summary: "Audit trail integrity compromised"
          
      - alert: FrequentRollbacks
        expr: increase(policy_rollback_count[1h]) > 3
        annotations:
          summary: "Unusual rollback activity"
```

---

## External Verification API

### Read-Only API for Auditors

Provide external auditors with lightweight API access for verification without full system access:

```python
# verification_api.py - Read-only audit API

from flask import Flask, jsonify
from policy_manager import PolicyManager

app = Flask(__name__)
manager = PolicyManager()

@app.route('/api/v1/policy/history', methods=['GET'])
def get_policy_history():
    """Get complete policy history."""
    return jsonify(manager.get_policy_history())

@app.route('/api/v1/audit/trail', methods=['GET'])
def get_audit_trail():
    """Get complete audit trail."""
    return jsonify(manager.audit_trail.get_full_trail())

@app.route('/api/v1/audit/verify', methods=['GET'])
def verify_audit_integrity():
    """Verify audit trail integrity."""
    is_valid = manager.verify_audit_trail()
    return jsonify({
        'valid': is_valid,
        'checked_at': datetime.now(timezone.utc).isoformat()
    })

@app.route('/api/v1/policy/at/<timestamp>', methods=['GET'])
def get_policy_at_time(timestamp):
    """Get policy active at specific timestamp."""
    policy = manager.get_policy_at_time(timestamp)
    return jsonify(policy)

@app.route('/api/v1/evidence/generate', methods=['POST'])
def generate_evidence():
    """Generate evidence bundle on demand."""
    bundle = manager.generate_compliance_evidence()
    return jsonify(bundle)

if __name__ == '__main__':
    # Run on read-only port with TLS
    app.run(host='0.0.0.0', port=8443, ssl_context='adhoc')
```

### API Usage Examples

```bash
# Get policy history
curl https://policy-audit.example.com/api/v1/policy/history

# Verify audit trail
curl https://policy-audit.example.com/api/v1/audit/verify

# Get policy at specific time
curl https://policy-audit.example.com/api/v1/policy/at/2026-01-15T14:30:00Z

# Generate evidence bundle
curl -X POST https://policy-audit.example.com/api/v1/evidence/generate
```

---

## Integration Examples

### CI/CD Pipeline

```yaml
# .github/workflows/policy-diff.yml
name: Policy Change Review

on:
  pull_request:
    paths:
      - 'policies/**.json'

jobs:
  policy-diff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Generate policy diff
        run: |
          python policy_diff.py diff \
            --old policies/privacy_policy_production.json \
            --new policies/privacy_policy_production_new.json \
            --output diff_report.md
      
      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const diff = fs.readFileSync('diff_report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Policy Diff\n\n${diff}`
            });
```

### Automated Evidence Generation

```python
# scheduled_evidence_generator.py
import schedule
import time
from policy_diff import SignedEvidenceGenerator
from policy_manager import PolicyManager

def generate_monthly_evidence():
    """Generate signed evidence bundle monthly."""
    manager = PolicyManager()
    generator = SignedEvidenceGenerator(gpg_key_id='YOUR_KEY_ID')
    
    # Generate bundle
    bundle = generator.generate_evidence_bundle(
        policy_history=manager.get_policy_history(),
        audit_trail=manager.audit_trail.get_full_trail()
    )
    
    # Sign it
    signed_bundle, signature = generator.sign_bundle(bundle)
    
    # Save with timestamp
    timestamp = datetime.now().strftime('%Y%m')
    with open(f'evidence/bundle_{timestamp}.json', 'w') as f:
        json.dump(signed_bundle, f, indent=2)
    with open(f'evidence/bundle_{timestamp}.sig', 'w') as f:
        f.write(signature)
    
    print(f"Evidence bundle generated: bundle_{timestamp}.json")

# Schedule monthly on 1st at midnight
schedule.every().month.at("00:00").do(generate_monthly_evidence)

while True:
    schedule.run_pending()
    time.sleep(3600)
```

---

## Best Practices

### 1. Regular Diff Reviews

Review policy diffs before deployment:

```bash
# Pre-deployment review
python policy_diff.py diff \
    --old current_production_policy.json \
    --new proposed_policy.json \
    --format human > review.txt
    
# Have team review before applying
less review.txt
```

### 2. Signed Evidence Archival

Generate and archive signed evidence monthly:

```bash
# Monthly evidence generation
python policy_manager.py evidence \
    --sign \
    --output evidence/$(date +%Y%m)_bundle.json \
    --signature evidence/$(date +%Y%m)_bundle.sig
```

### 3. Metrics Monitoring

Set up alerts for suspicious activity:

```yaml
# Alert on verification failures
- alert: PolicyVerificationFailure
  expr: policy_verification_failures > 0
  for: 5m
  annotations:
    summary: "Policy integrity check failed"
```

### 4. External Verification

Enable auditors to verify independently:

```bash
# Share public key with auditors
gpg --armor --export YOUR_KEY_ID > public_key.asc

# Auditors can then verify
gpg --import public_key.asc
gpg --verify bundle.sig bundle.json
```

### 5. Granular Rollback Testing

Test rollback procedures regularly:

```bash
# Test rollback (dry-run)
python policy_manager.py rollback \
    --timestamp "2026-01-15T00:00:00Z" \
    --dry-run

# Document rollback playbook
```

### 6. Diff-Based Deployment

Use diffs to understand impact before deployment:

```python
# Pre-deployment impact analysis
differ = PolicyDiffer()
changes = differ.diff(current_policy, new_policy)

# Analyze impact
critical_changes = [
    c for c in changes 
    if c.field_path.startswith('enforcement_level') or 
       c.field_path.startswith('compliance_frameworks')
]

if critical_changes:
    print("⚠ Critical changes detected - requires approval")
    for change in critical_changes:
        print(f"  - {change.field_path}: {change.change_type}")
```

### 7. Evidence Bundle Retention

Maintain evidence bundles per compliance requirements:

```
evidence/
├── 202601_bundle.json      # January 2026
├── 202601_bundle.sig
├── 202602_bundle.json      # February 2026
├── 202602_bundle.sig
└── README.md               # Retention policy
```

Retention policy:
- **SOC 2**: 1 year minimum
- **HIPAA**: 6 years minimum
- **GDPR**: Varies by use case
- **PCI-DSS**: 3 months minimum (1 year for cardholder data)

---

## Compliance Mapping

### GDPR

- **Article 30 (Records of Processing)**: Signed evidence bundles document processing activities
- **Article 32 (Security)**: Cryptographic signatures prove integrity
- **Article 5(1)(f) (Integrity)**: Audit trail demonstrates data protection measures

### SOC 2

- **CC6.1 (Logical Access)**: Audit trail tracks policy changes
- **CC7.2 (System Monitoring)**: Metrics provide operational visibility
- **CC7.3 (Incident Response)**: Evidence bundles support investigations

### HIPAA

- **§164.308(a)(1)(ii)(D) (Information System Activity Review)**: Audit trail enables review
- **§164.312(c)(1) (Integrity)**: Signatures ensure policy integrity
- **§164.312(d) (Authentication)**: GPG signatures authenticate policy authors

### ISO 27001

- **A.12.4.1 (Event Logging)**: Comprehensive audit trail
- **A.12.4.2 (Protection of Log Information)**: Tamper-evident design
- **A.12.4.3 (Administrator Logs)**: Tracks privileged policy changes

---

## Troubleshooting

### GPG Signing Issues

```bash
# Check GPG installation
gpg --version

# List available keys
gpg --list-secret-keys

# Test signing
echo "test" | gpg --clearsign --local-user YOUR_KEY_ID
```

### Verification Failures

```bash
# Check audit chain integrity
python policy_manager.py verify --verbose

# Identify break in chain
python policy_manager.py audit-trail --check-integrity
```

### Diff Performance

For large policies:

```python
# Use shallow diff for initial review
differ = PolicyDiffer()
changes = differ.diff(old_policy, new_policy, max_depth=2)
```

---

## Summary

The Policy Diff and Signed Evidence system provides:

✅ **Transparency**: Field-level visibility into policy changes  
✅ **Integrity**: Cryptographic signatures prove authenticity  
✅ **Auditability**: Complete trail of who changed what and when  
✅ **Compliance**: Meets SOC2, HIPAA, GDPR, ISO 27001 requirements  
✅ **Observability**: Real-time metrics for operational monitoring  
✅ **Independence**: External auditors can verify without system access  

This closes the loop on governance, making the privacy enforcement system not just strong and adaptable, but provably so.
