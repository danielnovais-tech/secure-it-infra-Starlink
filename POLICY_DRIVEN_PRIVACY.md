# Policy-Driven Privacy Enforcement Guide

## Overview

This guide explains how to use policy-driven privacy enforcement profiles to adaptively control privacy validation rules without code changes. The system supports environment-specific policies (production, staging, development) with configurable enforcement levels, pattern detection, and compliance frameworks.

## Table of Contents

1. [Policy File Format](#policy-file-format)
2. [Enforcement Profiles](#enforcement-profiles)
3. [Using Policy Files](#using-policy-files)
4. [Automated Regression Testing](#automated-regression-testing)
5. [External Auditor Mode](#external-auditor-mode)
6. [Integration with CI/CD](#integration-with-cicd)
7. [Compliance Frameworks](#compliance-frameworks)
8. [Best Practices](#best-practices)

## Policy File Format

Policy files are JSON documents that define privacy enforcement rules for different environments. They follow a standardized schema to ensure consistency and interoperability.

### Schema Structure

```json
{
  "$schema": "https://starlink-security.internal/schemas/privacy-policy-v1.0.0.json",
  "version": "1.0.0",
  "profile_name": "production|staging|development",
  "description": "Human-readable description of this policy",
  "created_at": "ISO8601 timestamp",
  "updated_at": "ISO8601 timestamp",
  "owner": "Team responsible for this policy",
  
  "enforcement_level": "strict|moderate|lenient",
  
  "pii_fields": {
    "suspect_fields": ["list", "of", "field", "names"],
    "required_tags": ["PII", "REDACTED"],
    "allow_untagged": false,
    "require_redaction": true
  },
  
  "phi_fields": {
    "suspect_fields": ["patient_id", "medical_record", ...],
    "required_tags": ["PHI", "REDACTED"],
    "allow_untagged": false,
    "require_redaction": true,
    "retention_days": 2555
  },
  
  "confidential_fields": {
    "suspect_fields": ["password", "secret", ...],
    "required_tags": ["CONFIDENTIAL", "REDACTED"],
    "allow_untagged": false,
    "require_redaction": true,
    "block_entirely": true
  },
  
  "pattern_detection": {
    "enabled": true,
    "patterns": {
      "email": {
        "regex": "pattern_here",
        "severity": "error|warning",
        "message": "Violation message"
      }
    }
  },
  
  "redaction_markers": {
    "accepted": ["***", "REDACTED", ...],
    "minimum_length": 3
  },
  
  "compliance": {
    "frameworks": ["GDPR", "HIPAA", ...],
    "data_minimization": true,
    "audit_all_access": true
  },
  
  "reporting": {
    "generate_audit_report": true,
    "report_format": "json|text|csv",
    "include_samples": false,
    "max_violations_per_report": 100
  }
}
```

## Enforcement Profiles

### Production Profile

**Location**: `policies/privacy_policy_production.json`

**Characteristics**:
- **Enforcement Level**: Strict
- **PII/PHI**: Must be tagged and redacted
- **Pattern Detection**: All patterns enabled with error severity
- **Compliance**: GDPR, HIPAA, PCI-DSS, SOC2, ISO27001
- **Audit Reports**: Enabled (JSON format, no samples)

**Use Cases**:
- Production environments
- Regulatory compliance audits
- Security-sensitive deployments
- Customer data processing

**Example Usage**:
```bash
python validate_logs.py \\
  --file prod_logs.jsonl \\
  --privacy-policy policies/privacy_policy_production.json \\
  --generate-audit-report
```

### Staging Profile

**Location**: `policies/privacy_policy_staging.json`

**Characteristics**:
- **Enforcement Level**: Moderate
- **PII/PHI**: Must be tagged and redacted
- **Pattern Detection**: Key patterns enabled
- **Compliance**: GDPR, SOC2
- **Audit Reports**: Enabled (JSON format, with samples)

**Use Cases**:
- Pre-production testing
- Integration testing
- Performance testing with production-like data
- Compliance validation before deployment

**Example Usage**:
```bash
python validate_logs.py \\
  --file staging_logs.jsonl \\
  --privacy-policy policies/privacy_policy_staging.json \\
  --lenient
```

### Development Profile

**Location**: `policies/privacy_policy_development.json`

**Characteristics**:
- **Enforcement Level**: Lenient
- **PII/PHI**: Warnings only, tagging optional
- **Pattern Detection**: Limited to critical patterns (passwords, secrets)
- **Compliance**: None
- **Audit Reports**: Disabled

**Use Cases**:
- Local development
- Unit testing
- Debugging
- Developer productivity

**Example Usage**:
```bash
python validate_logs.py \\
  --file dev_logs.jsonl \\
  --privacy-policy policies/privacy_policy_development.json
```

## Using Policy Files

### Command-Line Usage

```bash
# Use a specific policy file
python validate_logs.py \\
  --file logs/application.log \\
  --privacy-policy policies/privacy_policy_production.json

# Auto-detect policy based on environment variable
export STARLINK_ENVIRONMENT=production
python validate_logs.py --file logs/application.log --auto-detect-policy

# Generate audit report
python validate_logs.py \\
  --file logs/application.log \\
  --privacy-policy policies/privacy_policy_production.json \\
  --generate-audit-report \\
  --audit-report-output /tmp/audit_report.json
```

### Programmatic Usage

```python
from validate_logs import PolicyDrivenPrivacyEnforcer

# Load policy
enforcer = PolicyDrivenPrivacyEnforcer("policies/privacy_policy_production.json")

# Validate a log entry
log_entry = {...}
violations = enforcer.validate(log_entry)

if violations:
    print(f"Privacy violations detected: {len(violations)}")
    for violation in violations:
        print(f"  - {violation['message']}")

# Generate audit report
report = enforcer.generate_audit_report(format="json")
with open("audit_report.json", "w") as f:
    f.write(report)
```

## Automated Regression Testing

### Purpose

Automated regression tests deliberately inject PII/PHI patterns into sample logs to verify that privacy enforcement catches them. This ensures enforcement rules don't silently degrade over time.

### Test Suite Location

`tests/privacy_regression/test_privacy_enforcement.py`

### Running Tests

```bash
# Run all tests with production policy
python tests/privacy_regression/test_privacy_enforcement.py --policy production

# Run with staging policy
python tests/privacy_regression/test_privacy_enforcement.py --policy staging

# Verbose output
python tests/privacy_regression/test_privacy_enforcement.py --policy production --verbose

# JSON output
python tests/privacy_regression/test_privacy_enforcement.py --policy production --format json
```

### Test Coverage

The regression test suite covers:

1. **Unredacted Email**: Detects email addresses without proper tags
2. **Unredacted SSN**: Detects Social Security Numbers in messages
3. **Unredacted Credit Cards**: Detects credit card numbers in fields
4. **Unredacted Phone Numbers**: Detects phone numbers without redaction
5. **Properly Redacted PII**: Verifies that redacted PII passes validation
6. **Unredacted PHI**: Detects patient IDs and medical records
7. **API Keys in Messages**: Detects exposed API keys
8. **IP Addresses with Tags**: Verifies tagged IP addresses pass
9. **Multiple PII Fields**: Tests handling of multiple violations
10. **Blocked Confidential Fields**: Tests that passwords are blocked entirely

### Continuous Integration

```yaml
# .github/workflows/privacy-regression.yml
name: Privacy Enforcement Regression Tests

on: [push, pull_request]

jobs:
  privacy-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Run Privacy Regression Tests (Production)
        run: |
          python tests/privacy_regression/test_privacy_enforcement.py \\
            --policy production \\
            --format json > privacy_test_results.json
      
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: privacy-test-results
          path: privacy_test_results.json
```

## External Auditor Mode

External auditor mode generates machine-readable reports for compliance teams to review enforcement outcomes without accessing raw logs.

### Generating Audit Reports

```bash
# Generate JSON audit report
python validate_logs.py \\
  --file logs/production.log \\
  --privacy-policy policies/privacy_policy_production.json \\
  --generate-audit-report \\
  --audit-report-output audit_report.json \\
  --audit-report-format json

# Generate CSV audit report
python validate_logs.py \\
  --file logs/production.log \\
  --privacy-policy policies/privacy_policy_production.json \\
  --generate-audit-report \\
  --audit-report-output audit_report.csv \\
  --audit-report-format csv
```

### Audit Report Format (JSON)

```json
{
  "report_metadata": {
    "generated_at": "2026-01-16T20:00:00Z",
    "policy_name": "production",
    "policy_version": "1.0.0",
    "total_logs_scanned": 10000,
    "total_violations": 15,
    "compliance_frameworks": ["GDPR", "HIPAA", "PCI-DSS"]
  },
  "violations_summary": {
    "by_severity": {
      "error": 10,
      "warning": 5
    },
    "by_type": {
      "unredacted_pii": 8,
      "unredacted_phi": 3,
      "pattern_detection": 4
    }
  },
  "violations": [
    {
      "violation_id": "v001",
      "timestamp": "2026-01-16T19:30:00Z",
      "severity": "error",
      "type": "unredacted_pii",
      "field": "email",
      "message": "Email address detected without proper redaction",
      "log_identifier": "line_5042",
      "sample": null
    }
  ],
  "recommendations": [
    "Add privacy_tags=['PII', 'REDACTED'] to email fields",
    "Implement redaction filter for email addresses",
    "Review data minimization practices"
  ]
}
```

### Audit Report Format (CSV)

```csv
violation_id,timestamp,severity,type,field,message,log_identifier
v001,2026-01-16T19:30:00Z,error,unredacted_pii,email,Email detected,line_5042
v002,2026-01-16T19:31:00Z,error,pattern_detection,message,SSN detected,line_5043
```

## Integration with CI/CD

### Pre-Deployment Validation

```bash
#!/bin/bash
# scripts/validate_logs_before_deploy.sh

ENVIRONMENT=$1  # production, staging, development

echo "Validating logs with ${ENVIRONMENT} privacy policy..."

python validate_logs.py \\
  --file logs/application.log \\
  --privacy-policy policies/privacy_policy_${ENVIRONMENT}.json \\
  --strict \\
  --generate-audit-report \\
  --audit-report-output audit_${ENVIRONMENT}.json

if [ $? -ne 0 ]; then
  echo "Privacy violations detected! Deployment blocked."
  exit 1
fi

echo "Privacy validation passed!"
exit 0
```

### Policy Versioning

```bash
# Tag policy versions
git tag -a privacy-policy-v1.0.0 -m "Initial privacy policy release"
git push origin privacy-policy-v1.0.0

# Reference specific policy version in CI
python validate_logs.py \\
  --privacy-policy https://github.com/org/repo/raw/privacy-policy-v1.0.0/policies/privacy_policy_production.json
```

## Compliance Frameworks

### GDPR Compliance

**Requirements Mapped**:
- Data Minimization (Article 5)
- Purpose Limitation (Article 5)
- Accuracy (Article 5)
- Storage Limitation (Article 5)
- Integrity and Confidentiality (Article 5)

**Policy Configuration**:
```json
{
  "compliance": {
    "frameworks": ["GDPR"],
    "data_minimization": true,
    "consent_required": false,
    "audit_all_access": true
  },
  "pii_fields": {
    "require_redaction": true
  }
}
```

### HIPAA Compliance

**Requirements Mapped**:
- Protected Health Information (PHI) Safeguards (§164.502)
- Minimum Necessary Standard (§164.502(b))
- Access Controls (§164.308(a)(4))
- Audit Controls (§164.312(b))

**Policy Configuration**:
```json
{
  "compliance": {
    "frameworks": ["HIPAA"],
    "data_minimization": true,
    "audit_all_access": true
  },
  "phi_fields": {
    "require_redaction": true,
    "retention_days": 2555
  }
}
```

### PCI-DSS Compliance

**Requirements Mapped**:
- Requirement 3: Protect Stored Cardholder Data
- Requirement 4: Encrypt Transmission of Cardholder Data
- Requirement 10: Track and Monitor All Access to Network Resources

**Policy Configuration**:
```json
{
  "compliance": {
    "frameworks": ["PCI-DSS"],
    "audit_all_access": true
  },
  "pii_fields": {
    "suspect_fields": ["credit_card", "card_number", "cvv"],
    "require_redaction": true,
    "block_entirely": true
  }
}
```

## Best Practices

### 1. Policy File Management

- **Version Control**: Store policies in Git with semantic versioning
- **Code Review**: Require PR reviews for policy changes
- **Changelog**: Maintain CHANGELOG.md for policy modifications
- **Rollback Plan**: Keep previous policy versions for emergency rollback

### 2. Environment Separation

- **Never Use Dev Policies in Production**: Enforce via CI/CD checks
- **Test Policy Changes in Staging First**: Gradual rollout strategy
- **Document Differences**: Clearly document why policies differ across environments

### 3. Continuous Validation

- **Run Regression Tests**: On every policy change
- **Monitor Violation Rates**: Track trends over time
- **Alert on Spikes**: Automated alerting when violations increase
- **Regular Audits**: Quarterly manual reviews

### 4. Team Training

- **Onboarding**: Include privacy policy training in developer onboarding
- **Documentation**: Keep this guide up-to-date
- **Workshops**: Quarterly workshops on privacy enforcement
- **Feedback Loop**: Collect developer feedback on enforcement pain points

### 5. Policy Evolution

- **Grace Period**: 90-day minimum for deprecations
- **Communication**: Announce policy changes 30 days in advance
- **Migration Tools**: Provide automated migration scripts
- **Backward Compatibility**: Test legacy logs against new policies

## Troubleshooting

### Common Issues

**Issue**: Policy file not found
```bash
Error: Policy file 'policies/privacy_policy_production.json' not found
```

**Solution**:
```bash
# Verify file exists
ls -la policies/privacy_policy_production.json

# Use absolute path
python validate_logs.py --privacy-policy /absolute/path/to/policy.json
```

**Issue**: Too many false positives
```bash
Warning: 1000 violations detected
```

**Solution**:
- Review enforcement level (switch from strict to moderate)
- Add exceptions for known safe fields
- Update redaction markers list
- Use lenient mode during migration

**Issue**: Policy JSON syntax error
```bash
Error: JSON decode error in policy file
```

**Solution**:
```bash
# Validate JSON syntax
python -m json.tool policies/privacy_policy_production.json

# Use online JSON validator
# https://jsonlint.com
```

## Support and Feedback

- **Security Team**: security@starlink-security.internal
- **Platform Team**: platform@starlink-security.internal
- **Documentation**: https://docs.starlink-security.internal/privacy-enforcement

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2026-01-16 | Initial release with production, staging, development profiles | Security Team |
